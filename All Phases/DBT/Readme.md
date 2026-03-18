

# DBT 

Transform raw healthcare data from Snowflake into clean, analytics-ready business metrics using dbt

## dbt CLOUD SETUP


- 1. Created dbt Cloud Account

- Signed up at https://cloud.getdbt.com
- Selected "Developer" plan (free tier)

- 2. Created Project: healthcare_metrics

- Organization: Personal/Company name
- Project name: healthcare_metrics
- Repository: Connected to GitHub (or used dbt Cloud managed repo)

- 3. Connected to Snowflake

- Account: snowflake ID
- Database: ANALYTICS
- Warehouse: TRANSFORM_WH
- Role: HEALTHCARE_PIPELINE_ROLE
- Schema: STAGING (for development)

- 4. Connection settings in dbt Cloud

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

## Configured dbt_project.yml
```yml


# Name your project! Project names should contain only lowercase characters
# and underscores. A good package name should reflect your organization's
# name or the intended use of these models
name: 'healthcare_metrics'
version: '1.0.0'
config-version: 2

# This setting configures which "profile" dbt uses for this project.
profile: 'default'

# These configurations specify where dbt should look for different types of files.
# The `model-paths` config, for example, states that models in this project can be
# found in the "models/" directory. You probably won't need to change these!
model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"  # directory which will store compiled SQL files
clean-targets:         # directories to be removed by `dbt clean`
  - "target"
  - "dbt_packages"


# Configuring models
# Full documentation: https://docs.getdbt.com/docs/configuring-models

# In dbt, the default materialization for a model is a view. This means, when you run 
# dbt run or dbt build, all of your models will be built as a view in your data platform. 
# The configuration below will override this setting for models in the example folder to 
# instead be materialized as tables. Any models you add to the root of the models folder will 
# continue to be built as views. These settings can be overridden in the individual model files
# using the `{{ config(...) }}` macro.

# Configuring models
# Full documentation: https://docs.getdbt.com/docs/configuring-models

models:
  healthcare_metrics:
    # Staging models - cleaned raw data (Bronze -> Silver)
    staging:
      +materialized: view
      +schema: staging
      
    # Intermediate models - complex transformations
    intermediate:
      +materialized: view
      +schema: intermediate
      
    # Marts - business metrics (Silver -> Gold)
    marts:
      +materialized: table
      +schema: core

```

- Staging as views: Fast, always fresh from source
- Intermediate as views: No storage duplication
- Marts as tables: Pre-aggregated, fast queries for dashboard
- Schemas: Separate schemas for organization
- Tags: Filter models for selective runs

## STAGING MODELS (Bronze → Silver)

What Staging Models Do:

- Cast data types correctly
- Trim whitespace
- Handle NULL values
- Standardize date formats
- Rename columns to snake_case
- Remove duplicates
- Add audit columns (created_at, etc.)

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

  
