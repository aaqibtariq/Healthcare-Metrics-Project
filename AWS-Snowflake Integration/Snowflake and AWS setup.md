#  Create IAM Policy for S3 Access

- Click "Create policy" (opens in new tab)
- Switch to JSON tab and paste

 ```sql
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SnowflakeS3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::healthcare-metrics-project-at",
        "arn:aws:s3:::healthcare-metrics-project-at/landing/google_drive/*"
      ]
    }
  ]
}

**What this allows:**
- Read files from your S3 bucket
- List files in the bucket
- Get bucket location info
- **Does NOT allow:** Write, delete, or modify

```
- Name the Policy
- Policy name: SnowflakeS3ReadAccessPolicy
- Description: Allows Snowflake to read healthcare data from S3 landing zone
- Click **"Create policy"**


  

# CREATE AWS IAM ROLE FOR SNOWFLAKE

- Go to AWS Console
- Search for **IAM**
- Click **"Roles"** in left sidebar
- Click **"Create role"**
- Trusted entity type: AWS account
- An AWS account: Another AWS account
- Account ID: 123456789012
**For now, use a placeholder. We'll update this after we get Snowflake's account ID.**
- Attach Policy to Role
- Search for: SnowflakeS3ReadAccessPolicy
- Check the checkbox
- Click **"Next"**
- Role name: SnowflakeAccessRole
- Description: Allows Snowflake to access healthcare data in S3
- **Tags (optional):**
- Key: Project
- Value: HealthcareMetrics
- Click **"Create role"**
  

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

**Look for these two properties in the output:**

STORAGE_AWS_IAM_USER_ARN
STORAGE_AWS_EXTERNAL_ID
```

##  Update the AWS IAM role to trust Snowflake's AWS user

- IAM Console → Roles
- Click on "SnowflakeAccessRole"
- Click "Trust relationships" tab
- Click "Edit trust policy"
- Update Trust Policy

```json

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::Paste your value"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "Paste your value"
        }
      }
    }
  ]
}

*** This tells AWS IAM: "Allow this specific Snowflake user to assume this role, but only if they provide the correct external ID"***
```
- Click "Update policy"

## Verify Snowflake can access your S3 bucket

Grant Integration Usage to Pipeline Role

```sql

-- Grant usage of the integration
GRANT USAGE ON INTEGRATION HEALTHCARE_S3_INTEGRATION TO ROLE HEALTHCARE_PIPELINE_ROL

```


### Create External Stage

```sql

USE ROLE ACCOUNTADMIN;
USE DATABASE RAW;
USE SCHEMA HEALTHCARE;

-- Create external stage pointing to S3
CREATE OR REPLACE STAGE HEALTHCARE_S3_STAGE
  URL = 's3://healthcare-metrics-project-at/landing/google_drive/'
  STORAGE_INTEGRATION = HEALTHCARE_S3_INTEGRATION
  FILE_FORMAT = (
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    TRIM_SPACE = TRUE
    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
    NULL_IF = ('NULL', 'null', '')
  )
  COMMENT = 'External stage for healthcare CSV files from S3';

```

#### Test Stage by Listing Files

```sql

-- List files in the stage (should show your S3 files)
LIST @HEALTHCARE_S3_STAGE;


**Expected output:**
You should see a list of files like:

s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2024-02-25/PBJ_Daily_Nurse_Staffing_Q2_2024.csv
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2024-02-25/NH_ProviderInfo_Oct2024.csv

```




