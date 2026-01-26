# Staffing Metrics
✅ Average nurse-to-patient ratio

Status: ✅ YES (Strong, Core Metric)

Why:

You have total nursing hours (RN, LPN, CNA, etc.)

You have MDScensus (patient count proxy)

You have hospital + state from ProviderInfo

✔ Can calculate by:

Hospital

State

Time (day / quarter)

# Total hours worked by nurses

Status: ✅ YES

Why:

All nurse hours are explicitly available

Can aggregate by:

Hospital

State

Month / Quarter (from WorkDate / CY_Qtr)

✔ Very clean and defensible

# Staffing levels vs patient load

Status: ✅ YES (Very Strong)

Why:

Staffing hours ✅

Patient census ✅

✔ You can answer:

“Which hospitals are under-staffed relative to patient load?”

“Mismatch analysis”

# Top 10 hospitals by patient throughput

Status: ✅ YES (Proxy)

Why:

Use cumulative MDScensus over time

Rank hospitals

⚠️ Must clarify:

“Throughput proxy using cumulative patient census”

# Facilities with lowest staffing vs patient load

Status: ✅ YES

This naturally falls out of:

Nurse-to-patient ratio

Staffing vs census analysis

# Ratio of permanent vs contract staff

Status: ✅ YES (Strong)

Why:

Emp vs Ctr hours are clearly separated




# Final Metrics Set

Average nurse-to-patient ratio (hospital, state, time)

Total nursing hours (RN/LPN/CNA) by hospital & state

Staffing vs patient load mismatch index

Contract vs employee staffing ratio

Overtime pressure proxy (contract + admin hours)

These directly answer your objective and management questions.
