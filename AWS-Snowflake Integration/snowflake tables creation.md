
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
  NULL_IF = ('NULL', 'null', '', 'NA', 'N/A', '---')
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
        TO_VARCHAR(CONCAT(METADATA$FILENAME,'_',METADATA$FILE_ROW_NUMBER))
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
        TO_VARCHAR(CONCAT(METADATA$FILENAME,'_',METADATA$FILE_ROW_NUMBER))
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

# 3rd Table STATE_AVERAGES

```sql

-- ============================================================================
-- TABLE 3: STATE_AVERAGES
-- State and National Average Quality Metrics
-- File: NH_StateUSAverages_Oct2024.csv
-- Rows: ~54 (50 states + DC + territories + national average)
-- ============================================================================

DROP TABLE IF EXISTS STATE_AVERAGES;

CREATE OR REPLACE TABLE STATE_AVERAGES (
  -- Identifier
  STATE_OR_NATION                                                       STRING,
  
  -- Deficiencies by Cycle
  CYCLE_1_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES                          FLOAT,
  CYCLE_1_TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES                     FLOAT,
  CYCLE_2_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES                          FLOAT,
  CYCLE_2_TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES                     FLOAT,
  CYCLE_3_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES                          FLOAT,
  CYCLE_3_TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES                     FLOAT,
  
  -- Census & Staffing
  AVERAGE_NUMBER_OF_RESIDENTS_PER_DAY                                  FLOAT,
  REPORTED_NURSE_AIDE_STAFFING_HOURS_PER_RESIDENT_PER_DAY             FLOAT,
  REPORTED_LPN_STAFFING_HOURS_PER_RESIDENT_PER_DAY                    FLOAT,
  REPORTED_RN_STAFFING_HOURS_PER_RESIDENT_PER_DAY                     FLOAT,
  REPORTED_LICENSED_STAFFING_HOURS_PER_RESIDENT_PER_DAY               FLOAT,
  REPORTED_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY            FLOAT,
  TOTAL_NUMBER_OF_NURSE_STAFF_HOURS_PER_RESIDENT_PER_DAY_ON_WEEKEND   FLOAT,
  REGISTERED_NURSE_HOURS_PER_RESIDENT_PER_DAY_ON_WEEKEND              FLOAT,
  REPORTED_PHYSICAL_THERAPIST_STAFFING_HOURS_PER_RESIDENT_PER_DAY     FLOAT,
  
  -- Turnover
  TOTAL_NURSING_STAFF_TURNOVER                                         FLOAT,
  REGISTERED_NURSE_TURNOVER                                            FLOAT,
  NUMBER_OF_ADMINISTRATORS_WHO_HAVE_LEFT_THE_NURSING_HOME             FLOAT,
  
  -- Case-Mix
  NURSING_CASE_MIX_INDEX                                               FLOAT,
  CASE_MIX_RN_STAFFING_HOURS_PER_RESIDENT_PER_DAY                     FLOAT,
  CASE_MIX_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY            FLOAT,
  CASE_MIX_WEEKEND_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY    FLOAT,
  
  -- Penalties
  NUMBER_OF_FINES                                                      FLOAT,
  FINE_AMOUNT_IN_DOLLARS                                               FLOAT,
  
  -- Quality Measures - Long Stay
  PCT_LONG_STAY_RESIDENTS_NEED_FOR_HELP_WITH_DAILY_ACTIVITIES_INCREASED  FLOAT,
  PCT_LONG_STAY_RESIDENTS_WHO_LOSE_TOO_MUCH_WEIGHT                    FLOAT,
  PCT_LOW_RISK_LONG_STAY_RESIDENTS_WHO_LOSE_CONTROL_BOWELS_BLADDER    FLOAT,
  PCT_LONG_STAY_RESIDENTS_WITH_CATHETER_INSERTED_LEFT_IN_BLADDER      FLOAT,
  PCT_LONG_STAY_RESIDENTS_WITH_URINARY_TRACT_INFECTION                FLOAT,
  PCT_LONG_STAY_RESIDENTS_WHO_HAVE_DEPRESSIVE_SYMPTOMS                FLOAT,
  PCT_LONG_STAY_RESIDENTS_WHO_WERE_PHYSICALLY_RESTRAINED              FLOAT,
  PCT_LONG_STAY_RESIDENTS_EXPERIENCING_ONE_OR_MORE_FALLS_MAJOR_INJURY FLOAT,
  PCT_LONG_STAY_RESIDENTS_ASSESSED_APPROPRIATELY_GIVEN_PNEUMOCOCCAL_VACCINE  FLOAT,
  PCT_LONG_STAY_RESIDENTS_WHO_RECEIVED_ANTIPSYCHOTIC_MEDICATION       FLOAT,
  PCT_LONG_STAY_RESIDENTS_ABILITY_TO_MOVE_INDEPENDENTLY_WORSENED      FLOAT,
  PCT_LONG_STAY_RESIDENTS_WHO_RECEIVED_ANTIANXIETY_HYPNOTIC_MEDICATION  FLOAT,
  PCT_HIGH_RISK_LONG_STAY_RESIDENTS_WITH_PRESSURE_ULCERS              FLOAT,
  PCT_LONG_STAY_RESIDENTS_ASSESSED_APPROPRIATELY_GIVEN_SEASONAL_INFLUENZA_VACCINE  FLOAT,
  
  -- Quality Measures - Short Stay
  PCT_SHORT_STAY_RESIDENTS_ASSESSED_APPROPRIATELY_GIVEN_PNEUMOCOCCAL_VACCINE  FLOAT,
  PCT_SHORT_STAY_RESIDENTS_WHO_NEWLY_RECEIVED_ANTIPSYCHOTIC_MEDICATION  FLOAT,
  PCT_SHORT_STAY_RESIDENTS_WHO_MADE_IMPROVEMENTS_IN_FUNCTION          FLOAT,
  PCT_SHORT_STAY_RESIDENTS_ASSESSED_APPROPRIATELY_GIVEN_SEASONAL_INFLUENZA_VACCINE  FLOAT,
  PCT_SHORT_STAY_RESIDENTS_WHO_WERE_REHOSPITALIZED_AFTER_NH_ADMISSION  FLOAT,
  PCT_SHORT_STAY_RESIDENTS_WHO_HAD_OUTPATIENT_EMERGENCY_DEPARTMENT_VISIT  FLOAT,
  
  -- Hospitalization Rates
  NUMBER_OF_HOSPITALIZATIONS_PER_1000_LONG_STAY_RESIDENT_DAYS         FLOAT,
  NUMBER_OF_OUTPATIENT_EMERGENCY_DEPARTMENT_VISITS_PER_1000_LONG_STAY_RESIDENT_DAYS  FLOAT,
  
  -- Processing Date
  PROCESSING_DATE                                                      DATE,
  
  -- Metadata
  _LOAD_TIME                                                           TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  _SOURCE_FILE                                                         STRING,
  _LOAD_ID                                                             STRING
) COMMENT = 'State and national average quality and staffing metrics';

-- ============================================================================
-- LOAD DATA
-- ============================================================================

COPY INTO STATE_AVERAGES (
    STATE_OR_NATION,
    CYCLE_1_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES,
    CYCLE_1_TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES,
    CYCLE_2_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES,
    CYCLE_2_TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES,
    CYCLE_3_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES,
    CYCLE_3_TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES,
    AVERAGE_NUMBER_OF_RESIDENTS_PER_DAY,
    REPORTED_NURSE_AIDE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    REPORTED_LPN_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    REPORTED_RN_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    REPORTED_LICENSED_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    REPORTED_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    TOTAL_NUMBER_OF_NURSE_STAFF_HOURS_PER_RESIDENT_PER_DAY_ON_WEEKEND,
    REGISTERED_NURSE_HOURS_PER_RESIDENT_PER_DAY_ON_WEEKEND,
    REPORTED_PHYSICAL_THERAPIST_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    TOTAL_NURSING_STAFF_TURNOVER,
    REGISTERED_NURSE_TURNOVER,
    NUMBER_OF_ADMINISTRATORS_WHO_HAVE_LEFT_THE_NURSING_HOME,
    NURSING_CASE_MIX_INDEX,
    CASE_MIX_RN_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    CASE_MIX_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    CASE_MIX_WEEKEND_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    NUMBER_OF_FINES,
    FINE_AMOUNT_IN_DOLLARS,
    PCT_LONG_STAY_RESIDENTS_NEED_FOR_HELP_WITH_DAILY_ACTIVITIES_INCREASED,
    PCT_LONG_STAY_RESIDENTS_WHO_LOSE_TOO_MUCH_WEIGHT,
    PCT_LOW_RISK_LONG_STAY_RESIDENTS_WHO_LOSE_CONTROL_BOWELS_BLADDER,
    PCT_LONG_STAY_RESIDENTS_WITH_CATHETER_INSERTED_LEFT_IN_BLADDER,
    PCT_LONG_STAY_RESIDENTS_WITH_URINARY_TRACT_INFECTION,
    PCT_LONG_STAY_RESIDENTS_WHO_HAVE_DEPRESSIVE_SYMPTOMS,
    PCT_LONG_STAY_RESIDENTS_WHO_WERE_PHYSICALLY_RESTRAINED,
    PCT_LONG_STAY_RESIDENTS_EXPERIENCING_ONE_OR_MORE_FALLS_MAJOR_INJURY,
    PCT_LONG_STAY_RESIDENTS_ASSESSED_APPROPRIATELY_GIVEN_PNEUMOCOCCAL_VACCINE,
    PCT_LONG_STAY_RESIDENTS_WHO_RECEIVED_ANTIPSYCHOTIC_MEDICATION,
    PCT_LONG_STAY_RESIDENTS_ABILITY_TO_MOVE_INDEPENDENTLY_WORSENED,
    PCT_LONG_STAY_RESIDENTS_WHO_RECEIVED_ANTIANXIETY_HYPNOTIC_MEDICATION,
    PCT_HIGH_RISK_LONG_STAY_RESIDENTS_WITH_PRESSURE_ULCERS,
    PCT_LONG_STAY_RESIDENTS_ASSESSED_APPROPRIATELY_GIVEN_SEASONAL_INFLUENZA_VACCINE,
    PCT_SHORT_STAY_RESIDENTS_ASSESSED_APPROPRIATELY_GIVEN_PNEUMOCOCCAL_VACCINE,
    PCT_SHORT_STAY_RESIDENTS_WHO_NEWLY_RECEIVED_ANTIPSYCHOTIC_MEDICATION,
    PCT_SHORT_STAY_RESIDENTS_WHO_MADE_IMPROVEMENTS_IN_FUNCTION,
    PCT_SHORT_STAY_RESIDENTS_ASSESSED_APPROPRIATELY_GIVEN_SEASONAL_INFLUENZA_VACCINE,
    PCT_SHORT_STAY_RESIDENTS_WHO_WERE_REHOSPITALIZED_AFTER_NH_ADMISSION,
    PCT_SHORT_STAY_RESIDENTS_WHO_HAD_OUTPATIENT_EMERGENCY_DEPARTMENT_VISIT,
    NUMBER_OF_HOSPITALIZATIONS_PER_1000_LONG_STAY_RESIDENT_DAYS,
    NUMBER_OF_OUTPATIENT_EMERGENCY_DEPARTMENT_VISITS_PER_1000_LONG_STAY_RESIDENT_DAYS,
    PROCESSING_DATE,
    _SOURCE_FILE,
    _LOAD_ID
)
FROM (
    SELECT 
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
        $21, $22, $23, $24, $25, $26, $27, $28, $29, $30,
        $31, $32, $33, $34, $35, $36, $37, $38, $39, $40,
        $41, $42, $43, $44, $45, $46, $47, $48,
        METADATA$FILENAME,
        TO_VARCHAR(CONCAT(METADATA$FILENAME,'_',METADATA$FILE_ROW_NUMBER))
    FROM @HEALTHCARE_S3_STAGE/
)
PATTERN = '.*load_dt=.*/NH_StateUSAverages.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_pro)
ON_ERROR = 'CONTINUE'
Force = FALSE;


-- Verify
SELECT COUNT(*) AS total_rows FROM STATE_AVERAGES;
SELECT * FROM STATE_AVERAGES LIMIT 10;

-- Check specific states
SELECT STATE_OR_NATION, 
       REPORTED_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
       TOTAL_NURSING_STAFF_TURNOVER,
       _SOURCE_FILE
FROM STATE_AVERAGES 
WHERE STATE_OR_NATION IN ('NATION', 'CA', 'NY', 'TX', 'FL')
ORDER BY STATE_OR_NATION;

```

# 4th table QUALITY_CLAIMS

```sql

-- ============================================================================
-- TABLE 4: QUALITY_CLAIMS
-- Claims-Based Quality Measures
-- File: NH_QualityMsr_Claims_Oct2024.csv
-- Rows: ~59,258
-- ============================================================================

DROP TABLE IF EXISTS QUALITY_CLAIMS;

CREATE OR REPLACE TABLE QUALITY_CLAIMS (
  -- Facility Identifiers
  CCN                                    STRING,
  PROVIDER_NAME                          STRING,
  PROVIDER_ADDRESS                       STRING,
  CITY_TOWN                              STRING,
  STATE                                  STRING,
  ZIP_CODE                               STRING,
  
  -- Measure Information
  MEASURE_CODE                           NUMBER(38,0),
  MEASURE_DESCRIPTION                    STRING,
  RESIDENT_TYPE                          STRING,
  
  -- Scores
  ADJUSTED_SCORE                         FLOAT,
  OBSERVED_SCORE                         FLOAT,
  EXPECTED_SCORE                         FLOAT,
  FOOTNOTE_FOR_SCORE                     STRING,
  
  -- Quality Rating Info
  USED_IN_QUALITY_MEASURE_FIVE_STAR_RATING  STRING,
  MEASURE_PERIOD                         STRING,
  LOCATION                               STRING,
  PROCESSING_DATE                        DATE,
  
  -- Metadata
  _LOAD_TIME                             TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  _SOURCE_FILE                           STRING,
  _LOAD_ID                               STRING
) COMMENT = 'Claims-based quality measures - readmissions, ED visits, hospitalizations';

-- ============================================================================
-- LOAD DATA
-- ============================================================================

COPY INTO QUALITY_CLAIMS (
    CCN,
    PROVIDER_NAME,
    PROVIDER_ADDRESS,
    CITY_TOWN,
    STATE,
    ZIP_CODE,
    MEASURE_CODE,
    MEASURE_DESCRIPTION,
    RESIDENT_TYPE,
    ADJUSTED_SCORE,
    OBSERVED_SCORE,
    EXPECTED_SCORE,
    FOOTNOTE_FOR_SCORE,
    USED_IN_QUALITY_MEASURE_FIVE_STAR_RATING,
    MEASURE_PERIOD,
    LOCATION,
    PROCESSING_DATE,
    _SOURCE_FILE,
    _LOAD_ID
)
FROM (
    SELECT 
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15, $16, $17,
        METADATA$FILENAME,
        TO_VARCHAR(CONCAT(METADATA$FILENAME,'_',METADATA$FILE_ROW_NUMBER))
    FROM @HEALTHCARE_S3_STAGE/
)
PATTERN = '.*load_dt=.*/NH_QualityMsr_Claims.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_pro)
ON_ERROR = 'CONTINUE'
Force = FALSE;


-- Verify
SELECT COUNT(*) AS total_rows FROM QUALITY_CLAIMS;
SELECT * FROM QUALITY_CLAIMS LIMIT 10;

-- Check measure distribution
SELECT 
    MEASURE_CODE,
    MEASURE_DESCRIPTION,
    RESIDENT_TYPE,
    COUNT(*) AS facility_count,
    ROUND(AVG(ADJUSTED_SCORE), 2) AS avg_adjusted_score
FROM QUALITY_CLAIMS
GROUP BY MEASURE_CODE, MEASURE_DESCRIPTION, RESIDENT_TYPE
ORDER BY MEASURE_CODE;

-- Check metadata
SELECT 
    COUNT(*) AS total_rows,
    COUNT(_SOURCE_FILE) AS has_source_file,
    COUNT(_LOAD_ID) AS has_load_id,
    COUNT(DISTINCT CCN) AS unique_facilities,
    COUNT(DISTINCT MEASURE_CODE) AS unique_measures
FROM QUALITY_CLAIMS;

```

# 5th table 


``` sql

-- ============================================================================
-- TABLE 5: PENALTIES
-- Facility Penalties and Fines
-- File: NH_Penalties_Oct2024.csv
-- Rows: ~28,507
-- ============================================================================

DROP TABLE IF EXISTS PENALTIES;

CREATE OR REPLACE TABLE PENALTIES (
  -- Facility Identifiers
  CCN                                    STRING,
  PROVIDER_NAME                          STRING,
  PROVIDER_ADDRESS                       STRING,
  CITY_TOWN                              STRING,
  STATE                                  STRING,
  ZIP_CODE                               STRING,
  
  -- Penalty Information
  PENALTY_DATE                           DATE,
  PENALTY_TYPE                           STRING,
  FINE_AMOUNT                            NUMBER(38,2),
  PAYMENT_DENIAL_START_DATE              DATE,
  PAYMENT_DENIAL_LENGTH_IN_DAYS          NUMBER(38,0),
  
  -- Location & Processing
  LOCATION                               STRING,
  PROCESSING_DATE                        DATE,
  
  -- Metadata
  _LOAD_TIME                             TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  _SOURCE_FILE                           STRING,
  _LOAD_ID                               STRING
) COMMENT = 'Facility penalties including fines and payment denials';

-- ============================================================================
-- LOAD DATA
-- ============================================================================

COPY INTO PENALTIES (
    CCN,
    PROVIDER_NAME,
    PROVIDER_ADDRESS,
    CITY_TOWN,
    STATE,
    ZIP_CODE,
    PENALTY_DATE,
    PENALTY_TYPE,
    FINE_AMOUNT,
    PAYMENT_DENIAL_START_DATE,
    PAYMENT_DENIAL_LENGTH_IN_DAYS,
    LOCATION,
    PROCESSING_DATE,
    _SOURCE_FILE,
    _LOAD_ID
)
FROM (
    SELECT 
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13,
        METADATA$FILENAME,
        TO_VARCHAR(CONCAT(METADATA$FILENAME,'_',METADATA$FILE_ROW_NUMBER))
    FROM @HEALTHCARE_S3_STAGE/
)
PATTERN = '.*load_dt=.*/NH_Penalties.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_pro)
ON_ERROR = 'CONTINUE'
Force = FALSE;


-- Verify
SELECT COUNT(*) AS total_rows FROM PENALTIES;
SELECT * FROM PENALTIES LIMIT 10;

-- Check penalty types
SELECT 
    PENALTY_TYPE,
    COUNT(*) AS penalty_count,
    SUM(FINE_AMOUNT) AS total_fines,
    ROUND(AVG(FINE_AMOUNT), 2) AS avg_fine_amount,
    MAX(FINE_AMOUNT) AS max_fine_amount
FROM PENALTIES
WHERE FINE_AMOUNT IS NOT NULL
GROUP BY PENALTY_TYPE
ORDER BY total_fines DESC;

-- Top 10 facilities by total fines
SELECT 
    CCN,
    PROVIDER_NAME,
    STATE,
    COUNT(*) AS total_penalties,
    SUM(FINE_AMOUNT) AS total_fine_amount,
    MIN(PENALTY_DATE) AS earliest_penalty,
    MAX(PENALTY_DATE) AS latest_penalty
FROM PENALTIES
WHERE FINE_AMOUNT IS NOT NULL
GROUP BY CCN, PROVIDER_NAME, STATE
ORDER BY total_fine_amount DESC
LIMIT 10;

-- Penalties by state
SELECT 
    STATE,
    COUNT(*) AS penalty_count,
    COUNT(DISTINCT CCN) AS facilities_with_penalties,
    SUM(FINE_AMOUNT) AS total_fines,
    ROUND(AVG(FINE_AMOUNT), 2) AS avg_fine
FROM PENALTIES
WHERE FINE_AMOUNT IS NOT NULL
GROUP BY STATE
ORDER BY total_fines DESC;

-- Check metadata
SELECT 
    COUNT(*) AS total_rows,
    COUNT(_SOURCE_FILE) AS has_source_file,
    COUNT(_LOAD_ID) AS has_load_id,
    COUNT(DISTINCT CCN) AS unique_facilities,
    MIN(PENALTY_DATE) AS earliest_penalty_date,
    MAX(PENALTY_DATE) AS latest_penalty_date
FROM PENALTIES;


```


# Table 6th PROVIDER_INFO - ANALYZING FILE


```sql

-- ============================================================================
-- TABLE 6: PROVIDER_INFO
-- Master Provider/Facility Information
-- File: NH_ProviderInfo_Oct2024.csv
-- Rows: ~14,816
-- Columns: 103 (LARGEST TABLE)
-- ============================================================================

DROP TABLE IF EXISTS PROVIDER_INFO;

CREATE OR REPLACE TABLE PROVIDER_INFO (
  
  -- ========================================================================
  -- FACILITY IDENTIFIERS (Columns 1-6)
  -- ========================================================================
  CCN                                                    STRING,
  PROVIDER_NAME                                          STRING,
  PROVIDER_ADDRESS                                       STRING,
  CITY_TOWN                                              STRING,
  STATE                                                  STRING,
  ZIP_CODE                                               STRING,
  
  -- ========================================================================
  -- CONTACT & BASIC INFO (Columns 7-20)
  -- ========================================================================
  TELEPHONE_NUMBER                                       STRING,
  PROVIDER_SSA_COUNTY_CODE                              STRING,
  COUNTY_PARISH                                          STRING,
  OWNERSHIP_TYPE                                         STRING,
  NUMBER_OF_CERTIFIED_BEDS                              NUMBER(38,0),
  AVERAGE_NUMBER_OF_RESIDENTS_PER_DAY                   FLOAT,
  AVERAGE_NUMBER_OF_RESIDENTS_PER_DAY_FOOTNOTE          STRING,
  PROVIDER_TYPE                                          STRING,
  PROVIDER_RESIDES_IN_HOSPITAL                          STRING,
  LEGAL_BUSINESS_NAME                                    STRING,
  DATE_FIRST_APPROVED_TO_PROVIDE_MEDICARE_MEDICAID      DATE,
  AFFILIATED_ENTITY_NAME                                 STRING,
  AFFILIATED_ENTITY_ID                                   STRING,
  CONTINUING_CARE_RETIREMENT_COMMUNITY                   STRING,
  
  -- ========================================================================
  -- STATUS FLAGS (Columns 21-26)
  -- ========================================================================
  SPECIAL_FOCUS_STATUS                                   STRING,
  ABUSE_ICON                                             STRING,
  MOST_RECENT_HEALTH_INSPECTION_MORE_THAN_2_YEARS_AGO   STRING,
  PROVIDER_CHANGED_OWNERSHIP_IN_LAST_12_MONTHS          STRING,
  WITH_A_RESIDENT_AND_FAMILY_COUNCIL                    STRING,
  AUTOMATIC_SPRINKLER_SYSTEMS_IN_ALL_REQUIRED_AREAS     STRING,
  
  -- ========================================================================
  -- STAR RATINGS (Columns 27-40)
  -- ========================================================================
  OVERALL_RATING                                         NUMBER(38,0),
  OVERALL_RATING_FOOTNOTE                               STRING,
  HEALTH_INSPECTION_RATING                              NUMBER(38,0),
  HEALTH_INSPECTION_RATING_FOOTNOTE                     STRING,
  QM_RATING                                              NUMBER(38,0),
  QM_RATING_FOOTNOTE                                     STRING,
  LONG_STAY_QM_RATING                                    NUMBER(38,0),
  LONG_STAY_QM_RATING_FOOTNOTE                          STRING,
  SHORT_STAY_QM_RATING                                   NUMBER(38,0),
  SHORT_STAY_QM_RATING_FOOTNOTE                         STRING,
  STAFFING_RATING                                        NUMBER(38,0),
  STAFFING_RATING_FOOTNOTE                              STRING,
  REPORTED_STAFFING_FOOTNOTE                            STRING,
  PHYSICAL_THERAPIST_STAFFING_FOOTNOTE                  STRING,
  
  -- ========================================================================
  -- REPORTED STAFFING (Columns 41-54)
  -- ========================================================================
  REPORTED_NURSE_AIDE_STAFFING_HOURS_PER_RESIDENT_PER_DAY     FLOAT,
  REPORTED_LPN_STAFFING_HOURS_PER_RESIDENT_PER_DAY            FLOAT,
  REPORTED_RN_STAFFING_HOURS_PER_RESIDENT_PER_DAY             FLOAT,
  REPORTED_LICENSED_STAFFING_HOURS_PER_RESIDENT_PER_DAY       FLOAT,
  REPORTED_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY    FLOAT,
  TOTAL_NUMBER_OF_NURSE_STAFF_HOURS_PER_RESIDENT_PER_DAY_ON_WEEKEND  FLOAT,
  REGISTERED_NURSE_HOURS_PER_RESIDENT_PER_DAY_ON_WEEKEND      FLOAT,
  REPORTED_PHYSICAL_THERAPIST_STAFFING_HOURS_PER_RESIDENT_PER_DAY  FLOAT,
  TOTAL_NURSING_STAFF_TURNOVER                                FLOAT,
  TOTAL_NURSING_STAFF_TURNOVER_FOOTNOTE                       STRING,
  REGISTERED_NURSE_TURNOVER                                   FLOAT,
  REGISTERED_NURSE_TURNOVER_FOOTNOTE                          STRING,
  NUMBER_OF_ADMINISTRATORS_WHO_HAVE_LEFT_THE_NURSING_HOME     NUMBER(38,0),
  ADMINISTRATOR_TURNOVER_FOOTNOTE                             STRING,
  
  -- ========================================================================
  -- CASE-MIX ADJUSTED STAFFING (Columns 55-66)
  -- ========================================================================
  NURSING_CASE_MIX_INDEX                                      FLOAT,
  NURSING_CASE_MIX_INDEX_RATIO                               FLOAT,
  CASE_MIX_NURSE_AIDE_STAFFING_HOURS_PER_RESIDENT_PER_DAY    FLOAT,
  CASE_MIX_LPN_STAFFING_HOURS_PER_RESIDENT_PER_DAY           FLOAT,
  CASE_MIX_RN_STAFFING_HOURS_PER_RESIDENT_PER_DAY            FLOAT,
  CASE_MIX_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY   FLOAT,
  CASE_MIX_WEEKEND_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY  FLOAT,
  ADJUSTED_NURSE_AIDE_STAFFING_HOURS_PER_RESIDENT_PER_DAY    FLOAT,
  ADJUSTED_LPN_STAFFING_HOURS_PER_RESIDENT_PER_DAY           FLOAT,
  ADJUSTED_RN_STAFFING_HOURS_PER_RESIDENT_PER_DAY            FLOAT,
  ADJUSTED_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY   FLOAT,
  ADJUSTED_WEEKEND_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY  FLOAT,
  
  -- ========================================================================
  -- SURVEY CYCLE 1 (Columns 67-74)
  -- ========================================================================
  RATING_CYCLE_1_STANDARD_SURVEY_HEALTH_DATE             DATE,
  RATING_CYCLE_1_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES    NUMBER(38,0),
  RATING_CYCLE_1_NUMBER_OF_STANDARD_HEALTH_DEFICIENCIES NUMBER(38,0),
  RATING_CYCLE_1_NUMBER_OF_COMPLAINT_HEALTH_DEFICIENCIES NUMBER(38,0),
  RATING_CYCLE_1_HEALTH_DEFICIENCY_SCORE                 NUMBER(38,0),
  RATING_CYCLE_1_NUMBER_OF_HEALTH_REVISITS              NUMBER(38,0),
  RATING_CYCLE_1_HEALTH_REVISIT_SCORE                   NUMBER(38,0),
  RATING_CYCLE_1_TOTAL_HEALTH_SCORE                     NUMBER(38,0),
  
  -- ========================================================================
  -- SURVEY CYCLE 2 (Columns 75-82)
  -- ========================================================================
  RATING_CYCLE_2_STANDARD_HEALTH_SURVEY_DATE            DATE,
  RATING_CYCLE_2_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES    NUMBER(38,0),
  RATING_CYCLE_2_NUMBER_OF_STANDARD_HEALTH_DEFICIENCIES NUMBER(38,0),
  RATING_CYCLE_2_NUMBER_OF_COMPLAINT_HEALTH_DEFICIENCIES NUMBER(38,0),
  RATING_CYCLE_2_HEALTH_DEFICIENCY_SCORE                NUMBER(38,0),
  RATING_CYCLE_2_NUMBER_OF_HEALTH_REVISITS              NUMBER(38,0),
  RATING_CYCLE_2_HEALTH_REVISIT_SCORE                   NUMBER(38,0),
  RATING_CYCLE_2_TOTAL_HEALTH_SCORE                     NUMBER(38,0),
  
  -- ========================================================================
  -- SURVEY CYCLE 3 (Columns 83-90)
  -- ========================================================================
  RATING_CYCLE_3_STANDARD_HEALTH_SURVEY_DATE            DATE,
  RATING_CYCLE_3_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES    NUMBER(38,0),
  RATING_CYCLE_3_NUMBER_OF_STANDARD_HEALTH_DEFICIENCIES NUMBER(38,0),
  RATING_CYCLE_3_NUMBER_OF_COMPLAINT_HEALTH_DEFICIENCIES NUMBER(38,0),
  RATING_CYCLE_3_HEALTH_DEFICIENCY_SCORE                NUMBER(38,0),
  RATING_CYCLE_3_NUMBER_OF_HEALTH_REVISITS              NUMBER(38,0),
  RATING_CYCLE_3_HEALTH_REVISIT_SCORE                   NUMBER(38,0),
  RATING_CYCLE_3_TOTAL_HEALTH_SCORE                     NUMBER(38,0),
  
  -- ========================================================================
  -- PENALTIES & COMPLAINTS (Columns 91-98)
  -- ========================================================================
  TOTAL_WEIGHTED_HEALTH_SURVEY_SCORE                    FLOAT,
  NUMBER_OF_FACILITY_REPORTED_INCIDENTS                 NUMBER(38,0),
  NUMBER_OF_SUBSTANTIATED_COMPLAINTS                    NUMBER(38,0),
  NUMBER_OF_CITATIONS_FROM_INFECTION_CONTROL_INSPECTIONS NUMBER(38,0),
  NUMBER_OF_FINES                                        NUMBER(38,0),
  TOTAL_AMOUNT_OF_FINES_IN_DOLLARS                      NUMBER(38,2),
  NUMBER_OF_PAYMENT_DENIALS                             NUMBER(38,0),
  TOTAL_NUMBER_OF_PENALTIES                             NUMBER(38,0),
  
  -- ========================================================================
  -- LOCATION & PROCESSING (Columns 99-103)
  -- ========================================================================
  LOCATION                                               STRING,
  LATITUDE                                               FLOAT,
  LONGITUDE                                              FLOAT,
  GEOCODING_FOOTNOTE                                     STRING,
  PROCESSING_DATE                                        DATE,
  
  -- ========================================================================
  -- METADATA (Our tracking fields)
  -- ========================================================================
  _LOAD_TIME                                             TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  _SOURCE_FILE                                           STRING,
  _LOAD_ID                                               STRING
  
) COMMENT = 'Master provider information - comprehensive facility data with ratings, staffing, surveys, and penalties';

-- ============================================================================
-- LOAD DATA
-- ============================================================================

COPY INTO PROVIDER_INFO (
    -- Facility Identifiers
    CCN, PROVIDER_NAME, PROVIDER_ADDRESS, CITY_TOWN, STATE, ZIP_CODE,
    -- Contact & Basic Info
    TELEPHONE_NUMBER, PROVIDER_SSA_COUNTY_CODE, COUNTY_PARISH, OWNERSHIP_TYPE,
    NUMBER_OF_CERTIFIED_BEDS, AVERAGE_NUMBER_OF_RESIDENTS_PER_DAY, 
    AVERAGE_NUMBER_OF_RESIDENTS_PER_DAY_FOOTNOTE, PROVIDER_TYPE,
    PROVIDER_RESIDES_IN_HOSPITAL, LEGAL_BUSINESS_NAME,
    DATE_FIRST_APPROVED_TO_PROVIDE_MEDICARE_MEDICAID, AFFILIATED_ENTITY_NAME,
    AFFILIATED_ENTITY_ID, CONTINUING_CARE_RETIREMENT_COMMUNITY,
    -- Status Flags
    SPECIAL_FOCUS_STATUS, ABUSE_ICON, MOST_RECENT_HEALTH_INSPECTION_MORE_THAN_2_YEARS_AGO,
    PROVIDER_CHANGED_OWNERSHIP_IN_LAST_12_MONTHS, WITH_A_RESIDENT_AND_FAMILY_COUNCIL,
    AUTOMATIC_SPRINKLER_SYSTEMS_IN_ALL_REQUIRED_AREAS,
    -- Star Ratings
    OVERALL_RATING, OVERALL_RATING_FOOTNOTE, HEALTH_INSPECTION_RATING,
    HEALTH_INSPECTION_RATING_FOOTNOTE, QM_RATING, QM_RATING_FOOTNOTE,
    LONG_STAY_QM_RATING, LONG_STAY_QM_RATING_FOOTNOTE, SHORT_STAY_QM_RATING,
    SHORT_STAY_QM_RATING_FOOTNOTE, STAFFING_RATING, STAFFING_RATING_FOOTNOTE,
    REPORTED_STAFFING_FOOTNOTE, PHYSICAL_THERAPIST_STAFFING_FOOTNOTE,
    -- Reported Staffing
    REPORTED_NURSE_AIDE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    REPORTED_LPN_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    REPORTED_RN_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    REPORTED_LICENSED_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    REPORTED_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    TOTAL_NUMBER_OF_NURSE_STAFF_HOURS_PER_RESIDENT_PER_DAY_ON_WEEKEND,
    REGISTERED_NURSE_HOURS_PER_RESIDENT_PER_DAY_ON_WEEKEND,
    REPORTED_PHYSICAL_THERAPIST_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    TOTAL_NURSING_STAFF_TURNOVER, TOTAL_NURSING_STAFF_TURNOVER_FOOTNOTE,
    REGISTERED_NURSE_TURNOVER, REGISTERED_NURSE_TURNOVER_FOOTNOTE,
    NUMBER_OF_ADMINISTRATORS_WHO_HAVE_LEFT_THE_NURSING_HOME,
    ADMINISTRATOR_TURNOVER_FOOTNOTE,
    -- Case-Mix Adjusted Staffing
    NURSING_CASE_MIX_INDEX, NURSING_CASE_MIX_INDEX_RATIO,
    CASE_MIX_NURSE_AIDE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    CASE_MIX_LPN_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    CASE_MIX_RN_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    CASE_MIX_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    CASE_MIX_WEEKEND_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    ADJUSTED_NURSE_AIDE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    ADJUSTED_LPN_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    ADJUSTED_RN_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    ADJUSTED_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    ADJUSTED_WEEKEND_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY,
    -- Survey Cycle 1
    RATING_CYCLE_1_STANDARD_SURVEY_HEALTH_DATE,
    RATING_CYCLE_1_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES,
    RATING_CYCLE_1_NUMBER_OF_STANDARD_HEALTH_DEFICIENCIES,
    RATING_CYCLE_1_NUMBER_OF_COMPLAINT_HEALTH_DEFICIENCIES,
    RATING_CYCLE_1_HEALTH_DEFICIENCY_SCORE,
    RATING_CYCLE_1_NUMBER_OF_HEALTH_REVISITS,
    RATING_CYCLE_1_HEALTH_REVISIT_SCORE,
    RATING_CYCLE_1_TOTAL_HEALTH_SCORE,
    -- Survey Cycle 2
    RATING_CYCLE_2_STANDARD_HEALTH_SURVEY_DATE,
    RATING_CYCLE_2_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES,
    RATING_CYCLE_2_NUMBER_OF_STANDARD_HEALTH_DEFICIENCIES,
    RATING_CYCLE_2_NUMBER_OF_COMPLAINT_HEALTH_DEFICIENCIES,
    RATING_CYCLE_2_HEALTH_DEFICIENCY_SCORE,
    RATING_CYCLE_2_NUMBER_OF_HEALTH_REVISITS,
    RATING_CYCLE_2_HEALTH_REVISIT_SCORE,
    RATING_CYCLE_2_TOTAL_HEALTH_SCORE,
    -- Survey Cycle 3
    RATING_CYCLE_3_STANDARD_HEALTH_SURVEY_DATE,
    RATING_CYCLE_3_TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES,
    RATING_CYCLE_3_NUMBER_OF_STANDARD_HEALTH_DEFICIENCIES,
    RATING_CYCLE_3_NUMBER_OF_COMPLAINT_HEALTH_DEFICIENCIES,
    RATING_CYCLE_3_HEALTH_DEFICIENCY_SCORE,
    RATING_CYCLE_3_NUMBER_OF_HEALTH_REVISITS,
    RATING_CYCLE_3_HEALTH_REVISIT_SCORE,
    RATING_CYCLE_3_TOTAL_HEALTH_SCORE,
    -- Penalties & Complaints
    TOTAL_WEIGHTED_HEALTH_SURVEY_SCORE,
    NUMBER_OF_FACILITY_REPORTED_INCIDENTS,
    NUMBER_OF_SUBSTANTIATED_COMPLAINTS,
    NUMBER_OF_CITATIONS_FROM_INFECTION_CONTROL_INSPECTIONS,
    NUMBER_OF_FINES,
    TOTAL_AMOUNT_OF_FINES_IN_DOLLARS,
    NUMBER_OF_PAYMENT_DENIALS,
    TOTAL_NUMBER_OF_PENALTIES,
    -- Location & Processing
    LOCATION, LATITUDE, LONGITUDE, GEOCODING_FOOTNOTE, PROCESSING_DATE,
    -- Metadata
    _SOURCE_FILE, _LOAD_ID
)
FROM (
    SELECT 
        -- All 103 columns using positional notation
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
        $21, $22, $23, $24, $25, $26, $27, $28, $29, $30,
        $31, $32, $33, $34, $35, $36, $37, $38, $39, $40,
        $41, $42, $43, $44, $45, $46, $47, $48, $49, $50,
        $51, $52, $53, $54, $55, $56, $57, $58, $59, $60,
        $61, $62, $63, $64, $65, $66, $67, $68, $69, $70,
        $71, $72, $73, $74, $75, $76, $77, $78, $79, $80,
        $81, $82, $83, $84, $85, $86, $87, $88, $89, $90,
        $91, $92, $93, $94, $95, $96, $97, $98, $99, $100,
        $101, $102, $103,
        -- Metadata
        METADATA$FILENAME,
        TO_VARCHAR(CONCAT(METADATA$FILENAME,'_',METADATA$FILE_ROW_NUMBER))
    FROM @HEALTHCARE_S3_STAGE/
)
PATTERN = '.*load_dt=.*/NH_ProviderInfo.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_pro)
ON_ERROR = 'CONTINUE'
Force = FALSE;


-- Verify
SELECT COUNT(*) AS total_rows FROM PROVIDER_INFO;
SELECT * FROM PROVIDER_INFO LIMIT 5;

-- Check key fields
SELECT 
    COUNT(*) AS total_facilities,
    COUNT(DISTINCT CCN) AS unique_ccn,
    COUNT(DISTINCT STATE) AS unique_states,
    COUNT(DISTINCT OWNERSHIP_TYPE) AS ownership_types,
    ROUND(AVG(OVERALL_RATING), 2) AS avg_overall_rating,
    ROUND(AVG(REPORTED_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY), 2) AS avg_total_nursing_hours,
    ROUND(AVG(TOTAL_NURSING_STAFF_TURNOVER), 1) AS avg_turnover_pct
FROM PROVIDER_INFO;

-- Top 10 highest rated facilities
SELECT 
    CCN, PROVIDER_NAME, STATE, OWNERSHIP_TYPE,
    OVERALL_RATING,
    HEALTH_INSPECTION_RATING,
    QM_RATING,
    STAFFING_RATING,
    REPORTED_TOTAL_NURSE_STAFFING_HOURS_PER_RESIDENT_PER_DAY
FROM PROVIDER_INFO
WHERE OVERALL_RATING = 5
LIMIT 10;

```
# 7th Table SURVEY_SUMMARY

```sql


-- ============================================================================
-- TABLE 7: SURVEY_SUMMARY
-- Survey Deficiency Summary by Category
-- File: NH_SurveySummary_Oct2024.csv
-- Rows: ~44,245
-- Columns: 41
-- ============================================================================

DROP TABLE IF EXISTS SURVEY_SUMMARY;

CREATE OR REPLACE TABLE SURVEY_SUMMARY (
  
  -- ========================================================================
  -- FACILITY IDENTIFIERS (Columns 1-6)
  -- ========================================================================
  CCN                                                          STRING,
  PROVIDER_NAME                                                STRING,
  PROVIDER_ADDRESS                                             STRING,
  CITY_TOWN                                                    STRING,
  STATE                                                        STRING,
  ZIP_CODE                                                     STRING,
  
  -- ========================================================================
  -- SURVEY INFORMATION (Columns 7-11)
  -- ========================================================================
  INSPECTION_CYCLE                                             NUMBER(38,0),
  HEALTH_SURVEY_DATE                                           DATE,
  FIRE_SAFETY_SURVEY_DATE                                      DATE,
  TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES                         NUMBER(38,0),
  TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES                    NUMBER(38,0),
  
  -- ========================================================================
  -- HEALTH DEFICIENCY CATEGORIES (Columns 12-22)
  -- ========================================================================
  COUNT_OF_FREEDOM_FROM_ABUSE_AND_NEGLECT_AND_EXPLOITATION_DEFICIENCIES  NUMBER(38,0),
  COUNT_OF_QUALITY_OF_LIFE_AND_CARE_DEFICIENCIES              NUMBER(38,0),
  COUNT_OF_RESIDENT_ASSESSMENT_AND_CARE_PLANNING_DEFICIENCIES NUMBER(38,0),
  COUNT_OF_NURSING_AND_PHYSICIAN_SERVICES_DEFICIENCIES        NUMBER(38,0),
  COUNT_OF_RESIDENT_RIGHTS_DEFICIENCIES                       NUMBER(38,0),
  COUNT_OF_NUTRITION_AND_DIETARY_DEFICIENCIES                 NUMBER(38,0),
  COUNT_OF_PHARMACY_SERVICE_DEFICIENCIES                      NUMBER(38,0),
  COUNT_OF_ENVIRONMENTAL_DEFICIENCIES                         NUMBER(38,0),
  COUNT_OF_ADMINISTRATION_DEFICIENCIES                        NUMBER(38,0),
  COUNT_OF_INFECTION_CONTROL_DEFICIENCIES                     NUMBER(38,0),
  COUNT_OF_EMERGENCY_PREPAREDNESS_DEFICIENCIES                NUMBER(38,0),
  
  -- ========================================================================
  -- FIRE SAFETY DEFICIENCY CATEGORIES (Columns 23-39)
  -- ========================================================================
  COUNT_OF_AUTOMATIC_SPRINKLER_SYSTEMS_DEFICIENCIES          NUMBER(38,0),
  COUNT_OF_CONSTRUCTION_DEFICIENCIES                          NUMBER(38,0),
  COUNT_OF_SERVICES_DEFICIENCIES                              NUMBER(38,0),
  COUNT_OF_CORRIDOR_WALLS_AND_DOORS_DEFICIENCIES             NUMBER(38,0),
  COUNT_OF_EGRESS_DEFICIENCIES                                NUMBER(38,0),
  COUNT_OF_ELECTRICAL_DEFICIENCIES                            NUMBER(38,0),
  COUNT_OF_EMERGENCY_PLANS_AND_FIRE_DRILLS_DEFICIENCIES      NUMBER(38,0),
  COUNT_OF_FIRE_ALARM_SYSTEMS_DEFICIENCIES                   NUMBER(38,0),
  COUNT_OF_SMOKE_DEFICIENCIES                                 NUMBER(38,0),
  COUNT_OF_INTERIOR_DEFICIENCIES                              NUMBER(38,0),
  COUNT_OF_GAS_AND_VACUUM_AND_ELECTRICAL_SYSTEMS_DEFICIENCIES NUMBER(38,0),
  COUNT_OF_HAZARDOUS_AREA_DEFICIENCIES                        NUMBER(38,0),
  COUNT_OF_ILLUMINATION_AND_EMERGENCY_POWER_DEFICIENCIES     NUMBER(38,0),
  COUNT_OF_LABORATORIES_DEFICIENCIES                          NUMBER(38,0),
  COUNT_OF_MEDICAL_GASES_AND_ANAESTHETIZING_AREAS_DEFICIENCIES NUMBER(38,0),
  COUNT_OF_SMOKING_REGULATIONS_DEFICIENCIES                   NUMBER(38,0),
  COUNT_OF_MISCELLANEOUS_DEFICIENCIES                         NUMBER(38,0),
  
  -- ========================================================================
  -- LOCATION & PROCESSING (Columns 40-41)
  -- ========================================================================
  LOCATION                                                     STRING,
  PROCESSING_DATE                                              DATE,
  
  -- ========================================================================
  -- METADATA (Our tracking fields)
  -- ========================================================================
  _LOAD_TIME                                                   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  _SOURCE_FILE                                                 STRING,
  _LOAD_ID                                                     STRING
  
) COMMENT = 'Survey summary with detailed deficiency counts by category for each inspection cycle';

-- ============================================================================
-- LOAD DATA
-- ============================================================================

COPY INTO SURVEY_SUMMARY (
    -- Facility Identifiers
    CCN, PROVIDER_NAME, PROVIDER_ADDRESS, CITY_TOWN, STATE, ZIP_CODE,
    -- Survey Information
    INSPECTION_CYCLE, HEALTH_SURVEY_DATE, FIRE_SAFETY_SURVEY_DATE,
    TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES, TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES,
    -- Health Deficiency Categories
    COUNT_OF_FREEDOM_FROM_ABUSE_AND_NEGLECT_AND_EXPLOITATION_DEFICIENCIES,
    COUNT_OF_QUALITY_OF_LIFE_AND_CARE_DEFICIENCIES,
    COUNT_OF_RESIDENT_ASSESSMENT_AND_CARE_PLANNING_DEFICIENCIES,
    COUNT_OF_NURSING_AND_PHYSICIAN_SERVICES_DEFICIENCIES,
    COUNT_OF_RESIDENT_RIGHTS_DEFICIENCIES,
    COUNT_OF_NUTRITION_AND_DIETARY_DEFICIENCIES,
    COUNT_OF_PHARMACY_SERVICE_DEFICIENCIES,
    COUNT_OF_ENVIRONMENTAL_DEFICIENCIES,
    COUNT_OF_ADMINISTRATION_DEFICIENCIES,
    COUNT_OF_INFECTION_CONTROL_DEFICIENCIES,
    COUNT_OF_EMERGENCY_PREPAREDNESS_DEFICIENCIES,
    -- Fire Safety Deficiency Categories
    COUNT_OF_AUTOMATIC_SPRINKLER_SYSTEMS_DEFICIENCIES,
    COUNT_OF_CONSTRUCTION_DEFICIENCIES,
    COUNT_OF_SERVICES_DEFICIENCIES,
    COUNT_OF_CORRIDOR_WALLS_AND_DOORS_DEFICIENCIES,
    COUNT_OF_EGRESS_DEFICIENCIES,
    COUNT_OF_ELECTRICAL_DEFICIENCIES,
    COUNT_OF_EMERGENCY_PLANS_AND_FIRE_DRILLS_DEFICIENCIES,
    COUNT_OF_FIRE_ALARM_SYSTEMS_DEFICIENCIES,
    COUNT_OF_SMOKE_DEFICIENCIES,
    COUNT_OF_INTERIOR_DEFICIENCIES,
    COUNT_OF_GAS_AND_VACUUM_AND_ELECTRICAL_SYSTEMS_DEFICIENCIES,
    COUNT_OF_HAZARDOUS_AREA_DEFICIENCIES,
    COUNT_OF_ILLUMINATION_AND_EMERGENCY_POWER_DEFICIENCIES,
    COUNT_OF_LABORATORIES_DEFICIENCIES,
    COUNT_OF_MEDICAL_GASES_AND_ANAESTHETIZING_AREAS_DEFICIENCIES,
    COUNT_OF_SMOKING_REGULATIONS_DEFICIENCIES,
    COUNT_OF_MISCELLANEOUS_DEFICIENCIES,
    -- Location & Processing
    LOCATION, PROCESSING_DATE,
    -- Metadata
    _SOURCE_FILE, _LOAD_ID
)
FROM (
    SELECT 
        -- All 41 columns using positional notation
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
        $21, $22, $23, $24, $25, $26, $27, $28, $29, $30,
        $31, $32, $33, $34, $35, $36, $37, $38, $39, $40,
        $41,
        -- Metadata
        METADATA$FILENAME,
        TO_VARCHAR(CONCAT(METADATA$FILENAME,'_',METADATA$FILE_ROW_NUMBER))
    FROM @HEALTHCARE_S3_STAGE/
)
PATTERN = '.*load_dt=.*/NH_SurveySummary.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_pro)
ON_ERROR = 'CONTINUE'
Force = FALSE;


-- Verify
SELECT COUNT(*) AS total_rows FROM SURVEY_SUMMARY;
SELECT * FROM SURVEY_SUMMARY LIMIT 10;

-- Summary by inspection cycle
SELECT 
    INSPECTION_CYCLE,
    COUNT(*) AS survey_count,
    COUNT(DISTINCT CCN) AS unique_facilities,
    ROUND(AVG(TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES), 2) AS avg_health_deficiencies,
    ROUND(AVG(TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES), 2) AS avg_fire_safety_deficiencies,
    MIN(HEALTH_SURVEY_DATE) AS earliest_survey,
    MAX(HEALTH_SURVEY_DATE) AS latest_survey
FROM SURVEY_SUMMARY
GROUP BY INSPECTION_CYCLE
ORDER BY INSPECTION_CYCLE;

-- Top deficiency categories (Health)
SELECT 
    'Abuse & Neglect' AS category,
    SUM(COUNT_OF_FREEDOM_FROM_ABUSE_AND_NEGLECT_AND_EXPLOITATION_DEFICIENCIES) AS total_count
FROM SURVEY_SUMMARY
UNION ALL
SELECT 'Quality of Life', SUM(COUNT_OF_QUALITY_OF_LIFE_AND_CARE_DEFICIENCIES) FROM SURVEY_SUMMARY
UNION ALL
SELECT 'Assessment & Planning', SUM(COUNT_OF_RESIDENT_ASSESSMENT_AND_CARE_PLANNING_DEFICIENCIES) FROM SURVEY_SUMMARY
UNION ALL
SELECT 'Nursing Services', SUM(COUNT_OF_NURSING_AND_PHYSICIAN_SERVICES_DEFICIENCIES) FROM SURVEY_SUMMARY
UNION ALL
SELECT 'Resident Rights', SUM(COUNT_OF_RESIDENT_RIGHTS_DEFICIENCIES) FROM SURVEY_SUMMARY
UNION ALL
SELECT 'Nutrition & Dietary', SUM(COUNT_OF_NUTRITION_AND_DIETARY_DEFICIENCIES) FROM SURVEY_SUMMARY
UNION ALL
SELECT 'Pharmacy', SUM(COUNT_OF_PHARMACY_SERVICE_DEFICIENCIES) FROM SURVEY_SUMMARY
UNION ALL
SELECT 'Environmental', SUM(COUNT_OF_ENVIRONMENTAL_DEFICIENCIES) FROM SURVEY_SUMMARY
UNION ALL
SELECT 'Administration', SUM(COUNT_OF_ADMINISTRATION_DEFICIENCIES) FROM SURVEY_SUMMARY
UNION ALL
SELECT 'Infection Control', SUM(COUNT_OF_INFECTION_CONTROL_DEFICIENCIES) FROM SURVEY_SUMMARY
ORDER BY total_count DESC;

-- Facilities with most deficiencies across all cycles
SELECT 
    CCN,
    PROVIDER_NAME,
    STATE,
    COUNT(*) AS total_surveys,
    SUM(TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES) AS total_health_deficiencies,
    SUM(TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES) AS total_fire_safety_deficiencies,
    SUM(TOTAL_NUMBER_OF_HEALTH_DEFICIENCIES + TOTAL_NUMBER_OF_FIRE_SAFETY_DEFICIENCIES) AS total_all_deficiencies
FROM SURVEY_SUMMARY
GROUP BY CCN, PROVIDER_NAME, STATE
ORDER BY total_all_deficiencies DESC
LIMIT 20;

-- Check metadata
SELECT 
    COUNT(*) AS total_rows,
    COUNT(_SOURCE_FILE) AS has_source_file,
    COUNT(_LOAD_ID) AS has_load_id,
    COUNT(DISTINCT CCN) AS unique_facilities,
    COUNT(DISTINCT INSPECTION_CYCLE) AS unique_cycles
FROM SURVEY_SUMMARY;


```

# Table 8th OWNERSHIP

```sql

-- ============================================================================
-- TABLE 8: OWNERSHIP
-- Facility Ownership Information
-- File: NH_Ownership_Oct2024.csv
-- Rows: ~145,355
-- Columns: 13
-- ============================================================================

DROP TABLE IF EXISTS OWNERSHIP;

CREATE OR REPLACE TABLE OWNERSHIP (
  
  -- ========================================================================
  -- FACILITY IDENTIFIERS (Columns 1-6)
  -- ========================================================================
  CCN                                           STRING,
  PROVIDER_NAME                                 STRING,
  PROVIDER_ADDRESS                              STRING,
  CITY_TOWN                                     STRING,
  STATE                                         STRING,
  ZIP_CODE                                      STRING,
  
  -- ========================================================================
  -- OWNERSHIP DETAILS (Columns 7-11)
  -- ========================================================================
  ROLE_PLAYED_BY_OWNER_OR_MANAGER_IN_FACILITY  STRING,
  OWNER_TYPE                                    STRING,
  OWNER_NAME                                    STRING,
  OWNERSHIP_PERCENTAGE                          STRING,
  ASSOCIATION_DATE                              STRING,  -- Stored as string due to "since MM/DD/YYYY" format
  
  -- ========================================================================
  -- LOCATION & PROCESSING (Columns 12-13)
  -- ========================================================================
  LOCATION                                      STRING,
  PROCESSING_DATE                               DATE,
  
  -- ========================================================================
  -- METADATA (Our tracking fields)
  -- ========================================================================
  _LOAD_TIME                                    TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  _SOURCE_FILE                                  STRING,
  _LOAD_ID                                      STRING
  
) COMMENT = 'Facility ownership information - multiple owners per facility possible';

-- ============================================================================
-- LOAD DATA
-- ============================================================================

COPY INTO OWNERSHIP (
    CCN,
    PROVIDER_NAME,
    PROVIDER_ADDRESS,
    CITY_TOWN,
    STATE,
    ZIP_CODE,
    ROLE_PLAYED_BY_OWNER_OR_MANAGER_IN_FACILITY,
    OWNER_TYPE,
    OWNER_NAME,
    OWNERSHIP_PERCENTAGE,
    ASSOCIATION_DATE,
    LOCATION,
    PROCESSING_DATE,
    _SOURCE_FILE,
    _LOAD_ID
)
FROM (
    SELECT 
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13,
        METADATA$FILENAME,
        TO_VARCHAR(CONCAT(METADATA$FILENAME,'_',METADATA$FILE_ROW_NUMBER))
    FROM @HEALTHCARE_S3_STAGE/
)
PATTERN = '.*load_dt=.*/NH_Ownership.*\.csv'
FILE_FORMAT = (FORMAT_NAME = Healthcare_pro)
ON_ERROR = 'CONTINUE'
Force = FALSE;


-- Verify
SELECT COUNT(*) AS total_rows FROM OWNERSHIP;
SELECT * FROM OWNERSHIP LIMIT 10;

-- Check ownership structure
SELECT 
    OWNER_TYPE,
    COUNT(*) AS ownership_records,
    COUNT(DISTINCT CCN) AS unique_facilities
FROM OWNERSHIP
GROUP BY OWNER_TYPE
ORDER BY ownership_records DESC;

-- Check role distribution
SELECT 
    ROLE_PLAYED_BY_OWNER_OR_MANAGER_IN_FACILITY,
    COUNT(*) AS record_count,
    COUNT(DISTINCT CCN) AS unique_facilities
FROM OWNERSHIP
GROUP BY ROLE_PLAYED_BY_OWNER_OR_MANAGER_IN_FACILITY
ORDER BY record_count DESC;

-- Facilities with most owners
SELECT 
    CCN,
    PROVIDER_NAME,
    STATE,
    COUNT(*) AS number_of_owners,
    LISTAGG(DISTINCT OWNER_TYPE, ', ') AS owner_types
FROM OWNERSHIP
GROUP BY CCN, PROVIDER_NAME, STATE
ORDER BY number_of_owners DESC
LIMIT 20;

-- Ownership concentration
SELECT 
    CCN,
    PROVIDER_NAME,
    STATE,
    COUNT(*) AS total_owners,
    COUNT(CASE WHEN OWNER_TYPE = 'Individual' THEN 1 END) AS individual_owners,
    COUNT(CASE WHEN OWNER_TYPE = 'Corporation' THEN 1 END) AS corporate_owners,
    COUNT(CASE WHEN OWNER_TYPE LIKE '%Government%' THEN 1 END) AS government_owners
FROM OWNERSHIP
GROUP BY CCN, PROVIDER_NAME, STATE
HAVING COUNT(*) >= 5
ORDER BY total_owners DESC;

-- Check metadata
SELECT 
    COUNT(*) AS total_rows,
    COUNT(_SOURCE_FILE) AS has_source_file,
    COUNT(_LOAD_ID) AS has_load_id,
    COUNT(DISTINCT CCN) AS unique_facilities,
    COUNT(DISTINCT OWNER_NAME) AS unique_owners
FROM OWNERSHIP;

```


## check all count

```sql

SELECT COUNT(*) FROM PBJ_STAFFING; # 1,325,324
SELECT COUNT(*) FROM VBP_PERFORMANCE; # 10, 858 
SELECT COUNT(*) FROM STATE_AVERAGES; # 54
SELECT COUNT(*) FROM QUALITY_CLAIMS; # 59,256
SELECT COUNT(*) FROM PENALTIES; # 28,505
SELECT COUNT(*) FROM PROVIDER_INFO; # 14,814
SELECT COUNT(*) FROM SURVEY_SUMMARY; # 44,243
SELECT COUNT(*) FROM OWNERSHIP; # 145,354

```
