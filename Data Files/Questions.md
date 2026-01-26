
# Staffing Metrics

-  Average nurse-to-patient ratio by hospital and state (over time)
(derived using total nursing hours and patient census)

-  Total hours worked by nurses per hospital, state, and time period (month/quarter)
(RN, LPN, CNA combined and individually)

-  Percentage of nurses working overtime (proxy-based)
(using contract hours and admin hours as overtime pressure indicators)

# Facility Metrics

-  Comparison of staffing levels vs. patient load
(identifies hospitals where staffing is misaligned with patient volume)

-  Facilities with the lowest staffing levels compared to patient load
(bottom-ranked hospitals based on staffing-to-census ratios)

-  Top hospitals by patient throughput (proxy-based)
(using cumulative patient census over time)

# Operational / Cost-Related Metrics

-  Ratio of permanent staff to temporary/contract staff
(employee vs. contract staffing mix)


# Data Validation for Each Covered Question
# Average nurse-to-patient ratio by hospital and state (over time)

Data availability: ✅ YES

Required data:

Total nursing hours → ✔

Patient census (MDScensus) → ✔

Hospital ID & state → ✔

Time (WorkDate / CY_Qtr) → ✔

# Total hours worked by nurses per hospital, state, and time period

Data availability: ✅ YES

Required data:

RN / LPN / CNA hours → ✔

Hospital & state → ✔

Time → ✔

# Percentage of nurses working overtime (proxy-based)

Data availability: ⚠️ YES (Proxy)

Required data:

Contract hours → ✔

Admin hours → ✔

Total nursing hours → ✔

Must clearly state: overtime is inferred, not directly measured.

# Comparison of staffing levels vs. patient load

Data availability: ✅ YES

Required data:

Staffing hours → ✔

Patient census → ✔

Hospital identifier → ✔

# Facilities with the lowest staffing levels compared to patient load

Data availability: ✅ YES

Required data:

Same as #4 → ✔

# Top hospitals by patient throughput (proxy-based)

Data availability: ⚠️ YES (Proxy)

Required data:

Patient census → ✔

Hospital ID → ✔

Time aggregation → ✔

Throughput is approximated via cumulative census.

# Ratio of permanent staff to temporary/contract staff

Data availability: ✅ YES

Required data:

Employee hours → ✔

Contract hours → ✔

Hospital & state → ✔
