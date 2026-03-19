"""
Facility Lookup Page
Search and view detailed metrics for specific facilities
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import run_query, format_number

st.set_page_config(page_title="Facility Lookup", page_icon="", layout="wide")

st.title(" Facility Lookup")
st.markdown("### Search and analyze individual facilities")
st.markdown("---")

# Facility search
st.markdown("##  Search for a Facility")

col_search1, col_search2 = st.columns([2, 1])

with col_search1:
    # Get all facilities
    facilities_df = run_query("""
        SELECT DISTINCT facility_id, facility_name, state
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_HIGH_RISK_FACILITIES
        ORDER BY facility_name
    """)
    
    if facilities_df.empty:
        st.error("No facilities found in database")
        st.stop()
    
    # Create searchable dropdown
    facility_options = [
        f"{row['FACILITY_NAME']} ({row['STATE']}) - ID: {row['FACILITY_ID']}"
        for _, row in facilities_df.iterrows()
    ]
    
    selected_facility_str = st.selectbox(
        "Select Facility",
        options=facility_options,
        help="Start typing to search for a facility"
    )
    
    # Extract facility ID
    selected_facility_id = selected_facility_str.split("ID: ")[-1]

with col_search2:
    st.markdown("### Quick Stats")
    total_facilities = len(facilities_df)
    st.metric("Total Facilities", format_number(total_facilities))

if not selected_facility_id:
    st.info(" Select a facility to view detailed metrics")
    st.stop()

st.markdown("---")

# Load facility data from all marts
with st.spinner("Loading facility data..."):
    # Basic info from risk dashboard
    facility_info = run_query(f"""
        SELECT *
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_HIGH_RISK_FACILITIES
        WHERE facility_id = '{selected_facility_id}'
    """)
    
    # Staffing ratios (recent months)
    staffing_data = run_query(f"""
        SELECT *
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_RATIOS
        WHERE facility_id = '{selected_facility_id}'
        ORDER BY month DESC
        LIMIT 12
    """)
    
    # Quality metrics
    quality_data = run_query(f"""
        SELECT *
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_VS_QUALITY
        WHERE facility_id = '{selected_facility_id}'
    """)
    
    # Workforce mix (recent months)
    workforce_data = run_query(f"""
        SELECT *
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_EMPLOYEE_VS_CONTRACTOR
        WHERE facility_id = '{selected_facility_id}'
        ORDER BY month DESC
        LIMIT 12
    """)
    
    # Occupancy correlation
    occupancy_data = run_query(f"""
        SELECT *
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_VS_OCCUPANCY
        WHERE facility_id = '{selected_facility_id}'
    """)

# Display facility header
if not facility_info.empty:
    st.markdown(f"##  {facility_info['FACILITY_NAME'].iloc[0]}")
    st.markdown(f"**State:** {facility_info['STATE'].iloc[0]} | **Facility ID:** {facility_info['FACILITY_ID'].iloc[0]}")
    
    st.markdown("---")
    
    # Key metrics row
    st.markdown("###  Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        rating = facility_info['OVERALL_RATING'].iloc[0]
        st.metric("Star Rating", f"{rating}/5", delta=None)
    
    with col2:
        risk_cat = facility_info['RISK_CATEGORY'].iloc[0]
        risk_score = facility_info['TOTAL_RISK_SCORE'].iloc[0]
        st.metric("Risk Category", risk_cat, delta=f"Score: {risk_score}/6")
    
    with col3:
        if not quality_data.empty:
            quality_score = quality_data['COMPOSITE_QUALITY_SCORE'].iloc[0]
            st.metric("Quality Score", f"{quality_score:.1f}/100")
        else:
            st.metric("Quality Score", "N/A")
    
    with col4:
        hprd = facility_info['REPORTED_TOTAL_NURSING_HPRD'].iloc[0]
        st.metric("Nursing HPRD", f"{hprd:.2f}")
    
    with col5:
        penalties = facility_info['TOTAL_PENALTIES'].iloc[0]
        st.metric("Total Penalties", format_number(penalties))
    
    st.markdown("---")
    
    # Two column layout for charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("###  Staffing Trends (Last 12 Months)")
        
        if not staffing_data.empty:
            staffing_data['MONTH'] = pd.to_datetime(staffing_data['MONTH'])
            
            fig_staffing = go.Figure()
            
            fig_staffing.add_trace(go.Scatter(
                x=staffing_data['MONTH'],
                y=staffing_data['AVG_TOTAL_NURSING_HPRD'],
                name='Total Nursing HPRD',
                mode='lines+markers',
                line=dict(color='#2563eb', width=3),
                marker=dict(size=8)
            ))
            
            fig_staffing.add_trace(go.Scatter(
                x=staffing_data['MONTH'],
                y=staffing_data['STATE_BENCHMARK_HPRD'],
                name='State Benchmark',
                mode='lines',
                line=dict(color='#ef4444', width=2, dash='dash')
            ))
            
            fig_staffing.update_layout(
                xaxis_title="Month",
                yaxis_title="Hours Per Resident Day",
                height=350,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_staffing, use_container_width=True)
        else:
            st.info("No staffing trend data available")
    
    with col_right:
        st.markdown("###  Workforce Mix (Last 12 Months)")
        
        if not workforce_data.empty:
            workforce_data['MONTH'] = pd.to_datetime(workforce_data['MONTH'])
            
            fig_workforce = go.Figure()
            
            fig_workforce.add_trace(go.Bar(
                x=workforce_data['MONTH'],
                y=workforce_data['EMPLOYEE_PCT'],
                name='Employee %',
                marker_color='#10b981'
            ))
            
            fig_workforce.add_trace(go.Bar(
                x=workforce_data['MONTH'],
                y=workforce_data['CONTRACTOR_PCT'],
                name='Contractor %',
                marker_color='#ef4444'
            ))
            
            fig_workforce.update_layout(
                xaxis_title="Month",
                yaxis_title="Percentage",
                height=350,
                barmode='stack',
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_workforce, use_container_width=True)
        else:
            st.info("No workforce mix data available")
    
    st.markdown("---")
    
    # Risk factors breakdown
    st.markdown("###  Risk Factors Analysis")
    
    risk_factors = {
        'Low Staffing': facility_info['RISK_LOW_STAFFING'].iloc[0],
        'High Turnover': facility_info['RISK_HIGH_TURNOVER'].iloc[0],
        'Low Rating': facility_info['RISK_LOW_RATING'].iloc[0],
        'High Penalties': facility_info['RISK_HIGH_PENALTIES'].iloc[0],
        'High Readmissions': facility_info['RISK_HIGH_READMISSIONS'].iloc[0],
        'Abuse Deficiencies': facility_info['RISK_ABUSE_DEFICIENCIES'].iloc[0]
    }
    
    col_rf1, col_rf2, col_rf3, col_rf4, col_rf5, col_rf6 = st.columns(6)
    
    cols = [col_rf1, col_rf2, col_rf3, col_rf4, col_rf5, col_rf6]
    for idx, (factor, value) in enumerate(risk_factors.items()):
        with cols[idx]:
            if value == 1:
                st.error(f" {factor}")
            else:
                st.success(f" {factor}")
    
    st.markdown("---")
    
    # Quality metrics detail
    if not quality_data.empty:
        st.markdown("###  Quality Metrics Detail")
        
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        
        with col_q1:
            quality_tier = quality_data['QUALITY_TIER'].iloc[0]
            st.metric("Quality Tier", quality_tier)
        
        with col_q2:
            readmit = quality_data['READMISSION_RATE_SHORT_STAY'].iloc[0]
            st.metric("Readmission Rate", f"{readmit:.1f}%" if pd.notna(readmit) else "N/A")
        
        with col_q3:
            deficiencies = quality_data['HEALTH_DEFICIENCIES'].iloc[0]
            st.metric("HEALTH_DEFICIENCIES", format_number(deficiencies))
        
        with col_q4:
            staffing_quality = quality_data['STAFFING_QUALITY_CATEGORY'].iloc[0]
            st.metric("Staffing-Quality Category", staffing_quality if pd.notna(staffing_quality) else "N/A")
        
        st.markdown("---")
    
    # Occupancy correlation
    if not occupancy_data.empty:
        st.markdown("###  Staffing Flexibility Analysis")
        
        col_o1, col_o2, col_o3, col_o4 = st.columns(4)
        
        with col_o1:
            avg_occ = occupancy_data['AVG_OCCUPANCY_PCT'].iloc[0]
            st.metric("Avg Occupancy", f"{avg_occ:.1f}%")
        
        with col_o2:
            correlation = occupancy_data['STAFFING_OCCUPANCY_CORRELATION'].iloc[0]
            st.metric("Staffing-Occupancy Correlation", f"{correlation:.3f}" if pd.notna(correlation) else "N/A")
        
        with col_o3:
            flexibility = occupancy_data['STAFFING_FLEXIBILITY'].iloc[0]
            st.metric("Staffing Flexibility", flexibility if pd.notna(flexibility) else "N/A")
        
        with col_o4:
            utilization = occupancy_data['OCCUPANCY_UTILIZATION_CATEGORY'].iloc[0]
            st.metric("Utilization Category", utilization if pd.notna(utilization) else "N/A")
        
        st.markdown("---")
    
    # Detailed data tables
    st.markdown("###  Detailed Monthly Data")
    
    tab1, tab2 = st.tabs([" Staffing History", " Workforce History"])
    
    with tab1:
        if not staffing_data.empty:
            staffing_display = staffing_data[[
                'MONTH', 'AVG_TOTAL_NURSING_HPRD', 'AVG_RN_HPRD', 
                'AVG_LPN_HPRD', 'AVG_CNA_HPRD', 'STATE_BENCHMARK_HPRD',
                'VARIANCE_FROM_STATE_AVG', 'BENCHMARK_CATEGORY'
            ]].copy()
            
            staffing_display['MONTH'] = pd.to_datetime(staffing_display['MONTH']).dt.strftime('%Y-%m')
            staffing_display.columns = [
                'Month', 'Total Nursing HPRD', 'RN HPRD', 'LPN HPRD', 'CNA HPRD',
                'State Benchmark', 'Variance', 'Category'
            ]
            
            # Format numbers
            for col in ['Total Nursing HPRD', 'RN HPRD', 'LPN HPRD', 'CNA HPRD', 'State Benchmark', 'Variance']:
                staffing_display[col] = staffing_display[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
            
            st.dataframe(staffing_display, hide_index=True, use_container_width=True)
            
            # Download option
            csv = staffing_data.to_csv(index=False)
            st.download_button(
                label="Download Staffing History",
                data=csv,
                file_name=f"staffing_history_{selected_facility_id}.csv",
                mime="text/csv"
            )
        else:
            st.info("No staffing history available")
    
    with tab2:
        if not workforce_data.empty:
            workforce_display = workforce_data[[
                'MONTH', 'TOTAL_NURSING_HOURS', 'TOTAL_EMPLOYEE_HOURS', 'TOTAL_CONTRACTOR_HOURS',
                'EMPLOYEE_PCT', 'CONTRACTOR_PCT', 'STAFFING_MODEL'
            ]].copy()
            
            workforce_display['MONTH'] = pd.to_datetime(workforce_display['MONTH']).dt.strftime('%Y-%m')
            workforce_display.columns = [
                'Month', 'Total Hours', 'Employee Hours', 'Contractor Hours',
                'Employee %', 'Contractor %', 'Staffing Model'
            ]
            
            # Format numbers
            workforce_display['Total Hours'] = workforce_display['Total Hours'].apply(lambda x: format_number(x))
            workforce_display['Employee Hours'] = workforce_display['Employee Hours'].apply(lambda x: format_number(x))
            workforce_display['Contractor Hours'] = workforce_display['Contractor Hours'].apply(lambda x: format_number(x))
            workforce_display['Employee %'] = workforce_display['Employee %'].apply(lambda x: f"{x:.1f}%")
            workforce_display['Contractor %'] = workforce_display['Contractor %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(workforce_display, hide_index=True, use_container_width=True)
            
            # Download option
            csv = workforce_data.to_csv(index=False)
            st.download_button(
                label="Download Workforce History",
                data=csv,
                file_name=f"workforce_history_{selected_facility_id}.csv",
                mime="text/csv"
            )
        else:
            st.info("No workforce history available")

else:
    st.error("Facility not found in database")
