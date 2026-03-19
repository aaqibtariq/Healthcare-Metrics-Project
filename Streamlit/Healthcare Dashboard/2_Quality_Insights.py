"""
Quality Insights Page
METRIC 3: Relationship between staffing levels and quality outcomes
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import run_query, format_number

st.set_page_config(page_title="Quality Insights", page_icon="", layout="wide")

st.title(" Quality Insights")
st.markdown("### Understanding the relationship between staffing and quality outcomes")
st.markdown("---")

# Sidebar filters
with st.sidebar:
    st.markdown("##  Filters")
    
    # Quality tier filter
    quality_tiers = st.multiselect(
        "Quality Tier",
        ['High Quality', 'Medium Quality', 'Low Quality', 'Very Low Quality'],
        default=['High Quality', 'Medium Quality', 'Low Quality', 'Very Low Quality']
    )
    
    # Staffing quality category
    staffing_quality_cats = st.multiselect(
        "Staffing-Quality Category",
        ['High Staffing, High Quality', 'High Staffing, Low Quality', 
         'Low Staffing, High Quality', 'Low Staffing, Low Quality'],
        default=['High Staffing, High Quality', 'High Staffing, Low Quality', 
                 'Low Staffing, High Quality', 'Low Staffing, Low Quality']
    )
    
    st.markdown("---")
    
    # State filter
    states_df = run_query("SELECT DISTINCT state FROM ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_VS_QUALITY ORDER BY state")
    states = ['All States'] + states_df['STATE'].tolist()
    selected_state = st.selectbox("Select State", states)

# Build query
query = """
SELECT 
    facility_id,
    facility_name,
    state,
    overall_rating,
    reported_total_nursing_hprd,
    composite_quality_score,
    quality_tier,
    staffing_quality_category,
    readmission_rate_short_stay,
    health_deficiencies,
    total_penalties
FROM ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_VS_QUALITY
WHERE 1=1
"""

if quality_tiers:
    tiers_str = "','".join(quality_tiers)
    query += f" AND quality_tier IN ('{tiers_str}')"

if staffing_quality_cats:
    cats_str = "','".join(staffing_quality_cats)
    query += f" AND staffing_quality_category IN ('{cats_str}')"

if selected_state != 'All States':
    query += f" AND state = '{selected_state}'"

# Load data
with st.spinner("Loading quality data..."):
    df = run_query(query)

if df.empty:
    st.warning("No data available for selected filters")
    st.stop()

df['OVERALL_RATING'] = df['OVERALL_RATING'].fillna(1)

# Summary metrics
st.markdown("## 📊 Summary Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_facilities = len(df)
    st.metric("Total Facilities", format_number(total_facilities))

with col2:
    avg_quality_score = df['COMPOSITE_QUALITY_SCORE'].mean()
    st.metric("Avg Quality Score", f"{avg_quality_score:.1f}", delta="out of 100")

with col3:
    high_quality_pct = (df['QUALITY_TIER'] == 'High Quality').sum() / len(df) * 100
    st.metric("High Quality %", f"{high_quality_pct:.1f}%")

with col4:
    avg_rating = df['OVERALL_RATING'].mean()
    st.metric("Avg Star Rating", f"{avg_rating:.2f}", delta="out of 5")

st.markdown("---")

# Main scatter plot - Staffing vs Quality
st.markdown("### 📈 Staffing vs Quality Correlation")

fig_scatter = px.scatter(
    df,
    x='REPORTED_TOTAL_NURSING_HPRD',
    y='COMPOSITE_QUALITY_SCORE',
    color='QUALITY_TIER',
    size='OVERALL_RATING',
    hover_data=['FACILITY_NAME', 'STATE', 'OVERALL_RATING'],
    color_discrete_map={
        'High Quality': '#10b981',
        'Medium Quality': '#84cc16',
        'Low Quality': '#f59e0b',
        'Very Low Quality': '#ef4444'
    },
    labels={
        'REPORTED_TOTAL_NURSING_HPRD': 'Total Nursing HPRD',
        'COMPOSITE_QUALITY_SCORE': 'Composite Quality Score'
    },
    title="Each dot represents a facility"
)

# Add trendline
fig_scatter.update_traces(marker=dict(opacity=0.6, line=dict(width=0.5, color='white')))
fig_scatter.update_layout(
    height=500,
    hovermode='closest',
    showlegend=True
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# Two column layout
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("###  Staffing-Quality Matrix")
    
    matrix_counts = df['STAFFING_QUALITY_CATEGORY'].value_counts().reset_index()
    matrix_counts.columns = ['Category', 'Count']
    
    # Create custom colors
    color_map = {
        'High Staffing, High Quality': '#10b981',
        'High Staffing, Low Quality': '#f59e0b',
        'Low Staffing, High Quality': '#3b82f6',
        'Low Staffing, Low Quality': '#ef4444'
    }
    
    fig_matrix = go.Figure()
    
    for cat in matrix_counts['Category']:
        count = matrix_counts[matrix_counts['Category'] == cat]['Count'].values[0]
        fig_matrix.add_trace(go.Bar(
            name=cat,
            x=[cat],
            y=[count],
            marker_color=color_map.get(cat, '#6b7280'),
            text=[count],
            textposition='auto',
            showlegend=False
        ))
    
    fig_matrix.update_layout(
        xaxis_title="",
        yaxis_title="Number of Facilities",
        height=400,
        margin=dict(b=100)
    )
    
    fig_matrix.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig_matrix, use_container_width=True)

with col_right:
    st.markdown("###  Star Rating Distribution")
    
    rating_dist = df['OVERALL_RATING'].value_counts().sort_index().reset_index()
    rating_dist.columns = ['Rating', 'Count']
    
    fig_rating = go.Figure()
    
    fig_rating.add_trace(go.Bar(
        x=rating_dist['Rating'],
        y=rating_dist['Count'],
        marker_color=['#ef4444', '#f59e0b', '#eab308', '#84cc16', '#10b981'],
        text=rating_dist['Count'],
        textposition='auto',
    ))
    
    fig_rating.update_layout(
        xaxis_title="Star Rating",
        yaxis_title="Number of Facilities",
        height=400,
        showlegend=False,
        xaxis=dict(tickmode='linear', tick0=1, dtick=1)
    )
    
    st.plotly_chart(fig_rating, use_container_width=True)

st.markdown("---")

# Full width - Quality tier breakdown
st.markdown("###  Quality Metrics by Tier")

tier_stats = df.groupby('QUALITY_TIER').agg({
    'COMPOSITE_QUALITY_SCORE': 'mean',
    'OVERALL_RATING': 'mean',
    'REPORTED_TOTAL_NURSING_HPRD': 'mean',
    'READMISSION_RATE_SHORT_STAY': 'mean',
    'HEALTH_DEFICIENCIES': 'mean',
    'TOTAL_PENALTIES': 'mean',
    'FACILITY_ID': 'count'
}).reset_index()

tier_stats.columns = ['Quality Tier', 'Avg Quality Score', 'Avg Star Rating', 
                      'Avg Nursing HPRD', 'Avg Readmission Rate', 
                      'Avg Deficiencies', 'Avg Penalties', 'Facility Count']

# Format numbers
tier_stats['Avg Quality Score'] = tier_stats['Avg Quality Score'].apply(lambda x: f"{x:.1f}")
tier_stats['Avg Star Rating'] = tier_stats['Avg Star Rating'].apply(lambda x: f"{x:.2f}")
tier_stats['Avg Nursing HPRD'] = tier_stats['Avg Nursing HPRD'].apply(lambda x: f"{x:.2f}")
tier_stats['Avg Readmission Rate'] = tier_stats['Avg Readmission Rate'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
tier_stats['Avg Deficiencies'] = tier_stats['Avg Deficiencies'].apply(lambda x: f"{x:.1f}")
tier_stats['Avg Penalties'] = tier_stats['Avg Penalties'].apply(lambda x: f"{x:.1f}")

st.dataframe(tier_stats, hide_index=True, use_container_width=True)

st.markdown("---")

# Readmission rates analysis
col_read1, col_read2 = st.columns(2)

with col_read1:
    st.markdown("###  Readmission Rates by Quality Tier")
    
    readmit_data = df.groupby('QUALITY_TIER')['READMISSION_RATE_SHORT_STAY'].mean().reset_index()
    
    fig_readmit = go.Figure()
    
    fig_readmit.add_trace(go.Bar(
        x=readmit_data['QUALITY_TIER'],
        y=readmit_data['READMISSION_RATE_SHORT_STAY'],
        marker_color=['#10b981', '#84cc16', '#f59e0b', '#ef4444'],
        text=readmit_data['READMISSION_RATE_SHORT_STAY'].apply(lambda x: f"{x:.1f}%"),
        textposition='auto',
    ))
    
    fig_readmit.update_layout(
        xaxis_title="Quality Tier",
        yaxis_title="Avg Readmission Rate (%)",
        height=400,
        showlegend=False
    )
    
    fig_readmit.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig_readmit, use_container_width=True)

with col_read2:
    st.markdown("###  Deficiencies by Quality Tier")
    
    defic_data = df.groupby('QUALITY_TIER')['HEALTH_DEFICIENCIES'].mean().reset_index()
    
    fig_defic = go.Figure()
    
    fig_defic.add_trace(go.Bar(
        x=defic_data['QUALITY_TIER'],
        y=defic_data['HEALTH_DEFICIENCIES'],
        marker_color=['#10b981', '#84cc16', '#f59e0b', '#ef4444'],
        text=defic_data['HEALTH_DEFICIENCIES'].apply(lambda x: f"{x:.1f}"),
        textposition='auto',
    ))
    
    fig_defic.update_layout(
        xaxis_title="Quality Tier",
        yaxis_title="Avg Total Deficiencies",
        height=400,
        showlegend=False
    )
    
    fig_defic.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig_defic, use_container_width=True)

# Download option
st.markdown("---")
st.markdown("###  Export Data")
csv = df.to_csv(index=False)
st.download_button(
    label="Download Quality Data as CSV",
    data=csv,
    file_name=f"quality_insights_{selected_state}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    use_container_width=True
)
