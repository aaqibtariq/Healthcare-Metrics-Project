

# DBT 

Transform raw healthcare data from Snowflake into clean, analytics-ready business metrics using dbt

## dbt CLOUD SETUP

**1. Created dbt Cloud Account**

- Signed up at https://cloud.getdbt.com
- Selected "Developer" plan (free tier)

**2. Created Project: healthcare_metrics**

- Organization: Personal/Company name
- Project name: healthcare_metrics
- Repository: Connected to GitHub (or used dbt Cloud managed repo)

**3. Connected to Snowflake**

- Account: snowflake ID
- Database: ANALYTICS
- Warehouse: TRANSFORM_WH
- Role: HEALTHCARE_PIPELINE_ROLE
- Schema: STAGING (for development)

**4. Connection settings in dbt Cloud**

- type: snowflake
- account: snowflake ID
- user: HEALTHCARE_PIPELINE_USER
- password: [stored securely]
- role: HEALTHCARE_PIPELINE_ROLE
- database: ANALYTICS
- warehouse: TRANSFORM_WH
- schema: STAGING
- threads: 4

**1. Initialized dbt Project Structure**

```
healthcare_metrics/
├── dbt_project.yml          # Project configuration
├── packages.yml             # dbt packages (if needed)
├── models/
│   ├── staging/            # Bronze → Silver (cleaning)
│   ├── intermediate/       # Silver → Silver (joining)
│   └── marts/              # Silver → Gold (metrics)
├── tests/                  # Custom tests
├── macros/                 # Reusable SQL functions
├── seeds/                  # CSV reference data
└── snapshots/              # Slowly changing dimensions
```
- 5. Test Connection
- Clicked "Test Connection" in dbt Cloud
-  Success: Connected to Snowflake

## [Configured dbt_project.yml](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/dbt_project_yml.md)

- Staging as views: Fast, always fresh from source
- Intermediate as views: No storage duplication
- Marts as tables: Pre-aggregated, fast queries for dashboard
- Schemas: Separate schemas for organization
- Tags: Filter models for selective runs



## STAGING MODELS (Bronze → Silver)

**What Staging Models Do:**

- Cast data types correctly
- Trim whitespace
- Handle NULL values
- Standardize date formats
- Rename columns to snake_case
- Remove duplicates
- Add audit columns (created_at, etc.)

 
## [MODEL 1 stg_pbj_staffing.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Staging/MODEL%201%20stg_pbj_staffing.md)

**Purpose:** Clean daily staffing data (1.4M rows)

**Key Transformations:**

- NULL handling with coalesce()
- Date parsing with to_date()
- Column renaming (hrs_rn_emp → rn_emp_hours)
- Calculated totals (total_rn_hours, total_emp_hours)
- Data quality filter (census > 0)

## [MODEL 2 tg_provider_info.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Staging/MODEL%202%20tg_provider_info.md)

**Purpose:** Clean facility master data (14,814 facilities)

**Key Transformations:**

- String trimming
- Standardized naming (provnum → facility_id)
- NULL handling for numeric fields
- Star rating columns preserved

## [MODEL 3 stg_quality_claims.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Staging/MODEL%203%20stg_quality_claims.md)

**Purpose: Clean quality measure claims data (~100K rows)**

**Key Transformations:**

- Categorization (measure_category)
- Date parsing
- Score normalization

*** Now same logic for belows models as well

## [MODEL 4 stg_vbp_performance.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Staging/MODEL%204%20stg_vbp_performance.md)

## [MODEL 5 stg_state_averages.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Staging/MODEL%205%20stg_state_averages.md)

## [MODEL 6 stg_penalties.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Staging/MODEL%206%20stg_penalties.md)

## [MODEL 7 stg_survey_summary.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Staging/MODEL%207%20stg_survey_summary.md)

## [MODEL 8 stg_ownership.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Staging/MODEL%208%20stg_ownership.md)

## [STAGING SCHEMA.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Staging/STAGING%20SCHEMA.md)

**Tests Applied:**

- not_null - Required fields
- unique - Primary keys
- accepted_values - Valid state codes
- accepted_range - Numeric bounds (via dbt_utils package)

## INTERMEDIATE MODELS (Silver → Silver)

**Purpose:** Join staging tables and create reusable building blocks for marts.

## [From DBT](https://github.com/aaqibtariq/Healthcare-Metrics-Project/tree/main/models/intermediate)
## [MODEL 1 int_facility_metrics.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/INTERMEDIATE%20MODELS/MODEL%201%20int_facility_metrics.md)

**Key Features:**

- Monthly aggregation
- Calculates HPRD (Hours Per Resident per Day)
- Workforce mix percentages
- Quality metrics joined
- Handles division by zero (nullif())


## [MODEL 2 int_staffing_calculations.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/INTERMEDIATE%20MODELS/MODEL%202%20int_staffing_calculations.md)

**Calculations:**

- State benchmark comparison
- Percent above/below state average
- Occupancy rate
- Staffing adequacy categories


## [MODEL 3 int_quality_scores.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/INTERMEDIATE%20MODELS/MODEL%203%20int_quality_scores.md)
**Purpose:** Composite quality scoring

## MARTS MODELS (Silver → Gold)

**Purpose:** Create final business metrics optimized for dashboard consumption.

## [mart_staffing_ratios.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Marts/mart_staffing_ratios.md)

**Purpose:** METRIC #1 - Nurse-to-patient staffing ratios
**Output:** 14,547 rows (facility-month combinations)



## [mart_high_risk_facilities.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Marts/mart_high_risk_facilities.md)

**Purpose:** METRIC #5 - High-risk facility identification
**Output:** 4,029 facilities with risk scores


## [mart_staffing_vs_quality.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Marts/mart_staffing_vs_quality.md)

**Purpose:** METRIC #3 - Staffing vs quality correlation
**Output:** 14,814 facilities with staffing-quality metrics



## [mart_employee_vs_contractor.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Marts/mart_employee_vs_contractor.md)

**Purpose:** METRIC #4 - Employee vs contractor analysis
**Output:** 14,547 facility-months with workforce composition

## [mart_staffing_vs_occupancy.md](https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/Marts/mart_staffing_vs_occupancy.md)

**Purpose:** Complete facility profiles for lookup
**Output:** 14,547 facility profiles

## dbt TESTS



##  DBT Pipeline Diagram


<p align="center">
  <img src="https://raw.githubusercontent.com/aaqibtariq/Healthcare-Metrics-Project/main/All%20Phases/DBT/image%20-%202026-03-18T134333.439.png" width="800"/>
</p>


```

RAW.HEALTHCARE (Bronze)
    ↓ dbt staging models
ANALYTICS.STAGING (Silver - Clean)
    ↓ dbt intermediate models
ANALYTICS.INTERMEDIATE (Silver - Joined)
    ↓ dbt marts models
ANALYTICS.CORE (Gold - Metrics)
    ↓
Streamlit Dashboard

```

LEFT SIDE - SOURCES (Green/Blue):

- raw.state_averages (SRC - green source table)
- stg_quality_claims (MDL - blue staging model)
- stg_penalties
- stg_provider_info
- stg_survey_summary
- stg_pbj_staffing

MIDDLE - INTERMEDIATE LAYER:

- int_facility_quality_scores ← Joins multiple staging tables
- int_facility_daily_staffing ← Combines staffing + provider data
- int_facility_risk_factors ← Risk assessment calculations

RIGHT SIDE - BUSINESS METRICS (Your 5 Marts!):

- mart_high_risk_facilities  - Critical facilities needing intervention
- mart_staffing_ratios  - Monthly staffing benchmarks
- mart_staffing_vs_quality  - Staffing impact on quality
- mart_employee_vs_contractor  - Workforce composition
- mart_staffing_vs_occupancy  - Occupancy vs staffing correlation


 WHAT THIS SHOWS:
- Clean Architecture - Source → Staging → Intermediate → Marts
- Proper Layering - Each layer builds on the previous
- Clear Dependencies - You can see exactly how data flows
- Reusable Components - Intermediate models feed multiple marts


Whats done

- 16 dbt models transforming 1.6M+ rows
- 50 data quality tests (100% passing!)
- Interactive documentation with visual lineage
- 5 business-critical metrics ready for dashboards
- Clean, maintainable architecture

  
