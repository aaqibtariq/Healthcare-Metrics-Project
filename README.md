# Healthcare-Metrics-Project

## Core Objective

- **Industry:** Healthcare Analytics
- **Data Volume:** 1.6M+ rows across 8 data sources
- **Facilities Tracked:** 14,814 skilled nursing facilities
- **Total Nursing Hours Analyzed:** 393+ million hours
- **Architecture:** Event-driven, serverless, cloud-native

Build a unified analytics system to understand how nurse staffing, workload, and patient volumes impact care quality and operational efficiency across multiple hospital facilities.


## Project Goal

The objective of this project is to design and implement a scalable, event-driven data pipeline that ingests healthcare operational data from Google Drive, stores it in AWS S3, and processes it in Snowflake using a Medallion Architecture (Bronze → Silver → Gold).

The system enables incremental data ingestion, automated transformation using dbt, and interactive analytics through a Streamlit dashboard.

The goal is to provide reliable, near real-time insights into healthcare facility performance, staffing metrics, and operational efficiency while optimizing compute costs through event-driven orchestration.

## Abstract

This project implements an end-to-end cloud-based data engineering pipeline for healthcare metrics analysis. Data files are incrementally ingested from Google Drive into AWS S3 using AWS Lambda and securely managed credentials via AWS Secrets Manager.

The pipeline uses event-driven orchestration to trigger downstream transformations only when new data arrives. Snowflake serves as the cloud data warehouse, where data is structured using the Medallion Architecture model.

dbt Cloud is used to transform raw data into analytics-ready models across Bronze, Silver, and Gold layers. The final curated datasets power a Streamlit dashboard for interactive reporting and performance analysis.

This architecture ensures scalability, modularity, security, and cost-efficient compute utilization.

# Architecture 

```
┌─────────────────────────────────────────────────────────────┐
│                    EVERY HOUR (AUTOMATED)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ EventBridge Rule: healthcare-drive-sync-schedule            │
│ Triggers Lambda on schedule                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Lambda: healthcare-drive-to-s3-ingestion                    │
│ • Checks Google Drive for new/modified files                │
│ • Downloads 8 CSV types                                     │
│ • Uploads to S3 (date-partitioned)                          │
│ • Logs to DynamoDB (file + execution tracking)              │
│ • Triggers Step Functions                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step Functions: healthcare-data-pipeline-orchestrator       │
│                                                              │
│ State 1: DebounceCheck                                      │
│   → Checks if all 8 files present                           │
│   → If incomplete: loops every 30s                          │
│   → If complete: proceeds                                   │
│                                                              │
│ State 2: Wait30Seconds                                      │
│   → Safety wait for file write completion                   │
│                                                              │
│ State 3: TriggerSnowpipe                                    │
│   → Signals Snowpipe ready to load                          │
│   → Retry: 3 attempts with backoff                          │
│                                                              │
│ State 4: WaitForSnowpipeProcessing                          │
│   → Waits 60 seconds for Snowflake ingestion                │
│                                                              │
│ State 5: CheckSnowpipeStatus                                │
│   → Verifies load success                                   │
│                                                              │
│ State 6: SendSuccessNotification                            │
│   → Sends email: "Snowpipe complete, triggering dbt..."     │
│                                                              │
│ State 7: TriggerDbt                                         │
│   → Calls dbt Cloud API                                     │
│   → Starts transformation job                               │
│   → Retry: 2 attempts                                       │
│                                                              │
│ State 8: WaitForDbt                                         │
│   → Waits 5 minutes for dbt to complete                     │
│                                                              │
│ State 9: SendDbtCompleteNotification                        │
│   → Sends email: "Complete pipeline success!"               │
│                                                              │
│ State 10: PipelineSuccess                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Snowflake: Data Loaded                                      │
│ • RAW.HEALTHCARE (8 tables, 1.6M+ rows)                     │
│ • Auto-ingestion via Snowpipe                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ dbt Cloud: Data Transformation (triggered by Step Functions)│
│ • Runs 16 models (staging → intermediate → marts)           │
│ • Executes 50 data quality tests                            │
│ • Updates ANALYTICS.CORE schema                             │
│ • Duration: ~3-5 minutes                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Streamlit Dashboard: ANALYTICS.CORE                         │
│ • 6 interactive pages                                       │
│ • 14,814 facilities                                         │
│ • Real-time Snowflake connection                            │
│ • Fresh data automatically available                        │
└─────────────────────────────────────────────────────────────┘

```
## Technology Stack

### Cloud & Infrastructure

- AWS Lambda (serverless compute)
- AWS Step Functions (orchestration)
- AWS S3 (data lake)
- AWS EventBridge (scheduling)
- AWS SNS (notifications)
- AWS DynamoDB (state management)
- AWS Secrets Manager (credentials)
- AWS IAM (security)
- AWS CloudWatch (monitoring)

**Data & Analytics:**

- Snowflake (data warehouse)
- Medallion Architecture (Bronze → Silver → Gold layers)
- Snowpipe (auto-ingestion)
- dbt Cloud (transformations)
- Google Drive API (data source)

**Visualization & UI:**

- Streamlit (dashboard framework)
- Plotly (interactive charts)
- Python (data processing)

**Languages & Libraries:**

- Python 3.11
- SQL
- YAML (dbt config)
- JSON (AWS configs)
- Jinja (dbt templating)


# Phase 1 - 
# Google Drive APi setup

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/Google%20drive%20to%20AWS/Google%20Drive%20API.md

# AWS setup for Data Source Ingestion from Google Drive API

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/Google%20drive%20to%20AWS/AWS%20setup.md

# Lambda layer Package 

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/Google%20drive%20to%20AWS/google_layer.zip

# Connection test code 

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/Google%20drive%20to%20AWS/Lambda%20Test%20code.md

# Google Drive to S3 migration code

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/Google%20drive%20to%20AWS/Google%20drive%20to%20S3.md

# Result of first time transfer and readding file to check incremental strategy 

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/Google%20drive%20to%20AWS/Results.md

# Setup Event Processing

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/AWS-Snowflake%20Integration/Event%20Processing.md

# Setup DnamoDB

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/AWS-Snowflake%20Integration/DynamoDB.md

# Updated Lambda code

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/AWS-Snowflake%20Integration/Lambda%20Code.md

# setup Snowflake account

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/AWS-Snowflake%20Integration/Snowflake%20accounts%20setup.md

# Snowflake and S3 Integration 

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/AWS-Snowflake%20Integration/Snowflake%20and%20AWS%20setup.md

# Table Creation in Snowflake 

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/AWS-Snowflake%20Integration/snowflake%20tables%20creation.md

# Pipe Creation 

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/AWS-Snowflake%20Integration/Snowpipe%20for%20automated%20ingestion.md
