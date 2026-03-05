
# CREATE TABLES IN RAW.HEALTHCARE SCHEMA

Now we'll create 8 tables to hold healthcare data. Each table will match the structure of your CSV files.

# 1st table PBJ_Daily_Nurse_Staffing

``` sql

USE ROLE ACCOUNTADMIN;
USE DATABASE RAW;
USE SCHEMA HEALTHCARE;
USE WAREHOUSE LOADING_WH;

```


-- Create file format 

```sql

CREATE OR REPLACE FILE FORMAT Healthcare_pro
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  TRIM_SPACE = TRUE
  ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
  NULL_IF = ('NULL', 'null', '', 'NA', 'N/A')
  DATE_FORMAT = 'YYYYMMDD'
  TIMESTAMP_FORMAT = 'AUTO'
  ENCODING = 'UTF8'
  REPLACE_INVALID_CHARACTERS = TRUE;

```


##  PBJ_STAFFING table

``` sql

DROP TABLE IF EXISTS PBJ_STAFFING;


CREATE OR REPLACE TABLE PBJ_STAFFING (

  PROVNUM               STRING,
  PROVNAME              STRING,
  CITY                  STRING,
  STATE                 STRING,
  COUNTY_NAME           STRING,
  COUNTY_FIPS           STRING,
  CY_QTR                STRING,
  WORKDATE              DATE,
  MDSCENSUS             NUMBER(38,0),
  HRS_RNDON             FLOAT,
  HRS_RNDON_EMP         FLOAT,
  HRS_RNDON_CTR         FLOAT,
  HRS_RNADMIN           FLOAT,
  HRS_RNADMIN_EMP       FLOAT,
  HRS_RNADMIN_CTR       FLOAT,
  HRS_RN                FLOAT,
  HRS_RN_EMP            FLOAT,
  HRS_RN_CTR            FLOAT,
  HRS_LPNADMIN          FLOAT,
  HRS_LPNADMIN_EMP      FLOAT,
  HRS_LPNADMIN_CTR      FLOAT,
  HRS_LPN               FLOAT,
  HRS_LPN_EMP           FLOAT,
  HRS_LPN_CTR           FLOAT,
  HRS_CNA               FLOAT,
  HRS_CNA_EMP           FLOAT,
  HRS_CNA_CTR           FLOAT,
  HRS_NATRN             FLOAT,
  HRS_NATRN_EMP         FLOAT,
  HRS_NATRN_CTR         FLOAT,
  HRS_MEDAIDE           FLOAT,
  HRS_MEDAIDE_EMP       FLOAT,
  HRS_MEDAIDE_CTR       FLOAT,
  _LOAD_TIME            TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  _SOURCE_FILE          STRING,
  _LOAD_ID              STRING
);

--- Copy Data

-- Load data with metadata
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
    _SOURCE_FILE,
    _LOAD_ID
)
FROM (
    SELECT 
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
        $21, $22, $23, $24, $25, $26, $27, $28, $29, $30,
        $31, $32, $33,
        METADATA$FILENAME,
        TO_VARCHAR(METADATA$FILE_ROW_NUMBER)
    FROM @HEALTHCARE_S3_STAGE/
)
PATTERN = '.*load_dt=.*/PBJ_Daily_Nurse_Staffing.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_pro)
ON_ERROR = 'CONTINUE'
FORCE = FALSE;


-- Verify

SELECT COUNT(*) AS total_rows FROM PBJ_STAFFING;
SELECT * FROM PBJ_STAFFING LIMIT 10;

```

# 2nd Table VBP_Facility_Performance

```sql

DROP TABLE IF EXISTS VBP_PERFORMANCE;

CREATE OR REPLACE TABLE VBP_PERFORMANCE (
  -- Rankings
  SNF_VBP_PROGRAM_RANKING                             NUMBER(38,0),
  FOOTNOTE_SNF_VBP_PROGRAM_RANKING                    STRING,
  
  -- Facility Identifiers
  CCN                                                  STRING,
  PROVIDER_NAME                                        STRING,
  PROVIDER_ADDRESS                                     STRING,
  CITY_TOWN                                            STRING,
  STATE                                                STRING,
  ZIP_CODE                                             STRING,
  
  -- Baseline Period (FY 2019)
  BASELINE_PERIOD_FY2019_RSRR                          FLOAT,
  FOOTNOTE_BASELINE_PERIOD_FY2019_RSRR                STRING,
  
  -- Performance Period (FY 2022)
  PERFORMANCE_PERIOD_FY2022_RSRR                       FLOAT,
  FOOTNOTE_PERFORMANCE_PERIOD_FY2022_RSRR             STRING,
  
  -- Scores
  ACHIEVEMENT_SCORE                                    FLOAT,
  FOOTNOTE_ACHIEVEMENT_SCORE                          STRING,
  
  IMPROVEMENT_SCORE                                    FLOAT,
  FOOTNOTE_IMPROVEMENT_SCORE                          STRING,
  
  PERFORMANCE_SCORE                                    FLOAT,
  FOOTNOTE_PERFORMANCE_SCORE                          STRING,
  
  -- Payment Multiplier
  INCENTIVE_PAYMENT_MULTIPLIER                         FLOAT,
  FOOTNOTE_INCENTIVE_PAYMENT_MULTIPLIER               STRING,
  
  -- Metadata
  _LOAD_TIME                                           TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  _SOURCE_FILE                                         STRING,
  _LOAD_ID                                             STRING
) COMMENT = 'SNF Value-Based Purchasing Program Facility Performance - FY 2024';

-- ============================================================================
-- LOAD DATA
-- ============================================================================

COPY INTO VBP_PERFORMANCE (
    SNF_VBP_PROGRAM_RANKING,
    FOOTNOTE_SNF_VBP_PROGRAM_RANKING,
    CCN,
    PROVIDER_NAME,
    PROVIDER_ADDRESS,
    CITY_TOWN,
    STATE,
    ZIP_CODE,
    BASELINE_PERIOD_FY2019_RSRR,
    FOOTNOTE_BASELINE_PERIOD_FY2019_RSRR,
    PERFORMANCE_PERIOD_FY2022_RSRR,
    FOOTNOTE_PERFORMANCE_PERIOD_FY2022_RSRR,
    ACHIEVEMENT_SCORE,
    FOOTNOTE_ACHIEVEMENT_SCORE,
    IMPROVEMENT_SCORE,
    FOOTNOTE_IMPROVEMENT_SCORE,
    PERFORMANCE_SCORE,
    FOOTNOTE_PERFORMANCE_SCORE,
    INCENTIVE_PAYMENT_MULTIPLIER,
    FOOTNOTE_INCENTIVE_PAYMENT_MULTIPLIER,
    _SOURCE_FILE,
    _LOAD_ID
)
FROM (
    SELECT 
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
        METADATA$FILENAME,
        TO_VARCHAR(METADATA$FILE_ROW_NUMBER)
    FROM @HEALTHCARE_S3_STAGE/
)
PATTERN = '.*load_dt=.*/FY_.*_SNF_VBP_Facility_Performance\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_pro)
ON_ERROR = 'CONTINUE'
FORCE = FALSE;

-- Verify
SELECT COUNT(*) AS total_rows FROM VBP_PERFORMANCE;
SELECT * FROM VBP_PERFORMANCE LIMIT 10;

-- Check metadata populated
SELECT 
    COUNT(*) AS total_rows,
    COUNT(_SOURCE_FILE) AS has_source_file,
    COUNT(_LOAD_ID) AS has_load_id
FROM VBP_PERFORMANCE;

```


