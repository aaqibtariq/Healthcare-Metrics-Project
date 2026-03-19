
```

Google Drive (14,814 facility files)
    ↓
Lambda: healthcare-drive-to-s3-ingestion
    ├─ Downloads from Google Drive
    ├─ Uploads to S3
    ├─ Logs to DynamoDB
    └─  Triggers Step Functions
        ↓
Step Functions: healthcare-data-pipeline-orchestrator
    ├─ DebounceCheck (waits for all files)
    ├─ TriggerSnowpipe (signals ready)
    ├─ CheckSnowpipeStatus (verifies)
    └─ SendNotification (emails you)
        ↓
Snowflake: RAW.HEALTHCARE (8 tables)
    ↓
dbt Cloud: 16 models, 50 tests
    ↓
Streamlit Dashboard: 6 pages, 14,814 facilities

```

##  Step Function Flow

<p align="center">
  <img src="https://raw.githubusercontent.com/aaqibtariq/Healthcare-Metrics-Project/main/Step%20Function/image%20-%202026-03-19T115513.520.png" width="700"/>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/aaqibtariq/Healthcare-Metrics-Project/main/Step%20Function/image%20-%202026-03-19T115426.220.png" width="700"/>
</p>
