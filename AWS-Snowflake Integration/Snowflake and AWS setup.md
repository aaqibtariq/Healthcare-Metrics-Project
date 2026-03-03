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


  

# CREATE AWS IAM ROLE FOR SNOWFLAK

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
```
