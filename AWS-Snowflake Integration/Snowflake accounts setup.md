
## Test Account

```sql
-- Test query to verify account is working
SELECT CURRENT_ACCOUNT() AS account_id,
       CURRENT_REGION() AS region,
       CURRENT_USER() AS username,
       CURRENT_ROLE() AS role,
       CURRENT_VERSION() AS snowflake_version;

    -- List all warehouses
SHOW WAREHOUSES;
    -- List all Users
Show USERS;
 -- List all databases
SHOW DATABASES;
 -- List all roles
Show ROLES;

```

## Create Role and User 

Instead of using ACCOUNTADMIN for everything, let's create a dedicated user for our pipeline.

```sql
  -- Create a role for the healthcare pipeline

CREATE ROLE IF NOT EXISTS HEALTHCARE_PIPELINE_ROLE
  COMMENT = 'Role for automated healthcare data pipeline';

  -- Create a user for the pipeline

CREATE USER IF NOT EXISTS HEALTHCARE_PIPELINE_USER
  PASSWORD = ''  -- CHANGE THIS!
  DEFAULT_ROLE = HEALTHCARE_PIPELINE_ROLE
  DEFAULT_WAREHOUSE = 'LOADING_WH'  -- We'll create this soon
  COMMENT = 'User for automated data pipeline from AWS Lambda';

-- Grant role to user
GRANT ROLE HEALTHCARE_PIPELINE_ROLE TO USER HEALTHCARE_PIPELINE_USER;

```

## Create Warehouses

```sql
-- Warehouse for loading data from S3 via Snowpipe
CREATE WAREHOUSE IF NOT EXISTS LOADING_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60  -- Suspend after 60 seconds of inactivity
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Warehouse for loading data from S3';
```

Why X-SMALL?

-       Data loading doesn't require much compute
-       Cost-effective
-       Can scale up if needed

```sql
  -- Warehouse for dbt transformations
CREATE WAREHOUSE IF NOT EXISTS TRANSFORM_WH
  WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 300  -- Suspend after 5 minutes
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Warehouse for dbt data transformations';
```

Why SMALL?

-       Transformations with joins and aggregations need more compute
-       Still cost-effective
-       5-minute auto-suspend for longer dbt runs

```sql
  -- Warehouse for Streamlit dashboard queries
CREATE WAREHOUSE IF NOT EXISTS REPORTING_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 300  -- Suspend after 5 minutes
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Warehouse for dashboard and reporting queries';
```
Why X-SMALL?

-       Dashboard queries are typically simple SELECT statements
-       Pre-aggregated data in Gold layer
-       Cost-effective for end users


## Grant Warehouse Usage to Pipeline Role

```sql

-- Grant usage on warehouses to pipeline role
GRANT USAGE ON WAREHOUSE LOADING_WH TO ROLE HEALTHCARE_PIPELINE_ROLE;
GRANT USAGE ON WAREHOUSE TRANSFORM_WH TO ROLE HEALTHCARE_PIPELINE_ROLE;
GRANT USAGE ON WAREHOUSE REPORTING_WH TO ROLE HEALTHCARE_PIPELINE_ROLE;

-- Allow operations
GRANT OPERATE ON WAREHOUSE LOADING_WH TO ROLE HEALTHCARE_PIPELINE_ROLE;
GRANT OPERATE ON WAREHOUSE TRANSFORM_WH TO ROLE HEALTHCARE_PIPELINE_ROLE;

```

## CREATE DATABASES

Now we'll create the 3 databases for our Medallion Architecture.

```sql

-- RAW database for bronze layer (data exactly as received from S3)
CREATE DATABASE IF NOT EXISTS RAW
  COMMENT = 'Bronze layer - raw data from S3 via Snowpipe';


  -- ANALYTICS database for silver layer (cleaned, validated data)
CREATE DATABASE IF NOT EXISTS ANALYTICS
  COMMENT = 'Silver layer - cleaned and validated data via dbt';

  -- MARTS database for gold layer (business-ready aggregates)
CREATE DATABASE IF NOT EXISTS MARTS
  COMMENT = 'Gold layer - business metrics and aggregates for dashboard';

```

### check Database first

```sql

-- List all databases
SHOW DATABASES;

```

## Grant Database Access to Pipeline Role

```sql

-- Grant usage on databases
GRANT USAGE ON DATABASE RAW TO ROLE HEALTHCARE_PIPELINE_ROLE;
GRANT USAGE ON DATABASE ANALYTICS TO ROLE HEALTHCARE_PIPELINE_ROLE;
GRANT USAGE ON DATABASE MARTS TO ROLE HEALTHCARE_PIPELINE_ROLE;

-- Grant create schema privilege (needed for dbt)
GRANT CREATE SCHEMA ON DATABASE RAW TO ROLE HEALTHCARE_PIPELINE_ROLE;
GRANT CREATE SCHEMA ON DATABASE ANALYTICS TO ROLE HEALTHCARE_PIPELINE_ROLE;
GRANT CREATE SCHEMA ON DATABASE MARTS TO ROLE HEALTHCARE_PIPELINE_ROLE;
```

# Test connections

```sql

    -- List all warehouses
SHOW WAREHOUSES;
    -- List all Users
Show USERS;
 -- List all databases
SHOW DATABASES;
 -- List all roles
Show ROLES;

```
