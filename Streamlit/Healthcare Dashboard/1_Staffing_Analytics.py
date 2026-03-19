
"""
Staffing Analytics Page
METRIC 1: Monthly staffing ratios compared to state benchmarks
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import run_query, format_number

st.set_page_config(page_title="Staffing Analytics", page_icon="📈", layout="wide")

st.title("📈 Staffing Analytics")
st.markdown("### Monthly staffing ratios and state benchmark comparisons")
st.markdown("---")

with st.sidebar:
    st.markdown("## 🔍 Filters")

    states_df = run_query("""
        SELECT DISTINCT STATE
        FROM ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_RATIOS
        ORDER BY STATE
    """)
    states = ["All States"] + states_df["STATE"].dropna().tolist()
    selected_state = st.selectbox("Select State", states)

    benchmark_cats = st.multiselect(
        "Benchmark Category",
        [
            "At or Above Benchmark",
            "Slightly Below Benchmark",
            "Significantly Below Benchmark"
        ],
        default=[
            "At or Above Benchmark",
            "Slightly Below Benchmark",
            "Significantly Below Benchmark"
        ]
    )

    st.markdown("---")
    st.markdown("### 📅 Time Period")
    months_back = st.slider("Months of data", 1, 12, 6)

query = f"""
SELECT
    FACILITY_ID,
    FACILITY_NAME,
    STATE,
    OWNERSHIP_TYPE,
    MONTH,
    AVG_DAILY_CENSUS,
    AVG_OCCUPANCY_PCT,
    AVG_RN_HPRD,
    AVG_LPN_HPRD,
    AVG_CNA_HPRD,
    AVG_TOTAL_NURSING_HPRD,
    TOTAL_NURSING_HOURS,
    DAYS_REPORTED,
    STATE_BENCHMARK_HPRD,
    STATE_BENCHMARK_RN_HPRD,
    VARIANCE_FROM_STATE_AVG,
    BENCHMARK_CATEGORY
FROM ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_RATIOS
WHERE 1=1
"""

if selected_state != "All States":
    safe_state = selected_state.replace("'", "''")
    query += f" AND STATE = '{safe_state}'"

if benchmark_cats:
    cats_str = "', '".join(cat.replace("'", "''") for cat in benchmark_cats)
    query += f" AND BENCHMARK_CATEGORY IN ('{cats_str}')"

query += " ORDER BY MONTH DESC, FACILITY_NAME"

with st.spinner("Loading staffing data..."):
    df = run_query(query)

if df.empty:
    st.warning("No data available for selected filters")
    st.stop()

df["MONTH"] = pd.to_datetime(df["MONTH"])

st.markdown("## 📊 Summary Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_facilities = df["FACILITY_ID"].nunique()
    st.metric("Total Facilities", format_number(total_facilities))

with col2:
    avg_hprd = df.groupby("FACILITY_ID")["AVG_TOTAL_NURSING_HPRD"].mean().mean()
    st.metric("Avg Total Nursing HPRD", f"{avg_hprd:.2f}")

with col3:
    above_benchmark = (df["BENCHMARK_CATEGORY"] == "At or Above Benchmark").sum()
    pct_above = (above_benchmark / len(df) * 100) if len(df) > 0 else 0
    st.metric("At/Above Benchmark", f"{pct_above:.1f}%", delta="of facility-months")

with col4:
    avg_variance = df["VARIANCE_FROM_STATE_AVG"].mean()
    st.metric("Avg Variance from State", f"{avg_variance:+.2f}", delta="HPRD")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 📊 Staffing Trends Over Time")

    monthly_avg = df.groupby("MONTH", as_index=False).agg({
        "AVG_TOTAL_NURSING_HPRD": "mean",
        "AVG_RN_HPRD": "mean",
        "AVG_LPN_HPRD": "mean",
        "AVG_CNA_HPRD": "mean"
    })

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly_avg["MONTH"],
        y=monthly_avg["AVG_TOTAL_NURSING_HPRD"],
        name="Total Nursing",
        mode="lines+markers"
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly_avg["MONTH"],
        y=monthly_avg["AVG_RN_HPRD"],
        name="RN",
        mode="lines+markers"
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly_avg["MONTH"],
        y=monthly_avg["AVG_LPN_HPRD"],
        name="LPN",
        mode="lines+markers"
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly_avg["MONTH"],
        y=monthly_avg["AVG_CNA_HPRD"],
        name="CNA",
        mode="lines+markers"
    ))
    fig_trend.update_layout(
        xaxis_title="Month",
        yaxis_title="Hours Per Resident Day (HPRD)",
        height=400,
        hovermode="x unified"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    st.markdown("### 🎯 Benchmark Performance Distribution")

    benchmark_counts = df["BENCHMARK_CATEGORY"].value_counts().reset_index()
    benchmark_counts.columns = ["Category", "Count"]

    fig_benchmark = px.pie(
        benchmark_counts,
        values="Count",
        names="Category",
        hole=0.4
    )
    fig_benchmark.update_traces(textposition="inside", textinfo="percent+label")
    fig_benchmark.update_layout(height=400)
    st.plotly_chart(fig_benchmark, use_container_width=True)

st.markdown("---")

if selected_state == "All States":
    st.markdown("### 📍 State-Level Comparison")

    state_avg = df.groupby("STATE", as_index=False).agg({
        "AVG_TOTAL_NURSING_HPRD": "mean",
        "STATE_BENCHMARK_HPRD": "mean",
        "FACILITY_ID": "nunique"
    })

    state_avg = state_avg.sort_values("AVG_TOTAL_NURSING_HPRD", ascending=False).head(20)

    fig_states = go.Figure()
    fig_states.add_trace(go.Bar(
        x=state_avg["STATE"],
        y=state_avg["AVG_TOTAL_NURSING_HPRD"],
        name="Actual Avg"
    ))
    fig_states.add_trace(go.Scatter(
        x=state_avg["STATE"],
        y=state_avg["STATE_BENCHMARK_HPRD"],
        name="State Benchmark",
        mode="markers"
    ))
    fig_states.update_layout(
        xaxis_title="State",
        yaxis_title="Total Nursing HPRD",
        height=500,
        barmode="group"
    )
    fig_states.update_xaxes(tickangle=45)
    st.plotly_chart(fig_states, use_container_width=True)

st.markdown("---")

col_top, col_bottom = st.columns(2)

latest_month = df["MONTH"].max()

with col_top:
    st.markdown("### 🏆 Top 10 Performers (Highest HPRD)")
    top_10 = df[df["MONTH"] == latest_month].nlargest(10, "AVG_TOTAL_NURSING_HPRD")[
        ["FACILITY_NAME", "STATE", "AVG_TOTAL_NURSING_HPRD", "BENCHMARK_CATEGORY"]
    ].copy()
    top_10.columns = ["Facility", "State", "Nursing HPRD", "Category"]
    top_10["Nursing HPRD"] = top_10["Nursing HPRD"].map(lambda x: f"{x:.2f}")
    st.dataframe(top_10, hide_index=True, use_container_width=True)

with col_bottom:
    st.markdown("### ⚠️ Bottom 10 Performers (Lowest HPRD)")
    bottom_10 = df[df["MONTH"] == latest_month].nsmallest(10, "AVG_TOTAL_NURSING_HPRD")[
        ["FACILITY_NAME", "STATE", "AVG_TOTAL_NURSING_HPRD", "BENCHMARK_CATEGORY"]
    ].copy()
    bottom_10.columns = ["Facility", "State", "Nursing HPRD", "Category"]
    bottom_10["Nursing HPRD"] = bottom_10["Nursing HPRD"].map(lambda x: f"{x:.2f}")
    st.dataframe(bottom_10, hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown("### 💾 Export Data")

csv = df.to_csv(index=False)
st.download_button(
    label="Download Staffing Data as CSV",
    data=csv,
    file_name=f"staffing_analytics_{selected_state}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    use_container_width=True
)
