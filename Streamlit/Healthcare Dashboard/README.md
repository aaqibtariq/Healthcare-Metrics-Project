# Healthcare Analytics Dashboard

Interactive Streamlit dashboard visualizing metrics from 14,814 skilled nursing facilities.

## 📊 Dashboard Features

### Pages:
1. **🏠 Home** - Executive overview with key metrics and distributions
2. **📈 Staffing Analytics** - Monthly staffing ratios vs state benchmarks (Metric 1)
3. **⭐ Quality Insights** - Staffing vs quality correlation analysis (Metric 3)
4. **👥 Workforce Mix** - Employee vs contractor analysis (Metric 4)
5. **⚠️ Risk Dashboard** - Multi-factor risk assessment (Metric 5)
6. **🔍 Facility Lookup** - Search and analyze individual facilities

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Snowflake account with access to ANALYTICS database
- dbt models deployed (from Phase 8)

### Installation

1. **Clone or download this dashboard folder**

2. **Install dependencies**
```bash
cd healthcare_dashboard
pip install -r requirements.txt
```

3. **Configure Snowflake credentials**

Create `.streamlit/secrets.toml` file:
```bash
mkdir -p .streamlit
cp secrets_template.toml .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` with your credentials:
```toml
[snowflake]
user = "HEALTHCARE_PIPELINE_USER"
password = "your_password_here"
account = "your_account_identifier"  # Format: abc12345.us-east-1
warehouse = "TRANSFORM_WH"
database = "ANALYTICS"
schema = "DBT_ATARIQ_CORE"
role = "HEALTHCARE_PIPELINE_ROLE"
```

4. **Run the dashboard**
```bash
streamlit run streamlit_app.py
```

5. **Access the dashboard**
Open your browser to http://localhost:8501

## 📁 Project Structure

```
healthcare_dashboard/
├── streamlit_app.py          # Home page
├── pages/
│   ├── 1_📈_Staffing_Analytics.py
│   ├── 2_⭐_Quality_Insights.py
│   ├── 3_👥_Workforce_Mix.py
│   ├── 4_⚠️_Risk_Dashboard.py
│   └── 5_🔍_Facility_Lookup.py
├── utils.py                  # Helper functions
├── requirements.txt          # Python dependencies
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # Snowflake credentials (create this)
├── secrets_template.toml    # Template for secrets
└── README.md
```

## 🎨 Features

### Interactive Visualizations
- Line charts for trends over time
- Bar charts for comparisons
- Pie charts for distributions
- Scatter plots for correlations
- Color-coded risk indicators

### Filters & Interactivity
- State selection
- Date range selection
- Risk category filters
- Quality tier filters
- Staffing model filters
- Facility search

### Data Export
- Download filtered data as CSV
- Export charts as images
- Generate custom reports

## 🔒 Security

- Credentials stored in `.streamlit/secrets.toml` (gitignored)
- Read-only database access
- No data modification capabilities

## 📊 Data Sources

All data comes from dbt marts in Snowflake:
- `ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_RATIOS`
- `ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_VS_QUALITY`
- `ANALYTICS.DBT_ATARIQ_CORE.MART_EMPLOYEE_VS_CONTRACTOR`
- `ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_VS_OCCUPANCY`
- `ANALYTICS.DBT_ATARIQ_CORE.MART_HIGH_RISK_FACILITIES`

Data is cached for 10 minutes to optimize performance.

## 🚀 Deployment

### Streamlit Cloud

1. Push code to GitHub repository
2. Go to share.streamlit.io
3. Connect your repository
4. Add secrets in Streamlit Cloud dashboard (same format as secrets.toml)
5. Deploy!

### AWS/GCP/Azure

Use Docker:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🔄 Updating Data

Data automatically refreshes every 10 minutes. To force a refresh:
1. Click "Refresh Data" button in the sidebar
2. Or restart the Streamlit app

## 🐛 Troubleshooting

### "Connection Error"
- Verify Snowflake credentials in `.streamlit/secrets.toml`
- Check network connectivity to Snowflake
- Ensure ANALYTICS database exists and user has access

### "No data available"
- Verify dbt models are deployed and populated
- Check that schema names match (DBT_ATARIQ_CORE)
- Run `dbt run` to refresh dbt models

### "Query timeout"
- Increase Snowflake warehouse size
- Reduce date range in filters
- Check for long-running queries in Snowflake

## 📚 Documentation

For more information about the metrics:
- See Phase 8 documentation for dbt model details
- Review data lineage graph in dbt docs
- Check Snowflake tables for raw data

## 🤝 Support

For issues or questions:
1. Check this README
2. Review dbt documentation
3. Check Snowflake query history
4. Verify data pipeline is running

## 📝 License

Internal use only - Healthcare Analytics Project

## 🎯 Next Steps

1. **Customize visualizations** - Modify chart types and colors
2. **Add new pages** - Create additional analysis views
3. **Enhance filters** - Add more interactive controls
4. **Schedule reports** - Set up automated email reports
5. **Add ML insights** - Integrate predictive analytics

---

Built with ❤️ using Streamlit, Snowflake, and dbt
