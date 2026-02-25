# Healthcare-Metrics-Project

## Core Objective

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


## Technology Stack

### Cloud & Infrastructure

-  AWS Lambda (serverless ingestion)

-  AWS S3 (data lake / landing zone)

-  AWS IAM (role-based access control)

-  AWS Secrets Manager (secure credential management)

-  AWS EventBridge (event-driven orchestration)

### Data Warehouse

-  Snowflake (cloud data warehouse)

-  Medallion Architecture (Bronze → Silver → Gold layers)

-  Snowpipe / COPY INTO (data ingestion from S3)

### Transformation

-  dbt Cloud (data transformation & testing)

-  SQL (analytics modeling)

-  Analytics & Visualization

-  Streamlit (interactive dashboard)

-  Plotly (data visualization)

### Programming & APIs

-  Python (AWS Lambda & API integration)

-  Google Drive API (data source ingestion)

-   dbt Cloud REST API (job orchestration)


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
