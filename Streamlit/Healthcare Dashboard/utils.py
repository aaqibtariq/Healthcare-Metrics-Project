"""
Utility functions for Snowflake connection and data loading
"""
import streamlit as st
import snowflake.connector
import pandas as pd
from typing import Optional

@st.cache_resource
def get_snowflake_connection():
    """
    Create and cache Snowflake connection
    """
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"]
    )

@st.cache_data(ttl=600)
def run_query(query: str) -> pd.DataFrame:
    """
    Execute a query and return results as a DataFrame
    Cached for 10 minutes
    """
    conn = get_snowflake_connection()
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_mart_data(mart_name: str, filters: Optional[dict] = None) -> pd.DataFrame:
    """
    Load data from a specific mart table with optional filters
    
    Args:
        mart_name: Name of the mart table (e.g., 'mart_staffing_ratios')
        filters: Dictionary of column: value filters
    
    Returns:
        DataFrame with mart data
    """
    query = f"SELECT * FROM {mart_name}"
    
    if filters:
        conditions = []
        for col, val in filters.items():
            if isinstance(val, str):
                conditions.append(f"{col} = '{val}'")
            elif isinstance(val, list):
                vals = "','".join(val)
                conditions.append(f"{col} IN ('{vals}')")
            else:
                conditions.append(f"{col} = {val}")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
    
    return run_query(query)

def format_number(num, decimals=0, prefix="", suffix=""):
    """Format number with commas and optional prefix/suffix"""
    if pd.isna(num):
        return "N/A"
    if decimals == 0:
        return f"{prefix}{num:,.0f}{suffix}"
    return f"{prefix}{num:,.{decimals}f}{suffix}"

def get_color_scale(value, min_val, max_val, reverse=False):
    """
    Get color based on value position in range
    reverse=True for metrics where lower is better
    """
    if pd.isna(value):
        return "#cccccc"
    
    normalized = (value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
    
    if reverse:
        normalized = 1 - normalized
    
    if normalized >= 0.7:
        return "#10b981"  # green
    elif normalized >= 0.4:
        return "#f59e0b"  # amber
    else:
        return "#ef4444"  # red
