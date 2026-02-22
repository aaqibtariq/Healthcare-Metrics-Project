

# QUESTIONS WE WILL ANSWER (3 of 4):

-  Staffing vs occupancy relationship
-  Facilities with highest overtime
-  Average staffing by state/type
-  Length of stay trends - Data doesn't exist

# METRICS WE WILL CALCULATE (5 Core):

-  Nurse-to-Patient Staffing Ratios
-  Staffing vs Occupancy Correlation
-  Staffing vs Quality (Readmissions)
-  Employee vs Contractor
-  High-Risk Facility Identification

# FILES WE WILL USE (8 of 22):

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv -> Primary staffing data - core dataset
-  NH_ProviderInfo_Oct2024.csv -> Master dimension - facility characteristics
-  NH_QualityMsr_Claims_Oct2024.csv -> Quality outcomes - readmissions, ED visits
-  FY_2024_SNF_VBP_Facility_Performance.csv -> VBP scores, readmission rates
-  NH_StateUSAverages_Oct2024.csv -> Benchmarking - state/national comparisons
-  NH_Penalties_Oct2024.csv -> Compliance - fines and penalties
-  NH_SurveySummary_Oct2024.csv -> Compliance - deficiency summaries
-  NH_Ownership_Oct2024.csv -> Ownership analysis dimension

# FILES WE ARE EXCLUDING (14 of 22):

## Reference Tables (can reference as needed, not loaded in pipeline):

-  NH_CitationDescriptions_Oct2024.csv
-  NH_DataCollectionIntervals_Oct2024.csv
-  NH_HlthInspecCutpointsState_Oct2024.csv

## Redundant/Overlapping:

-  NH_QualityMsr_MDS_Oct2024.csv (overlaps with Claims)
-  SNF_QRP_Provider_Data_Oct2024.csv (overlaps with Claims/VBP)
-  SNF_QRP_National_Data_Oct2024.csv (benchmarks in StateAverages)
-  FY_2024_SNF_VBP_Aggregate_Performance.csv (only 1 row, low value)

## Granular Detail (summary data sufficient):

-  NH_HealthCitations_Oct2024.csv (use SurveySummary instead)
-  NH_FireSafetyCitations_Oct2024.csv (use SurveySummary instead)
-  NH_SurveyDates_Oct2024.csv (dates in SurveySummary)

## Out of Scope:

-  NH_CovidVaxAverages_20241027.csv
-  NH_CovidVaxProvider_20241027.csv
-  Swing_Bed_SNF_data_Oct2024.csv (specialized facilities)

  
  
  # METRICS WE WILL CALCULATE (5 CORE METRICS)

# METRIC 1: Nurse-to-Patient Staffing Ratios

# Average nursing hours per resident per day

## WHY IT MATTERS:

-  Industry standard staffing metric
-  Direct indicator of care capacity
-  Regulatory compliance benchmark
-  Quality of care predictor

## DATA SOURCES:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv
-  NH_ProviderInfo_Oct2024.csv

## CALCULATIONS:

```
python# Overall Nursing Hours Per Resident Per Day
Total_Nursing_HPRD = (Hrs_RN + Hrs_LPN + Hrs_CNA) / MDScensus

# By Staff Type
RN_HPRD = Hrs_RN / MDScensus
LPN_HPRD = Hrs_LPN / MDScensus
CNA_HPRD = Hrs_CNA / MDScensus

# Breakdowns
- By facility (PROVNUM)
- By state (STATE)
- By month (aggregate WorkDate)
- By ownership type (from ProviderInfo)
- By facility size (bed count categories)

```

## DELIVERABLES:

-  Summary statistics table
-  State comparison heatmap
-  Time trend line charts
-  Top/bottom 10 facilities


   # METRIC 2: Staffing vs Occupancy Correlation
# Relationship between patient census and staffing levels

## WHY IT MATTERS:

-  Optimizes resource allocation
-  Identifies staffing inefficiencies
-  Directly answers Question #1
-  Informs workforce planning

## DATA SOURCES:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv
-  NH_ProviderInfo_Oct2024.csv

## CALCULATIONS:
```
python# Variables
X = Occupancy_Rate = (MDScensus / Number_of_Certified_Beds) * 100
Y = Staffing_Hours_Per_Patient = Total_Nursing_Hours / MDScensus

# Analysis
- Pearson correlation coefficient
- Scatter plot with regression line
- Segment by occupancy levels (Low <70%, Medium 70-85%, High >85%)
- Compare staffing efficiency across segments

# Questions Answered
- Do facilities increase staffing proportionally to occupancy?
- Are some facilities overstaffed when census is low?
- Are some facilities understaffed during high occupancy?

```
## DELIVERABLES:

-  Correlation coefficient (r-value, p-value)
-  Scatter plot visualization
-  Segmented analysis by occupancy level
-  Outlier facilities flagged

   # METRIC 3: Staffing vs Quality Outcomes (Readmissions)
   
# Relationship between staffing levels and patient readmission rates

## WHY IT MATTERS:

-  Quality of care indicator
-  Financial impact (VBP penalties/bonuses)
-  Directly answers Question #1 (quality dimension)
-  Evidence-based staffing decisions

## DATA SOURCES:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv
-  NH_QualityMsr_Claims_Oct2024.csv (Measures 521, 551)
-  FY_2024_SNF_VBP_Facility_Performance.csv

## CALCULATIONS:

```
python# Variables
X = Avg_Nursing_HPRD = Average staffing hours per patient
Y = Readmission_Rate = Measure 521 (Short Stay) or 551 (Long Stay)

# Analysis
- Correlation analysis (negative correlation expected)
- Quartile analysis:
  - Q1: Lowest staffing → Readmission rate?
  - Q4: Highest staffing → Readmission rate?
- Control variables: Facility size, ownership, state

# Additional Quality Metrics
- ED visit rates (Measure 522, 552)
- VBP Performance Scores
- Falls with major injury rates

```

## DELIVERABLES:

-  Correlation matrix (staffing vs multiple quality metrics)
-  Scatter plots with confidence intervals
-  Quartile comparison tables
-  Best practice facilities (high staffing + low readmissions)

 # METRIC 4: Employee vs Contractor Staffing Mix
# Ratio of employed staff to contracted staff

## WHY IT MATTERS:

-  Cost implications (contractors ~30-50% more expensive)
-  Continuity of care (employed staff = better)
-  Workforce stability indicator
-  Strategic staffing decisions

## DATA SOURCES:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv

## CALCULATIONS:

```
python# Hours by Employment Type
Employee_Hours = Hrs_RN_emp + Hrs_LPN_emp + Hrs_CNA_emp
Contractor_Hours = Hrs_RN_ctr + Hrs_LPN_ctr + Hrs_CNA_ctr
Total_Hours = Employee_Hours + Contractor_Hours

# Metrics
Contractor_Percentage = (Contractor_Hours / Total_Hours) * 100
Employee_Percentage = (Employee_Hours / Total_Hours) * 100

# By Staff Type
RN_Contractor_Pct = Hrs_RN_ctr / Hrs_RN
LPN_Contractor_Pct = Hrs_LPN_ctr / Hrs_LPN
CNA_Contractor_Pct = Hrs_CNA_ctr / Hrs_CNA

# Correlations
- Contractor use vs Quality outcomes
- Contractor use vs Turnover rates
- Contractor use vs Facility size/ownership

```

## DELIVERABLES:

-  Stacked bar chart: Employee vs Contractor by state
-  Pie charts: Mix by facility type
-  Trend analysis: Contractor usage over Q2 2024
-  Correlation with turnover and quality

   # METRIC 5: High-Risk Facilities Identification
# Facilities with staffing-quality-cost misalignment

## WHY IT MATTERS:

-  Actionable - prioritize intervention targets
-  Comprehensive - combines multiple dimensions
-  Management decision support
-  Risk management

## DATA SOURCES:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv
-  NH_ProviderInfo_Oct2024.csv
-  NH_Penalties_Oct2024.csv
-  FY_2024_SNF_VBP_Facility_Performance.csv

## CALCULATIONS:

```
python# Risk Score Components
1. Low Staffing Score (Below state average by >20%)
2. High Turnover Score (Turnover > 50%)
3. High Penalties Score (Fines > state median)
4. Poor Quality Score (Readmission rate > state avg)
5. Low VBP Score (Payment multiplier < 1.0)

# Composite Risk Score
Risk_Score = Weighted sum of above components

# Segments
- High Risk (score > 7)
- Medium Risk (score 4-7)
- Low Risk (score < 4)

# Also Identify Best Performers
Excellence_Score = High staffing + Low turnover + High quality + No penalties

```

## DELIVERABLES:

-  Risk-ranked facility list
-  Heat map by state
-  Detailed profiles of top 10 high-risk facilities
-  Best practice profiles (top 10 excellent facilities)
-  Actionable recommendations







# PART 1: QUESTIONS WE WILL ANSWER (3 of 4)

# QUESTION 1: What is the relationship between nurse staffing levels and hospital occupancy rates?
WHY FOCUS ON THIS:

- Core project objective - understanding staffing effectiveness
- Fully calculable with available data
- High business value - optimize staffing based on patient load
- Actionable insights - improve workforce planning

## DATA SOURCES:

-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv -> Daily nursing hours (RN, LPN, CNA), Patient census (MDScensus) -> Calculate staffing hours per patient per day
-  NH_ProviderInfo_Oct2024.csv -> umber of Certified Beds, Facility info -> Calculate occupancy rate = Census / Beds
-  NH_StateUSAverages_Oct2024.csv -> State/national benchmarks -> Compare facility performance to benchmarks


## HOW WE CALCULATE:

```
python# Staffing Level
Staffing_Hours_Per_Patient = (Hrs_RN + Hrs_LPN + Hrs_CNA) / MDScensus

 Occupancy Rate
Occupancy_Rate = (MDScensus / Number_of_Certified_Beds) * 100

 Analysis
- Correlation analysis (Pearson/Spearman)
- Scatter plot visualization
- Trend analysis over time
- Group by state, ownership type, facility size

```

## EXPECTED OUTCOMES:

Correlation coefficient (positive/negative/no correlation)
Identify optimal staffing ratios for different occupancy levels
Flag facilities that are over/under-staffed relative to census


# QUESTION 2: Which hospitals have the highest overtime hours for nurses?
WHY FOCUS ON THIS:

- Operational efficiency insight
- Proxy metrics available (not direct overtime data)
- Cost implications - overtime is expensive
- Staff burnout indicator


## DATA SOURCES:


- PBJ_Daily_Nurse_Staffing_Q2_2024.csv->  Daily total hours, Expected census -> Identify patterns suggesting overtime
- NH_ProviderInfo_Oct2024.csv -> Expected staffing ratios, Turnover rates -> Benchmark against expected levels
  
## HOW WE CALCULATE (PROXY METRICS):

```
python# Proxy 1: High Utilization Days
Daily_Expected_Hours = MDScensus * Expected_Hours_Per_Patient_Per_Day
Overtime_Proxy = (Actual_Hours - Expected_Hours) / Expected_Hours

# Proxy 2: Variability Pattern
High_Variability = STD(Daily_Hours) > Threshold
# High variability suggests irregular staffing = likely overtime

# Proxy 3: Above-Benchmark Hours
Benchmark_Comparison = Facility_Hours_Per_Resident > State_Avg * 1.2

# Ranking
Rank facilities by:
1. Days with >20% above expected hours
2. Total excess hours over 3 months
3. Correlation with high turnover rates

```

### EXPECTED OUTCOMES:

-  Top 10 facilities with highest likely overtime
-  Facilities with most staffing variability (burnout risk)
-  Correlation between high hours and quality issues

Limitation: We don't have actual overtime data or individual nurse schedules. We can identify facilities with patterns suggesting overtime but cannot calculate exact overtime percentages.

#  QUESTION 3: What are the average staffing levels by state and hospital type?
WHY FOCUS ON THIS:

- Fully calculable - straightforward aggregation
- Benchmarking value - compare states and facility types
- Policy implications - identify states with staffing gaps
- High visualization potential - great for dashboard

## DATA SOURCES:


-  PBJ_Daily_Nurse_Staffing_Q2_2024.csv -> Daily hours by facility -> Calculate averages
-  NH_ProviderInfo_Oct2024.csv -> tate ownership Type, Provider Type, Facility size -> Grouping dimensions
-  NH_StateUSAverages_Oct2024.csv ->  re-calculated state averages -> Validation and benchmarking

## HOW WE CALCULATE:
python# Average Staffing by State
Avg_Hours_Per_Patient = (Total_RN + Total_LPN + Total_CNA) / Total_Census
Group by: STATE
Calculate: Mean, Median, Min, Max, Std Dev

# Average Staffing by Hospital Type
Hospital_Type dimensions:
- Ownership Type (For-profit, Non-profit, Government)
- Provider Type (Medicare/Medicaid, Medicare only, etc.)
- Size (Small <50 beds, Medium 50-100, Large >100)

Group by: Ownership_Type, Provider_Type, Bed_Count_Category
Calculate: Mean staffing hours per resident per day

# Breakdowns
- RN hours per patient (by state/type)
- LPN hours per patient (by state/type)
- CNA hours per patient (by state/type)
- Total nursing hours per patient (by state/type)
- Employee vs Contractor ratio (by state/type)

## EXPECTED OUTCOMES:

Heatmap: Average staffing by state
Bar charts: Staffing by ownership type
Box plots: Distribution of staffing levels
Identify best/worst performing states and facility types

# QUESTION 4: What trends can you identify in patient length of stay over time?
WHY WE CANNOT ANSWER THIS:
-  No length of stay data available
-  No admission dates
-  No discharge dates
-  No Average Length of Stay metrics


