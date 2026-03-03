# CREATE S3 INTEGRATION

```sql

-- Use ACCOUNTADMIN role (required for creating integrations)
USE ROLE ACCOUNTADMIN;

-- Create S3 integration
CREATE STORAGE INTEGRATION IF NOT EXISTS HEALTHCARE_S3_INTEGRATION
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::YOUR_AWS_ACCOUNT_ID:role/SnowflakeAccessRole'
  STORAGE_ALLOWED_LOCATIONS = ('s3://healthcare-metrics-project-at/landing/google_drive/')
  COMMENT = 'Integration for healthcare data from S3';

```
## Get Snowflake AWS Account Info

```sql
 -- Describe the integration to get Snowflake's AWS info
DESC INTEGRATION HEALTHCARE_S3_INTEGRATION;
```
