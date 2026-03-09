# Pipe Creation and Configure S3 Event Notification

```sql

USE ROLE ACCOUNTADMIN;
USE DATABASE RAW;
USE SCHEMA HEALTHCARE;

DROP PIPE IF EXISTS PBJ_STAFFING_PIPE;
DROP PIPE IF EXISTS VBP_PERFORMANCE_PIPE;
DROP PIPE IF EXISTS STATE_AVERAGES_PIPE;
DROP PIPE IF EXISTS QUALITY_CLAIMS_PIPE;
DROP PIPE IF EXISTS PENALTIES_PIPE;
DROP PIPE IF EXISTS PROVIDER_INFO_PIPE;
DROP PIPE IF EXISTS SURVEY_SUMMARY_PIPE;
DROP PIPE IF EXISTS OWNERSHIP_PIPE;

```

## Auto-ingest PBJ staffing data from S3

```sql

CREATE OR REPLACE PIPE PBJ_STAFFING_PIPE
  AUTO_INGEST = TRUE
  COMMENT = 'Auto-ingest PBJ staffing data from S3'
AS
COPY INTO PBJ_STAFFING (
    PROVNUM, PROVNAME, CITY, STATE, COUNTY_NAME, COUNTY_FIPS,
    CY_QTR, WORKDATE, MDSCENSUS,
    HRS_RNDON, HRS_RNDON_EMP, HRS_RNDON_CTR,
    HRS_RNADMIN, HRS_RNADMIN_EMP, HRS_RNADMIN_CTR,
    HRS_RN, HRS_RN_EMP, HRS_RN_CTR,
    HRS_LPNADMIN, HRS_LPNADMIN_EMP, HRS_LPNADMIN_CTR,
    HRS_LPN, HRS_LPN_EMP, HRS_LPN_CTR,
    HRS_CNA, HRS_CNA_EMP, HRS_CNA_CTR,
    HRS_NATRN, HRS_NATRN_EMP, HRS_NATRN_CTR,
    HRS_MEDAIDE, HRS_MEDAIDE_EMP, HRS_MEDAIDE_CTR,
    _SOURCE_FILE, _LOAD_ID
)
FROM (
    SELECT 
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
        $21, $22, $23, $24, $25, $26, $27, $28, $29, $30,
        $31, $32, $33,
        METADATA$FILENAME,
        TO_VARCHAR(CONCAT(METADATA$FILENAME,'_',METADATA$FILE_ROW_NUMBER))
    FROM @HEALTHCARE_S3_STAGE/
)
PATTERN = '.*load_dt=.*/PBJ_Daily_Nurse_Staffing.*\.csv'
FILE_FORMAT = (FORMAT_NAME = healthcare_pro);


DESC PIPE PBJ_STAFFING_PIPE;

```


## Auto-ingest VBP_PERFORMANCE data from S3


```sql

CREATE OR REPLACE PIPE VBP_PERFORMANCE_PIPE AUTO_INGEST = TRUE
AS COPY INTO VBP_PERFORMANCE (
    SNF_VBP_PROGRAM_RANKING, FOOTNOTE_SNF_VBP_PROGRAM_RANKING,
    CCN, PROVIDER_NAME, PROVIDER_ADDRESS, CITY_TOWN, STATE, ZIP_CODE,
    BASELINE_PERIOD_FY2019_RSRR, FOOTNOTE_BASELINE_PERIOD_FY2019_RSRR,
    PERFORMANCE_PERIOD_FY2022_RSRR, FOOTNOTE_PERFORMANCE_PERIOD_FY2022_RSRR,
    ACHIEVEMENT_SCORE, FOOTNOTE_ACHIEVEMENT_SCORE,
    IMPROVEMENT_SCORE, FOOTNOTE_IMPROVEMENT_SCORE,
    PERFORMANCE_SCORE, FOOTNOTE_PERFORMANCE_SCORE,
    INCENTIVE_PAYMENT_MULTIPLIER, FOOTNOTE_INCENTIVE_PAYMENT_MULTIPLIER,
    _SOURCE_FILE, _LOAD_ID
)
FROM (SELECT $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,
      METADATA$FILENAME, TO_VARCHAR(METADATA$FILE_ROW_NUMBER) FROM @HEALTHCARE_S3_STAGE/)
PATTERN = '.*load_dt=.*/FY_.*_SNF_VBP_Facility_Performance\.csv'
FILE_FORMAT = (FORMAT_NAME = VBP_FORMAT);

```

## all other pipe

```sql


CREATE OR REPLACE PIPE STATE_AVERAGES_PIPE AUTO_INGEST = TRUE
AS COPY INTO STATE_AVERAGES
FROM @HEALTHCARE_S3_STAGE/
PATTERN = '.*load_dt=.*/NH_StateUSAverages.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_General_Format)
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE PIPE QUALITY_CLAIMS_PIPE AUTO_INGEST = TRUE
AS COPY INTO QUALITY_CLAIMS
FROM @HEALTHCARE_S3_STAGE/
PATTERN = '.*load_dt=.*/NH_QualityMsr_Claims.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_General_Format)
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE PIPE PENALTIES_PIPE AUTO_INGEST = TRUE
AS COPY INTO PENALTIES
FROM @HEALTHCARE_S3_STAGE/
PATTERN = '.*load_dt=.*/NH_Penalties.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_General_Format)
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE PIPE PROVIDER_INFO_PIPE AUTO_INGEST = TRUE
AS COPY INTO PROVIDER_INFO
FROM @HEALTHCARE_S3_STAGE/
PATTERN = '.*load_dt=.*/NH_ProviderInfo.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_General_Format)
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE PIPE SURVEY_SUMMARY_PIPE AUTO_INGEST = TRUE
AS COPY INTO SURVEY_SUMMARY
FROM @HEALTHCARE_S3_STAGE/
PATTERN = '.*load_dt=.*/NH_SurveySummary.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_General_Format)
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE PIPE OWNERSHIP_PIPE AUTO_INGEST = TRUE
AS COPY INTO OWNERSHIP
FROM @HEALTHCARE_S3_STAGE/
PATTERN = '.*load_dt=.*/NH_Ownership.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_General_Format)
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

```

## show all pipe

```sql

SHOW PIPES IN SCHEMA RAW.HEALTHCARE;

```

## - Configure S3 Event Notification

**Go to AWS S3 Console:**

1. Open bucket: `healthcare-metrics-project-at`
2. Go to **Properties** tab
3. Scroll to **Event notifications** section
4. Click **Create event notification**

**Configuration:**

- **Event name:** `snowpipe-auto-ingest`
- **Event types:**
  -  Check: **All object create events** (s3:ObjectCreated:*)
- **Prefix (optional):** `landing/google_drive/`
- **Suffix (optional):** `.csv`
- **Destination:**
  - Select: **SQS queue**
  - Select: **Enter SQS queue ARN**
  - **Paste the SQS ARN from Snowflake** (from DESC PIPE output)
  - Click Save
  
  Example:
```
  arn:aws:sqs:us-east-1:123456789012:sf-snowpipe-AIDAI5Q6...
```
## STEP 6.18: STORE SNOWFLAKE CREDENTIALS IN AWS SECRETS MANAGER

### Create the Secret in AWS Console

- Go to AWS Secrets Manager:
- Open AWS Console
- Search for "Secrets Manager"
- Click "Store a new secret"

- Configure Secret Type
 - Step 1: Choose secret type
 - Select: "Other type of secret"
 - Click "Key/value" tab

```
Enter these key-value pairs:
Key                  Value
account            Your Snowflake account
user               HEALTHCARE_PIPELINE_USER
Rpassword              Your user password
warehouse               LOADING_WH
database                 RAW
schema                HEALTHCAREHEALTHCARE
role                  HEALTHCARE_PIPELINE_ROLE

Or use JSON format (click "Plaintext" tab):
json{
  "account": "ABC12345.us-east-1.aws",
  "user": "HEALTHCARE_PIPELINE_USER",
  "password": "YOUR_SECURE_PASSWORD_HERE",
  "warehouse": "LOADING_WH",
  "database": "RAW",
  "schema": "HEALTHCARE",
  "role": "HEALTHCARE_PIPELINE_ROLE"
}

```
** IMPORTANT: Replace with your actual values! **

 - Name the Secret
   - Step 2: Configure secret

- Secret name: snowflake/healthcare/credentials
- Description: Snowflake credentials for healthcare data pipeline
- Encryption key: Default (AWS managed key)

- Click Next

- Configure Rotation (Optional)
 - Step 3: Configure rotation

- Disable automatic rotation (for now)
- Click Next
- Review and Store
-  Review

- Review all settings
- Click Store


## Testing if you want to check all Pipe line ( not recommanded manually)

## PBJ_STAFFING_PIPE

```sql


# Copy existing file to new partition
aws s3 cp \
  s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-25/PBJ_Daily_Nurse_Staffing_Q2_2024.csv \
  s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-03-05/PBJ_Daily_Nurse_Staffing_Q2_2024.csv

-- Refresh pipe manually (loads any files it missed)
ALTER PIPE PBJ_STAFFING_PIPE REFRESH;

-- Check pipe status
SELECT SYSTEM$PIPE_STATUS('PBJ_STAFFING_PIPE');

-- View pipe history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'PBJ_STAFFING',
    START_TIME => DATEADD(hours, -1, CURRENT_TIMESTAMP())
));

```


##  VBP_PERFORMANCE

```sql

# Use aws cmd

aws s3 cp \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-25/FY_2024_SNF_VBP_Facility_Performance.csv \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-03-05/FY_2024_SNF_VBP_Facility_Performance.csv


-- Refresh pipe manually (loads any files it missed)
ALTER PIPE VBP_PERFORMANCE_PIPE REFRESH;

-- Check pipe status
SELECT SYSTEM$PIPE_STATUS('VBP_PERFORMANCE_PIPE');

-- View pipe history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'VBP_PERFORMANCE',
    START_TIME => DATEADD(hours, -1, CURRENT_TIMESTAMP())
```

## STATE_AVERAGES

```sql
# Use aws cmd

aws s3 cp \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-25/NH_StateUSAverages_Oct2024.csv \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-03-05/NH_StateUSAverages_Oct2024.csv


-- Refresh pipe manually (loads any files it missed)
ALTER PIPE STATE_AVERAGES_PIPE REFRESH;

-- Check pipe status
SELECT SYSTEM$PIPE_STATUS('STATE_AVERAGES_PIPE');

-- View pipe history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'STATE_AVERAGES',
    START_TIME => DATEADD(hours, -1, CURRENT_TIMESTAMP())

```

## QUALITY_CLAIMS

```sql
# Use aws cmd

aws s3 cp \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-25/NH_Penalties_Oct2024.csv \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-03-05/NH_Penalties_Oct2024.csv



-- Refresh pipe manually (loads any files it missed)
ALTER PIPE QUALITY_CLAIMS_PIPE REFRESH;

-- Check pipe status
SELECT SYSTEM$PIPE_STATUS('QUALITY_CLAIMS_PIPE');

-- View pipe history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'QUALITY_CLAIMS',
    START_TIME => DATEADD(hours, -1, CURRENT_TIMESTAMP())

```


## PENALTIES

```sql
# Use aws cmd

aws s3 cp \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-25/NH_Penalties_Oct2024.csv \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-03-05/NH_Penalties_Oct2024.csv


-- Refresh pipe manually (loads any files it missed)
ALTER PIPE PENALTIES_PIPE REFRESH;

-- Check pipe status
SELECT SYSTEM$PIPE_STATUS('PENALTIES_PIPE');

-- View pipe history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'PENALTIES',
    START_TIME => DATEADD(hours, -1, CURRENT_TIMESTAMP())

```

## PROVIDER_INFO

```sql
# Use aws cmd

aws s3 cp \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-25/NH_ProviderInfo_Oct2024.csv \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-03-05/NH_ProviderInfo_Oct2024.csv

-- Refresh pipe manually (loads any files it missed)
ALTER PIPE PROVIDER_INFO_PIPE REFRESH;

-- Check pipe status
SELECT SYSTEM$PIPE_STATUS('PROVIDER_INFO_PIPE');

-- View pipe history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'PROVIDER_INFO',
    START_TIME => DATEADD(hours, -1, CURRENT_TIMESTAMP())

```


## SURVEY_SUMMARY

```sql
# Use aws cmd

aws s3 cp \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-25/NH_SurveySummary_Oct2024.csv \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-03-05/NH_SurveySummary_Oct2024.csv

-- Refresh pipe manually (loads any files it missed)
ALTER PIPE SURVEY_SUMMARY_PIPE REFRESH;

-- Check pipe status
SELECT SYSTEM$PIPE_STATUS('SURVEY_SUMMARY_PIPE');

-- View pipe history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'SURVEY_SUMMARY',
    START_TIME => DATEADD(hours, -1, CURRENT_TIMESTAMP())

```


## OWNERSHIP

```sql
# Use aws cmd

aws s3 cp \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-25/NH_Ownership_Oct2024.csv \
s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-03-05/NH_Ownership_Oct2024.csv

-- Refresh pipe manually (loads any files it missed)
ALTER PIPE OWNERSHIP_PIPE REFRESH;

-- Check pipe status
SELECT SYSTEM$PIPE_STATUS('OWNERSHIP_PIPE');

-- View pipe history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'OWNERSHIP',
    START_TIME => DATEADD(hours, -1, CURRENT_TIMESTAMP())

```
