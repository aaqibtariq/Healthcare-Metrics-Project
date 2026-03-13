"""
Workforce Mix Page
METRIC 4: Employee vs contractor staffing mix and cost analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import run_query, format_number

st.set_page_config(page_title="Workforce Mix", page_icon="👥", layout="wide")

st.title("👥 Workforce Mix Analysis")
st.markdown("### Employee vs contractor staffing patterns and cost implications")
st.markdown("---")

# Sidebar filters
with st.sidebar:
    st.markdown("## 🔍 Filters")
    
    # Staffing model filter
    staffing_models = st.multiselect(
        "Staffing Model",
        ['Employee Only', 'Primarily Employee', 'Mixed Model', 'Contractor Dependent'],
        default=['Employee Only', 'Primarily Employee', 'Mixed Model', 'Contractor Dependent']
    )
    
    st.markdown("---")
    
    # State filter
    states_df = run_query("SELECT DISTINCT state FROM ANALYTICS.DBT_ATARIQ_CORE.MART_EMPLOYEE_VS_CONTRACTOR ORDER BY state")
    states = ['All States'] + states_df['STATE'].tolist()
    selected_state = st.selectbox("Select State", states)
    
    st.markdown("---")
    
    # Time period
    st.markdown("### 📅 Time Period")
    months_back = st.slider("Months of data", 1, 12, 6)

# Build query
query = f"""
SELECT 
    facility_id,
    facility_name,
    state,
    month,
    total_nursing_hours,
    total_employee_hours,
    total_contractor_hours,
    employee_pct,
    contractor_pct,
    staffing_model,
    estimated_cost_equivalent_hours
FROM ANALYTICS.DBT_ATARIQ_CORE.MART_EMPLOYEE_VS_CONTRACTOR
WHERE 1=1
"""

if staffing_models:
    models_str = "','".join(staffing_models)
    query += f" AND staffing_model IN ('{models_str}')"

if selected_state != 'All States':
    query += f" AND state = '{selected_state}'"

query += " ORDER BY month DESC, facility_name"

# Load data
with st.spinner("Loading workforce data..."):
    df = run_query(query)

if df.empty:
    st.warning("No data available for selected filters")
    st.stop()

# Convert month to datetime
df['MONTH'] = pd.to_datetime(df['MONTH'])

# Summary metrics
st.markdown("## 📊 Summary Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_facilities = df['FACILITY_ID'].nunique()
    st.metric("Total Facilities", format_number(total_facilities))

with col2:
    avg_employee_pct = df.groupby('FACILITY_ID')['EMPLOYEE_PCT'].mean().mean()
    st.metric("Avg Employee %", f"{avg_employee_pct:.1f}%")

with col3:
    avg_contractor_pct = df.groupby('FACILITY_ID')['CONTRACTOR_PCT'].mean().mean()
    st.metric("Avg Contractor %", f"{avg_contractor_pct:.1f}%")

with col4:
    total_hours = df['TOTAL_NURSING_HOURS'].sum()
    st.metric("Total Nursing Hours", format_number(total_hours))

st.markdown("---")

# Staffing model distribution
st.markdown("### 📊 Staffing Model Distribution")

col_pie, col_bar = st.columns(2)

with col_pie:
    # Pie chart - latest month
    latest_month = df['MONTH'].max()
    latest_data = df[df['MONTH'] == latest_month]
    
    model_counts = latest_data['STAFFING_MODEL'].value_counts().reset_index()
    model_counts.columns = ['Model', 'Count']
    
    fig_pie = px.pie(
        model_counts,
        values='Count',
        names='Model',
        color='Model',
        color_discrete_map={
            'Employee Only': '#10b981',
            'Primarily Employee': '#3b82f6',
            'Mixed Model': '#f59e0b',
            'Contractor Dependent': '#ef4444'
        },
        hole=0.4,
        title=f"Current Month Distribution ({latest_month.strftime('%B %Y')})"
    )
    
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=400)
    
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    # Bar chart - trend over time
    model_trend = df.groupby(['MONTH', 'STAFFING_MODEL']).size().reset_index(name='Count')
    
    fig_trend = px.bar(
        model_trend,
        x='MONTH',
        y='Count',
        color='STAFFING_MODEL',
        color_discrete_map={
            'Employee Only': '#10b981',
            'Primarily Employee': '#3b82f6',
            'Mixed Model': '#f59e0b',
            'Contractor Dependent': '#ef4444'
        },
        title="Staffing Model Trends Over Time",
        barmode='stack'
    )
    
    fig_trend.update_layout(
        height=400,
        xaxis_title="Month",
        yaxis_title="Number of Facilities",
        legend_title="Staffing Model"
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# Employee vs Contractor percentage trends
st.markdown("### 📈 Employee vs Contractor Trends")

monthly_avg = df.groupby('MONTH').agg({
    'EMPLOYEE_PCT': 'mean',
    'CONTRACTOR_PCT': 'mean',
    'TOTAL_NURSING_HOURS': 'sum'
}).reset_index()

fig_mix = go.Figure()

fig_mix.add_trace(go.Scatter(
    x=monthly_avg['MONTH'],
    y=monthly_avg['EMPLOYEE_PCT'],
    name='Employee %',
    mode='lines+markers',
    line=dict(color='#10b981', width=3),
    marker=dict(size=8),
    fill='tonexty'
))

fig_mix.add_trace(go.Scatter(
    x=monthly_avg['MONTH'],
    y=monthly_avg['CONTRACTOR_PCT'],
    name='Contractor %',
    mode='lines+markers',
    line=dict(color='#ef4444', width=3),
    marker=dict(size=8),
    fill='tozeroy'
))

fig_mix.update_layout(
    xaxis_title="Month",
    yaxis_title="Percentage of Total Hours",
    height=450,
    hovermode='x unified',
    yaxis=dict(range=[0, 100])
)

st.plotly_chart(fig_mix, use_container_width=True)

st.markdown("---")

# State comparison (if All States selected)
if selected_state == 'All States':
    st.markdown("### 📍 State-Level Comparison")
    
    state_avg = df.groupby('STATE').agg({
        'EMPLOYEE_PCT': 'mean',
        'CONTRACTOR_PCT': 'mean',
        'FACILITY_ID': 'nunique'
    }).reset_index()
    
    state_avg = state_avg.sort_values('CONTRACTOR_PCT', ascending=False).head(20)
    
    fig_states = go.Figure()
    
    fig_states.add_trace(go.Bar(
        x=state_avg['STATE'],
        y=state_avg['EMPLOYEE_PCT'],
        name='Employee %',
        marker_color='#10b981',
        text=state_avg['EMPLOYEE_PCT'].apply(lambda x: f"{x:.1f}%"),
        textposition='inside'
    ))
    
    fig_states.add_trace(go.Bar(
        x=state_avg['STATE'],
        y=state_avg['CONTRACTOR_PCT'],
        name='Contractor %',
        marker_color='#ef4444',
        text=state_avg['CONTRACTOR_PCT'].apply(lambda x: f"{x:.1f}%"),
        textposition='inside'
    ))
    
    fig_states.update_layout(
        xaxis_title="State",
        yaxis_title="Percentage",
        height=500,
        barmode='stack',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig_states.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig_states, use_container_width=True)

st.markdown("---")

# Detailed breakdown by staffing model
st.markdown("### 📊 Detailed Metrics by Staffing Model")

model_stats = df.groupby('STAFFING_MODEL').agg({
    'FACILITY_ID': 'nunique',
    'EMPLOYEE_PCT': 'mean',
    'CONTRACTOR_PCT': 'mean',
    'TOTAL_NURSING_HOURS': 'mean',
    'TOTAL_EMPLOYEE_HOURS': 'mean',
    'TOTAL_CONTRACTOR_HOURS': 'mean',
    'ESTIMATED_COST_EQUIVALENT_HOURS': 'mean'
}).reset_index()

model_stats.columns = ['Staffing Model', 'Facilities', 'Avg Employee %', 
                       'Avg Contractor %', 'Avg Total Hours', 'Avg Employee Hours',
                       'Avg Contractor Hours', 'Avg Cost Equivalent Hours']

# Format numbers
model_stats['Avg Employee %'] = model_stats['Avg Employee %'].apply(lambda x: f"{x:.1f}%")
model_stats['Avg Contractor %'] = model_stats['Avg Contractor %'].apply(lambda x: f"{x:.1f}%")
model_stats['Avg Total Hours'] = model_stats['Avg Total Hours'].apply(lambda x: format_number(x))
model_stats['Avg Employee Hours'] = model_stats['Avg Employee Hours'].apply(lambda x: format_number(x))
model_stats['Avg Contractor Hours'] = model_stats['Avg Contractor Hours'].apply(lambda x: format_number(x))
model_stats['Avg Cost Equivalent Hours'] = model_stats['Avg Cost Equivalent Hours'].apply(lambda x: format_number(x))

st.dataframe(model_stats, hide_index=True, use_container_width=True)

st.markdown("---")

# Top contractor-dependent facilities
col_top1, col_top2 = st.columns(2)

with col_top1:
    st.markdown("### 🔴 Most Contractor-Dependent")
    latest_month = df['MONTH'].max()
    top_contractor = df[df['MONTH'] == latest_month].nlargest(10, 'CONTRACTOR_PCT')[
        ['FACILITY_NAME', 'STATE', 'CONTRACTOR_PCT', 'STAFFING_MODEL']
    ]
    top_contractor.columns = ['Facility', 'State', 'Contractor %', 'Model']
    top_contractor['Contractor %'] = top_contractor['Contractor %'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(top_contractor, hide_index=True, use_container_width=True)

with col_top2:
    st.markdown("### 🟢 Most Employee-Focused")
    top_employee = df[df['MONTH'] == latest_month].nlargest(10, 'EMPLOYEE_PCT')[
        ['FACILITY_NAME', 'STATE', 'EMPLOYEE_PCT', 'STAFFING_MODEL']
    ]
    top_employee.columns = ['Facility', 'State', 'Employee %', 'Model']
    top_employee['Employee %'] = top_employee['Employee %'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(top_employee, hide_index=True, use_container_width=True)

# Cost implications
st.markdown("---")
st.markdown("### 💰 Cost Equivalent Analysis")

st.info("""
**Cost Equivalent Hours** represents the employee-equivalent hours accounting for typical contractor premium rates.
For example, 100 contractor hours might equal 150-180 employee-equivalent hours due to higher contractor costs.
""")

cost_by_model = df.groupby('STAFFING_MODEL').agg({
    'TOTAL_NURSING_HOURS': 'sum',
    'ESTIMATED_COST_EQUIVALENT_HOURS': 'sum'
}).reset_index()

cost_by_model['COST_PREMIUM'] = ((cost_by_model['ESTIMATED_COST_EQUIVALENT_HOURS'] / 
                                   cost_by_model['TOTAL_NURSING_HOURS'] - 1) * 100)

fig_cost = go.Figure()

fig_cost.add_trace(go.Bar(
    x=cost_by_model['STAFFING_MODEL'],
    y=cost_by_model['COST_PREMIUM'],
    marker_color=['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
    text=cost_by_model['COST_PREMIUM'].apply(lambda x: f"+{x:.1f}%"),
    textposition='auto',
))

fig_cost.update_layout(
    xaxis_title="Staffing Model",
    yaxis_title="Cost Premium (%)",
    height=400,
    showlegend=False
)

fig_cost.update_xaxes(tickangle=45)

st.plotly_chart(fig_cost, use_container_width=True)

# Download option
st.markdown("---")
st.markdown("### 💾 Export Data")
csv = df.to_csv(index=False)
st.download_button(
    label="Download Workforce Mix Data as CSV",
    data=csv,
    file_name=f"workforce_mix_{selected_state}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    use_container_width=True
)
