"""
Healthcare Analytics Dashboard - Home Page
Overview of key metrics across all 14,814 skilled nursing facilities
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import run_query, format_number

# Page configuration
st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    .big-number {
        font-size: 2.5em;
        font-weight: bold;
        color: #2563eb;
    }
    .metric-label {
        font-size: 0.9em;
        color: #6c757d;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🏥 Healthcare Analytics Dashboard")
st.markdown("### Comprehensive insights from 14,814 skilled nursing facilities")
st.markdown("---")

# Sidebar info
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/2563eb/ffffff?text=Healthcare+Analytics", use_container_width=True)
    st.markdown("## 📊 Dashboard Navigation")
    st.markdown("""
    Use the sidebar to navigate between different analytics views:
    
    - **📈 Staffing Analytics** - Staffing ratios and benchmarks
    - **⭐ Quality Insights** - Quality vs staffing correlation
    - **👥 Workforce Mix** - Employee vs contractor analysis
    - **⚠️ Risk Dashboard** - High-risk facility identification
    - **🔍 Facility Lookup** - Search specific facilities
    """)
    
    st.markdown("---")
    st.markdown("### 🔄 Data Refresh")
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.success("Data refreshed!")

# Load summary data
@st.cache_data(ttl=600)
def load_summary_stats():
    """Load high-level summary statistics"""
    
    # Total facilities
    total_facilities = run_query("""
        SELECT COUNT(DISTINCT facility_id) as total
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_HIGH_RISK_FACILITIES
    """)
    
    # Risk distribution
    risk_dist = run_query("""
        SELECT 
            risk_category,
            COUNT(*) as count
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_HIGH_RISK_FACILITIES
        GROUP BY risk_category
        ORDER BY 
            CASE risk_category
                WHEN 'Critical Risk' THEN 1
                WHEN 'High Risk' THEN 2
                WHEN 'Medium Risk' THEN 3
                WHEN 'Low Risk' THEN 4
                WHEN 'Minimal Risk' THEN 5
            END
    """)
    
    # Average staffing by state
    state_staffing = run_query("""
        SELECT 
            state,
            AVG(avg_total_nursing_hprd) as avg_hprd,
            COUNT(DISTINCT facility_id) as facilities
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_RATIOS
        WHERE month >= (Select DATEADD(month, -3, Max(Month))
            From ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_RATIOS)
        GROUP BY state
        ORDER BY avg_hprd DESC
    """)
    
    # Quality distribution
    quality_dist = run_query("""
        SELECT 
            quality_tier,
            COUNT(*) as count,
            AVG(composite_quality_score) as avg_score
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_VS_QUALITY
        GROUP BY quality_tier
        ORDER BY avg_score DESC
    """)
    
    # Staffing model mix
    staffing_mix = run_query("""
        SELECT 
            staffing_model,
            COUNT(DISTINCT facility_id) as facilities,
            AVG(contractor_pct) as avg_contractor_pct
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_EMPLOYEE_VS_CONTRACTOR
        WHERE month >=(Select DATEADD(month, -1, Max(Month))
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_EMPLOYEE_VS_CONTRACTOR)
        GROUP BY staffing_model
        ORDER BY facilities DESC
    """)
    
    return {
        'total': total_facilities,
        'risk': risk_dist,
        'states': state_staffing,
        'quality': quality_dist,
        'staffing_mix': staffing_mix
    }

# Load data with spinner
with st.spinner("Loading dashboard data..."):
    data = load_summary_stats()

# Key Metrics Row
st.markdown("## 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total = data['total']['TOTAL'].iloc[0] if not data['total'].empty else 0
    st.metric(
        label="Total Facilities",
        value=format_number(total),
        delta=None
    )

with col2:
    critical = data['risk'][data['risk']['RISK_CATEGORY'] == 'Critical Risk']['COUNT'].iloc[0] if 'Critical Risk' in data['risk']['RISK_CATEGORY'].values else 0
    st.metric(
        label="Critical Risk Facilities",
        value=format_number(critical),
        delta=f"{(critical/total*100):.1f}% of total" if total > 0 else None,
        delta_color="inverse"
    )

with col3:
    high_quality = data['quality'][data['quality']['QUALITY_TIER'] == 'High Quality']['COUNT'].iloc[0] if 'High Quality' in data['quality']['QUALITY_TIER'].values else 0
    st.metric(
        label="High Quality Facilities",
        value=format_number(high_quality),
        delta=f"{(high_quality/total*100):.1f}% of total" if total > 0 else None,
        delta_color="normal"
    )

with col4:
    avg_hprd = data['states']['AVG_HPRD'].mean() if not data['states'].empty else 0
    st.metric(
        label="Avg Nursing HPRD",
        value=f"{avg_hprd:.2f}",
        delta="hours per resident per day"
    )

st.markdown("---")

# Two column layout
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### ⚠️ Risk Category Distribution")
    if not data['risk'].empty:
        fig_risk = px.pie(
            data['risk'],
            values='COUNT',
            names='RISK_CATEGORY',
            color='RISK_CATEGORY',
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
        fig_risk.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("No risk data available")

with col_right:
    st.markdown("### ⭐ Quality Distribution")
    if not data['quality'].empty:
        fig_quality = go.Figure()
        fig_quality.add_trace(go.Bar(
            x=data['quality']['QUALITY_TIER'],
            y=data['quality']['COUNT'],
            marker_color=['#10b981', '#84cc16', '#f59e0b', '#ef4444'],
            text=data['quality']['COUNT'],
            textposition='auto',
        ))
        fig_quality.update_layout(
            xaxis_title="Quality Tier",
            yaxis_title="Number of Facilities",
            height=400,
            showlegend=False,
            margin=dict(t=20, b=40, l=40, r=20)
        )
        st.plotly_chart(fig_quality, use_container_width=True)
    else:
        st.info("No quality data available")

st.markdown("---")

# Bottom row - full width charts
col_full1, col_full2 = st.columns(2)

with col_full1:
    st.markdown("### 📍 Top 10 States by Avg Staffing")
    if not data['states'].empty:
        top_states = data['states'].head(10)
        fig_states = go.Figure()
        fig_states.add_trace(go.Bar(
            x=top_states['AVG_HPRD'],
            y=top_states['STATE'],
            orientation='h',
            marker_color='#2563eb',
            text=top_states['AVG_HPRD'].apply(lambda x: f"{x:.2f}"),
            textposition='auto',
        ))
        fig_states.update_layout(
            xaxis_title="Average Nursing HPRD",
            yaxis_title="State",
            height=400,
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(t=20, b=40, l=60, r=20)
        )
        st.plotly_chart(fig_states, use_container_width=True)
    else:
        st.info("No state data available")

with col_full2:
    st.markdown("### 👥 Staffing Model Distribution")
    if not data['staffing_mix'].empty:
        fig_mix = go.Figure()
        fig_mix.add_trace(go.Bar(
            x=data['staffing_mix']['STAFFING_MODEL'],
            y=data['staffing_mix']['FACILITIES'],
            marker_color=['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
            text=data['staffing_mix']['FACILITIES'],
            textposition='auto',
        ))
        fig_mix.update_layout(
            xaxis_title="Staffing Model",
            yaxis_title="Number of Facilities",
            height=400,
            showlegend=False,
            margin=dict(t=20, b=80, l=40, r=20)
        )
        fig_mix.update_xaxes(tickangle=45)
        st.plotly_chart(fig_mix, use_container_width=True)
    else:
        st.info("No staffing mix data available")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d; padding: 20px;'>
    <p>Data refreshes every 10 minutes | Last updated: Real-time from Snowflake</p>
    <p>Built with Streamlit | Powered by dbt + Snowflake</p>
</div>
""", unsafe_allow_html=True)
