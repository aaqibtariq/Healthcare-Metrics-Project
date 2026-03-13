# 🚀 QUICK SETUP GUIDE - Healthcare Analytics Dashboard

## ✅ Step-by-Step Setup (5 minutes)

### **STEP 1: Download the Dashboard Files**
You have all the files in the `healthcare_dashboard` folder:
- streamlit_app.py (home page)
- pages/ folder (5 analytics pages)
- utils.py (helper functions)
- requirements.txt (dependencies)
- .streamlit/config.toml (styling)
- secrets_template.toml (credential template)

### **STEP 2: Install Python Packages**
```bash
cd healthcare_dashboard
pip install -r requirements.txt
```

This installs:
- streamlit (dashboard framework)
- snowflake-connector-python (database connection)
- pandas (data manipulation)
- plotly (interactive charts)

### **STEP 3: Configure Snowflake Credentials**

Create `.streamlit/secrets.toml`:
```bash
mkdir -p .streamlit
nano .streamlit/secrets.toml
```

Add your Snowflake credentials:
```toml
[snowflake]
user = "HEALTHCARE_PIPELINE_USER"
password = "YOUR_PASSWORD"
account = "YOUR_ACCOUNT.us-east-1"  # Check Snowflake for exact format
warehouse = "TRANSFORM_WH"
database = "ANALYTICS"
schema = "DBT_ATARIQ_CORE"
role = "HEALTHCARE_PIPELINE_ROLE"
```

**Find your Snowflake account identifier:**
- Go to Snowflake
- Look at the URL: `https://YOUR_ACCOUNT.snowflakecomputing.com`
- Your account ID is the part before `.snowflakecomputing.com`

### **STEP 4: Run the Dashboard**
```bash
streamlit run streamlit_app.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.x:8501
```

### **STEP 5: Open in Browser**
Navigate to: `http://localhost:8501`

You should see the Healthcare Analytics Dashboard home page!

---

## 🎨 What You'll See

### **Home Page:**
- Total facilities count
- Critical risk facility count
- High quality facility count
- Average nursing HPRD
- Risk category pie chart
- Quality distribution chart
- Top states by staffing
- Staffing model distribution

### **Navigation Sidebar:**
Click through 5 analytics pages:
1. 📈 Staffing Analytics
2. ⭐ Quality Insights
3. 👥 Workforce Mix
4. ⚠️ Risk Dashboard
5. 🔍 Facility Lookup

---

## 🔧 Troubleshooting

### **Problem: "ModuleNotFoundError: No module named 'streamlit'"**
**Solution:** Run `pip install -r requirements.txt`

### **Problem: "Connection error" or "Authentication failed"**
**Solution:** 
1. Check `.streamlit/secrets.toml` exists
2. Verify Snowflake credentials are correct
3. Test connection in Snowflake first

### **Problem: "No data available"**
**Solution:**
1. Verify dbt models are deployed: `dbt run`
2. Check schema name matches: `DBT_ATARIQ_CORE`
3. Query Snowflake directly to confirm data exists:
```sql
SELECT COUNT(*) FROM ANALYTICS.DBT_ATARIQ_CORE.MART_STAFFING_RATIOS;
```

### **Problem: Dashboard is slow**
**Solution:**
1. Increase Snowflake warehouse size
2. Reduce date range filters
3. Dashboard caches data for 10 minutes - wait for cache

---

## 🌐 Deploy to Streamlit Cloud (Optional)

### **Make it shareable on the internet:**

1. **Push code to GitHub:**
```bash
git init
git add .
git commit -m "Healthcare Analytics Dashboard"
git push
```

2. **Go to Streamlit Cloud:**
   - Visit: https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Select branch: `main`
   - Main file: `streamlit_app.py`

3. **Add secrets in Streamlit Cloud:**
   - In app settings, go to "Secrets"
   - Copy contents of `.streamlit/secrets.toml`
   - Paste and save

4. **Deploy!**
   - Your dashboard will be live at: `https://your-app-name.streamlit.app`
   - Share the link with your team!

---

## 📊 Using the Dashboard

### **Filters:**
- Every page has a sidebar with filters
- Select states, date ranges, categories
- Click "Refresh Data" to force reload

### **Export Data:**
- Every page has a "Download CSV" button
- Export filtered data for Excel analysis

### **Navigation:**
- Use sidebar to switch between pages
- Click facility names to drill down (on Facility Lookup page)

---

## 🎯 Next Steps

1. **Customize colors:** Edit `.streamlit/config.toml`
2. **Add new charts:** Modify page files in `pages/`
3. **Schedule reports:** Use Streamlit Cloud scheduled runs
4. **Add authentication:** Use Streamlit auth or deploy behind SSO

---

## 📚 Files Overview

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Home page with executive dashboard |
| `pages/1_📈_Staffing_Analytics.py` | Staffing ratios vs benchmarks |
| `pages/2_⭐_Quality_Insights.py` | Quality scores and correlation |
| `pages/3_👥_Workforce_Mix.py` | Employee vs contractor analysis |
| `pages/4_⚠️_Risk_Dashboard.py` | High-risk facility identification |
| `pages/5_🔍_Facility_Lookup.py` | Individual facility search |
| `utils.py` | Snowflake connection & helper functions |
| `requirements.txt` | Python package dependencies |
| `.streamlit/config.toml` | Theme and styling |
| `.streamlit/secrets.toml` | Snowflake credentials (YOU CREATE THIS) |

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] `.streamlit/secrets.toml` created with Snowflake credentials
- [ ] dbt models deployed in Snowflake
- [ ] Dashboard runs locally (`streamlit run streamlit_app.py`)
- [ ] Can see data on home page
- [ ] All 5 pages load successfully

---

**🎉 Congratulations! Your healthcare analytics dashboard is live!**

Questions? Check the README.md for detailed documentation.
