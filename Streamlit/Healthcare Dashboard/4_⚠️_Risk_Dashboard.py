"""
Risk Dashboard Page
METRIC 5: Multi-factor risk assessment for facility prioritization
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import run_query, format_number

st.set_page_config(page_title="Risk Dashboard", page_icon="⚠️", layout="wide")

st.title("⚠️ Risk Dashboard")
st.markdown("### Multi-factor risk assessment and facility prioritization")
st.markdown("---")

# Sidebar filters
with st.sidebar:
    st.markdown("## 🔍 Filters")
    
    # Risk category filter
    risk_categories = st.multiselect(
        "Risk Category",
        ['Critical Risk', 'High Risk', 'Medium Risk', 'Low Risk', 'Minimal Risk'],
        default=['Critical Risk', 'High Risk', 'Medium Risk']
    )
    
    # Intervention priority
    priorities = st.multiselect(
        "Intervention Priority",
        [1, 2, 3, 4],
        default=[1, 2],
        format_func=lambda x: f"Priority {x} {'(Highest)' if x == 1 else ''}"
    )
    
    st.markdown("---")
    
    # State filter
    states_df = run_query("SELECT DISTINCT state FROM ANALYTICS.DBT_ATARIQ_CORE.MART_HIGH_RISK_FACILITIES ORDER BY state")
    states = ['All States'] + states_df['STATE'].tolist()
    selected_state = st.selectbox("Select State", states)
    
    st.markdown("---")
    
    # Risk factors
    st.markdown("### 🎯 Risk Factors")
    show_low_staffing = st.checkbox("Low Staffing", value=True)
    show_high_turnover = st.checkbox("High Turnover", value=True)
    show_low_rating = st.checkbox("Low Rating", value=True)
    show_high_penalties = st.checkbox("High Penalties", value=True)
    show_high_readmissions = st.checkbox("High Readmissions", value=True)
    show_abuse_deficiencies = st.checkbox("Abuse Deficiencies", value=True)

# Build query
query = """
SELECT 
    facility_id,
    facility_name,
    state,
    total_risk_score,
    risk_category,
    intervention_priority,
    overall_rating,
    reported_total_nursing_hprd,
    total_penalties,
    health_deficiencies,
    risk_low_staffing,
    risk_high_turnover,
    risk_low_rating,
    risk_high_penalties,
    risk_high_readmissions,
    risk_abuse_deficiencies
FROM ANALYTICS.DBT_ATARIQ_CORE.MART_HIGH_RISK_FACILITIES
WHERE 1=1
"""

if risk_categories:
    cats_str = "','".join(risk_categories)
    query += f" AND risk_category IN ('{cats_str}')"

if priorities:
    priorities_str = ','.join(map(str, priorities))
    query += f" AND intervention_priority IN ({priorities_str})"

if selected_state != 'All States':
    query += f" AND state = '{selected_state}'"

# Risk factor filters
risk_filters = []
if show_low_staffing:
    risk_filters.append("risk_low_staffing = 1")
if show_high_turnover:
    risk_filters.append("risk_high_turnover = 1")
if show_low_rating:
    risk_filters.append("risk_low_rating = 1")
if show_high_penalties:
    risk_filters.append("risk_high_penalties = 1")
if show_high_readmissions:
    risk_filters.append("risk_high_readmissions = 1")
if show_abuse_deficiencies:
    risk_filters.append("risk_abuse_deficiencies = 1")

if risk_filters:
    query += " AND (" + " OR ".join(risk_filters) + ")"

query += " ORDER BY total_risk_score DESC, intervention_priority ASC"

# Load data
with st.spinner("Loading risk data..."):
    df = run_query(query)

if df.empty:
    st.warning("No facilities match the selected criteria")
    st.stop()

# Summary metrics
st.markdown("## 📊 Risk Summary")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_facilities = len(df)
    st.metric("Facilities at Risk", format_number(total_facilities))

with col2:
    critical_count = (df['RISK_CATEGORY'] == 'Critical Risk').sum()
    st.metric("Critical Risk", format_number(critical_count), 
              delta=f"{(critical_count/total_facilities*100):.1f}%" if total_facilities > 0 else None,
              delta_color="inverse")

with col3:
    avg_risk_score = df['TOTAL_RISK_SCORE'].mean()
    st.metric("Avg Risk Score", f"{avg_risk_score:.2f}", delta="out of 6")

with col4:
    priority_1 = (df['INTERVENTION_PRIORITY'] == 1).sum()
    st.metric("Priority 1 Facilities", format_number(priority_1))

st.markdown("---")

# Risk distribution
col_risk1, col_risk2 = st.columns(2)

with col_risk1:
    st.markdown("### ⚠️ Risk Category Distribution")
    
    risk_counts = df['RISK_CATEGORY'].value_counts().reset_index()
    risk_counts.columns = ['Category', 'Count']
    
    # Order by severity
    order_map = {
        'Critical Risk': 1,
        'High Risk': 2,
        'Medium Risk': 3,
        'Low Risk': 4,
        'Minimal Risk': 5
    }
    risk_counts['Order'] = risk_counts['Category'].map(order_map)
    risk_counts = risk_counts.sort_values('Order')
    
    fig_risk = px.pie(
        risk_counts,
        values='Count',
        names='Category',
        color='Category',
        color_discrete_map={
            'Critical Risk': '#ef4444',
            'High Risk': '#f59e0b',
            'Medium Risk': '#eab308',
            'Low Risk': '#84cc16',
            'Minimal Risk': '#10b981'
        },
        hole=0.4
    )
    
    fig_risk.update_traces(textposition='inside', textinfo='percent+label')
    fig_risk.update_layout(height=400)
    
    st.plotly_chart(fig_risk, use_container_width=True)

with col_risk2:
    st.markdown("### 🎯 Intervention Priority")
    
    priority_counts = df['INTERVENTION_PRIORITY'].value_counts().sort_index().reset_index()
    priority_counts.columns = ['Priority', 'Count']
    
    fig_priority = go.Figure()
    
    fig_priority.add_trace(go.Bar(
        x=priority_counts['Priority'],
        y=priority_counts['Count'],
        marker_color=['#ef4444', '#f59e0b', '#eab308', '#84cc16'],
        text=priority_counts['Count'],
        textposition='auto',
    ))
    
    fig_priority.update_layout(
        xaxis_title="Intervention Priority (1=Highest)",
        yaxis_title="Number of Facilities",
        height=400,
        showlegend=False,
        xaxis=dict(tickmode='linear', tick0=1, dtick=1)
    )
    
    st.plotly_chart(fig_priority, use_container_width=True)

st.markdown("---")

# Risk factors breakdown
st.markdown("### 🔍 Risk Factors Analysis")

risk_factors_data = {
    'Risk Factor': [
        'Low Staffing',
        'High Turnover',
        'Low Rating',
        'High Penalties',
        'High Readmissions',
        'Abuse Deficiencies'
    ],
    'Count': [
        df['RISK_LOW_STAFFING'].sum(),
        df['RISK_HIGH_TURNOVER'].sum(),
        df['RISK_LOW_RATING'].sum(),
        df['RISK_HIGH_PENALTIES'].sum(),
        df['RISK_HIGH_READMISSIONS'].sum(),
        df['RISK_ABUSE_DEFICIENCIES'].sum()
    ]
}

risk_factors_df = pd.DataFrame(risk_factors_data)
risk_factors_df = risk_factors_df.sort_values('Count', ascending=True)

fig_factors = go.Figure()

fig_factors.add_trace(go.Bar(
    x=risk_factors_df['Count'],
    y=risk_factors_df['Risk Factor'],
    orientation='h',
    marker_color='#ef4444',
    text=risk_factors_df['Count'],
    textposition='auto',
))

fig_factors.update_layout(
    xaxis_title="Number of Facilities with Risk Factor",
    yaxis_title="",
    height=400,
    showlegend=False
)

st.plotly_chart(fig_factors, use_container_width=True)

st.markdown("---")

# Risk score distribution
st.markdown("### 📊 Risk Score Distribution")

score_dist = df['TOTAL_RISK_SCORE'].value_counts().sort_index().reset_index()
score_dist.columns = ['Risk Score', 'Count']

fig_score = go.Figure()

fig_score.add_trace(go.Bar(
    x=score_dist['Risk Score'],
    y=score_dist['Count'],
    marker_color='#ef4444',
    text=score_dist['Count'],
    textposition='auto',
))

fig_score.update_layout(
    xaxis_title="Total Risk Score (0-6)",
    yaxis_title="Number of Facilities",
    height=400,
    showlegend=False,
    xaxis=dict(tickmode='linear', tick0=0, dtick=1)
)

st.plotly_chart(fig_score, use_container_width=True)

st.markdown("---")

# High-risk facilities table
st.markdown("### 🚨 High-Risk Facilities (Top 20)")

top_risk = df.nlargest(20, 'TOTAL_RISK_SCORE')[[
    'FACILITY_NAME', 'STATE', 'TOTAL_RISK_SCORE', 'RISK_CATEGORY', 
    'INTERVENTION_PRIORITY', 'OVERALL_RATING', 'TOTAL_PENALTIES'
]]

top_risk.columns = ['Facility', 'State', 'Risk Score', 'Risk Category', 
                    'Priority', 'Star Rating', 'Total Penalties']

# Color code by risk
def color_risk(val):
    if 'Critical' in str(val):
        return 'background-color: #fee2e2'
    elif 'High' in str(val):
        return 'background-color: #fed7aa'
    return ''

styled_table = top_risk.style.applymap(color_risk, subset=['Risk Category'])

st.dataframe(top_risk, hide_index=True, use_container_width=True)

st.markdown("---")

# State comparison (if All States)
if selected_state == 'All States':
    st.markdown("### 📍 Risk by State")
    
    state_risk = df.groupby('STATE').agg({
        'FACILITY_ID': 'count',
        'TOTAL_RISK_SCORE': 'mean',
        'RISK_CATEGORY': lambda x: (x == 'Critical Risk').sum()
    }).reset_index()
    
    state_risk.columns = ['State', 'Facilities', 'Avg Risk Score', 'Critical Risk Count']
    state_risk = state_risk.sort_values('Avg Risk Score', ascending=False).head(20)
    
    fig_states = go.Figure()
    
    fig_states.add_trace(go.Bar(
        x=state_risk['State'],
        y=state_risk['Avg Risk Score'],
        marker_color='#ef4444',
        text=state_risk['Avg Risk Score'].apply(lambda x: f"{x:.2f}"),
        textposition='outside',
        name='Avg Risk Score'
    ))
    
    fig_states.update_layout(
        xaxis_title="State",
        yaxis_title="Average Risk Score",
        height=500,
        showlegend=False
    )
    
    fig_states.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig_states, use_container_width=True)

# Detailed risk breakdown
st.markdown("---")
st.markdown("### 📋 Detailed Risk Metrics by Category")

risk_stats = df.groupby('RISK_CATEGORY').agg({
    'FACILITY_ID': 'count',
    'TOTAL_RISK_SCORE': 'mean',
    'OVERALL_RATING': 'mean',
    'REPORTED_TOTAL_NURSING_HPRD': 'mean',
    'TOTAL_PENALTIES': 'mean',
    'HEALTH_DEFICIENCIES': 'mean',
    'RISK_LOW_STAFFING': 'sum',
    'RISK_ABUSE_DEFICIENCIES': 'sum'
}).reset_index()

risk_stats.columns = ['Risk Category', 'Facility Count', 'Avg Risk Score', 
                      'Avg Star Rating', 'Avg Nursing HPRD', 'Avg Penalties',
                      'Avg Health Deficiencies', 'Low Staffing Count', 'Abuse Deficiencies Count']

# Format numbers
risk_stats['Avg Risk Score'] = risk_stats['Avg Risk Score'].apply(lambda x: f"{x:.2f}")
risk_stats['Avg Star Rating'] = risk_stats['Avg Star Rating'].apply(lambda x: f"{x:.2f}")
risk_stats['Avg Nursing HPRD'] = risk_stats['Avg Nursing HPRD'].apply(lambda x: f"{x:.2f}")
risk_stats['Avg Penalties'] = risk_stats['Avg Penalties'].apply(lambda x: f"{x:.1f}")
risk_stats['Avg Health Deficiencies'] = risk_stats['Avg Health Deficiencies'].apply(lambda x: f"{x:.1f}")

st.dataframe(risk_stats, hide_index=True, use_container_width=True)

# Download option
st.markdown("---")
st.markdown("### 💾 Export Data")

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download All Risk Data as CSV",
        data=csv,
        file_name=f"risk_dashboard_{selected_state}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_dl2:
    critical_csv = df[df['RISK_CATEGORY'].isin(['Critical Risk', 'High Risk'])].to_csv(index=False)
    st.download_button(
        label="Download Critical/High Risk Only",
        data=critical_csv,
        file_name=f"critical_risk_facilities_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
