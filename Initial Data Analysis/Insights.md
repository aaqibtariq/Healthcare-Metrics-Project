
# 1. STAFFING METRICS

## Average nurse-to-patient ratio by hospital, state, and department

Status:  YES (Hospital & State only, NOT Department)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - For daily hours (Hrs_RN, Hrs_LPN, Hrs_CNA) and census (MDScensus)
-  NH_ProviderInfo_Oct2024.csv - For STATE grouping

## Calculation:
```
sqlNurse_to_Patient_Ratio = (Hrs_RN + Hrs_LPN + Hrs_CNA) / MDScensus
GROUP BY PROVNUM (hospital), STATE
```
Limitation:  No "department" data (nursing homes don't have hospital-style departments like ICU, ER, Med/Surg)
Achievable: Hospital (Yes) | State (Yes) | Department (No)


## Total hours worked by nurses per hospital, state, and month

Status:  YES (100% Calculable)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - For all nursing hours and WorkDate

## Calculation:
```
sqlTotal_Hours = SUM(Hrs_RN + Hrs_LPN + Hrs_CNA)
GROUP BY PROVNUM, STATE, MONTH(WorkDate)
```
Achievable:  Fully calculable


## Percentage of nurses working overtime

Status:  NO (Direct data unavailable, proxy possible)

## Problem:

-  No individual nurse data (only facility-level aggregates)
-  No shift-level data
-  No overtime flags

## Proxy Option:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - Can identify days with abnormally high hours
-  NH_ProviderInfo_Oct2024.csv - For expected staffing benchmarks

## Calculate:

```
sql-- Facilities with high utilization patterns (suggesting overtime)
Days_With_High_Staffing = COUNT(days WHERE actual_hours > expected_hours * 1.15)
```
Achievable:  Direct metric (No), but Proxy metric (Yes)

# 2. FACILITY METRICS

## Hospital occupancy rate trends over the past year (monthly/quarterly)

Status:  PARTIALLY (Only Q2 2024 available, not full year)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - For MDScensus (daily patient count)
-  NH_ProviderInfo_Oct2024.csv - For Number of Certified Beds

## Calculation:
```
sqlOccupancy_Rate = (MDScensus / Number_of_Certified_Beds) * 100
GROUP BY PROVNUM, MONTH/QUARTER
```
Limitation:  Only 3 months of data (April-June 2024), not 12 months
Achievable: Calculation (Yes) | Full year (no) | Q2 2024 (Yes)

## Bed utilization rates by hospital and department

Status:  PARTIALLY (Hospital only, not department)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - For census
-  NH_ProviderInfo_Oct2024.csv - For certified beds

## Calculation:
```
sqlBed_Utilization = (MDScensus / Number_of_Certified_Beds) * 100
```
Limitation:  No department-level data
Achievable: Hospital (yes) | Department (no)


## Comparison of staffing levels vs. bed occupancy rates

Status:  YES (Fully calculable)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - For staffing hours and census
-  NH_ProviderInfo_Oct2024.csv - For certified beds

## Calculation:
```
sqlStaffing_Level = Total_Nursing_Hours / MDScensus
Occupancy_Rate = MDScensus / Number_of_Certified_Beds
-- Correlation analysis between the two
```

Achievable:  Answers Question #1!

## Top 10 hospitals with the highest patient throughput

Status:  YES (Fully calculable)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - For daily census
-  NH_ProviderInfo_Oct2024.csv - For Average Number of Residents per Day

## Calculation:
```
sqlPatient_Throughput = AVG(MDScensus) or SUM(MDScensus) -- Total resident days
ORDER BY Patient_Throughput DESC
LIMIT 10
```
Achievable:  Fully calculable

## Facilities with the lowest staffing levels compared to patient load

Status:  YES (Fully calculable)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - For hours and census

## Calculation:
```
sqlStaffing_Per_Patient = (Hrs_RN + Hrs_LPN + Hrs_CNA) / MDScensus
ORDER BY Staffing_Per_Patient ASC
LIMIT 10
```
Achievable:  Fully calculable

# 3. QUALITY METRICS

## Readmission rates within 30 days by hospital, state, and diagnosis category

Status:  PARTIALLY (Hospital & State only, NOT diagnosis category)

## Files Used:

-  NH_QualityMsr_Claims_Oct2024.csv - For readmission measures (521, 522, 551, 552)
-  FY_2024_SNF_VBP_Facility_Performance.csv - For risk-standardized readmission rates

## Available Measures:

-  Measure 521: Percentage of short-stay residents who were rehospitalized
-  Measure 551: Number of hospitalizations per 1000 long-stay resident days

## Calculation:

```
sqlSELECT PROVNUM, STATE, Adjusted_Score as Readmission_Rate
FROM NH_QualityMsr_Claims
WHERE Measure_Code IN (521, 551)
```

Limitation:  No diagnosis category breakdown
Achievable: Hospital (yes)  | State (yes)  | Diagnosis Category (No)

## Correlation between nurse staffing levels and readmission rates

Status:  YES (Fully calculable)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - For staffing levels
-  NH_QualityMsr_Claims_Oct2024.csv - For readmission rates (Measure 521, 551)
-  FY_2024_SNF_VBP_Facility_Performance.csv - For VBP readmission rates

## Calculation:
```
sql-- Calculate average staffing per facility
Avg_Staffing = AVG(Total_Nursing_Hours / MDScensus)

-- Get readmission rate per facility
Readmission_Rate = Adjusted_Score FROM Claims WHERE Measure_Code = 521

-- Statistical correlation (Pearson/Spearman)
CORRELATION(Avg_Staffing, Readmission_Rate)
```
Achievable:  Answers Question #1!

# 4. COST METRICS (nothing)

# 5. OPERATIONAL METRICS

## Ratio of permanent staff to temporary/contract staff

Status:  YES (Fully calculable)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - Has employed vs contracted hours

## Columns Available:

-  Hrs_RN_emp, Hrs_LPN_emp, Hrs_CNA_emp (employed)
-  Hrs_RN_ctr, Hrs_LPN_ctr, Hrs_CNA_ctr (contracted)

## Calculation:
```
sqlEmployed_Hours = SUM(Hrs_RN_emp + Hrs_LPN_emp + Hrs_CNA_emp)
Contracted_Hours = SUM(Hrs_RN_ctr + Hrs_LPN_ctr + Hrs_CNA_ctr)
Ratio = Employed_Hours / Contracted_Hours
```
Achievable: Fully calculable

## Trend analysis of nurse attrition rates

Status:  YES (Pre-calculated in data)

## Files Used:

-  NH_ProviderInfo_Oct2024.csv - Contains turnover data

## Columns Available:

-  Total nursing staff turnover
-  Registered Nurse turnover
-  Number of administrators who have left

## Calculation:
```
sql-- Already calculated, just aggregate/compare
SELECT STATE, AVG(Total_nursing_staff_turnover) as Avg_Turnover
FROM NH_ProviderInfo
GROUP BY STATE
```
Achievable: Pre-calculated, ready to use


# QUESTIONS NEED TO ANSWER

## Q1: What is the relationship between nurse staffing levels and hospital occupancy rates?

Status:  YES (Fully answerable)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv
-  NH_ProviderInfo_Oct2024.csv

## Analysis:
```
sql-- Staffing level
Staffing_HPRD = Total_Nursing_Hours / MDScensus

-- Occupancy rate
Occupancy = MDScensus / Number_of_Certified_Beds

-- Correlation analysis
CORRELATION(Staffing_HPRD, Occupancy)
```

Achievable:  Core project question - fully answerable

##  Q2: Which hospitals have the highest overtime hours for nurses?

Status:  PROXY ONLY (No direct overtime data)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv
-  NH_ProviderInfo_Oct2024.csv

## Proxy Metrics:
```
sql-- High utilization days (suggests overtime)
High_Utilization_Days = COUNT(days WHERE actual_hours > expected_hours * 1.20)

-- Facilities with highest hour variability (suggests irregular staffing/overtime)
Staffing_Variability = STDDEV(Daily_Total_Hours)

-- Facilities with highest hours per resident
Hours_Per_Resident = AVG(Total_Hours / MDScensus)
ORDER BY DESC
```
Achievable: Direct overtime (no) | Proxy indicators (yes)

## Q3: What are the average staffing levels by state and hospital type?

Status:  YES (Fully answerable)

## Files Used:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv
-  NH_ProviderInfo_Oct2024.csv
-  NH_StateUSAverages_Oct2024.csv (for validation)

## Analysis:
```
sql-- By state
SELECT STATE, 
       AVG(Total_Nursing_Hours / MDScensus) as Avg_Staffing_HPRD
FROM PBJ_Staffing JOIN ProviderInfo
GROUP BY STATE

-- By hospital type (ownership)
SELECT Ownership_Type,
       AVG(Total_Nursing_Hours / MDScensus) as Avg_Staffing_HPRD
GROUP BY Ownership_Type

-- By facility size
SELECT CASE 
         WHEN Number_of_Certified_Beds < 50 THEN 'Small'
         WHEN Number_of_Certified_Beds < 100 THEN 'Medium'
         ELSE 'Large'
       END as Facility_Size,
       AVG(Staffing_HPRD)
GROUP BY Facility_Size
```

Achievable:  Fully answerable

## Q4: What trends can you identify in patient length of stay over time?
Status:  NO (Data doesn't exist)


## Core Files (Must Use):

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv - Used in almost EVERY metric
-  NH_ProviderInfo_Oct2024.csv - Master dimension, used frequently
-  NH_QualityMsr_Claims_Oct2024.csv - For readmissions, quality
-  FY_2024_SNF_VBP_Facility_Performance.csv - For VBP scores, readmissions
-  NH_StateUSAverages_Oct2024.csv - For benchmarking

Supporting Files:

- NH_Penalties_Oct2024.csv - For cost/risk analysis
- NH_SurveySummary_Oct2024.csv - For compliance metrics
- NH_Ownership_Oct2024.csv - For ownership analysis
