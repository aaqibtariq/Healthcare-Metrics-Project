
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
