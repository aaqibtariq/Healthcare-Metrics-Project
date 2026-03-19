
##  Healthcare Pipeline – Architecture & Monitoring

---

###  Google Drive → S3 Ingestion

<p align="center">
  <img src="https://raw.githubusercontent.com/aaqibtariq/Healthcare-Metrics-Project/main/All%20Phases/Reference%20files/Google%20drive%20to%20S3.png" width="750"/>
</p>

**Description:**
- Data is sourced from Google Drive and ingested into AWS S3
- Acts as the entry point of the pipeline
- Ensures centralized storage for downstream processing

---

###  S3 Storage Layer

<p align="center">
  <img src="https://raw.githubusercontent.com/aaqibtariq/Healthcare-Metrics-Project/main/All%20Phases/Reference%20files/S3.jpg" width="750"/>
</p>

**Description:**
- S3 serves as the raw data lake
- Stores incoming healthcare datasets
- Supports scalable and durable storage
- Enables event-driven processing

---

###  S3 State Monitoring

<p align="center">
  <img src="https://raw.githubusercontent.com/aaqibtariq/Healthcare-Metrics-Project/main/All%20Phases/Reference%20files/S3%20state%20monitoring%20.png" width="750"/>
</p>

**Description:**
- Tracks file-level ingestion status in S3
- Monitors processing stages (uploaded, processed, failed)
- Helps ensure no data loss or duplication

---

###  DynamoDB – File Ingestion State

<p align="center">
  <img src="https://raw.githubusercontent.com/aaqibtariq/Healthcare-Metrics-Project/main/All%20Phases/Reference%20files/dynamoDB%20healthcare_file_ingestion_state.png" width="750"/>
</p>

**Description:**
- Stores metadata for each ingested file
- Tracks ingestion status and timestamps
- Prevents duplicate processing
- Acts as a checkpoint system

---

###  DynamoDB – Pipeline Execution State

<p align="center">
  <img src="https://raw.githubusercontent.com/aaqibtariq/Healthcare-Metrics-Project/main/All%20Phases/Reference%20files/DynamoDB%20healthcare_pipeline_execution_state.png" width="750"/>
</p>

**Description:**
- Tracks overall pipeline execution status
- Maintains step-level progress (e.g., ingestion, transformation)
- Supports recovery and reprocessing logic
- Enables audit and monitoring capabilities

---

###  CloudWatch Monitoring

<p align="center">
  <img src="https://raw.githubusercontent.com/aaqibtariq/Healthcare-Metrics-Project/main/All%20Phases/Reference%20files/cloudwatch.png" width="750"/>
</p>

**Description:**
- Centralized logging and monitoring system
- Tracks Lambda, Step Functions, and pipeline logs
- Enables alerting for failures and anomalies
- Supports operational visibility

---
