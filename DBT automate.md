# AUTOMATE dbt RUNS (SNOWFLAKE → DBT → DASHBOARD) By Schedule  

## STEP 1: GO TO dbt CLOUD

- Log in to dbt Cloud: https://cloud.getdbt.com
- Select your project (the healthcare project)
- Click "Deploy" in the left sidebar
- Click "Jobs"

## STEP 2: CREATE A NEW JOB

- Click "Create Job" (top right, green button)

## STEP 3: CONFIGURE JOB SETTINGS
- Job Settings Tab:
- General:
- Job Name: Healthcare Daily Transform
- Description: Daily transformation of healthcare data after Snowpipe loads
- Environment: Select Production (or your prod environment)
- Execution Settings:
- Commands to run: (in order)
- dbt run
- dbt test
- dbt docs generate
- Generate docs on run (check this box)

##  STEP 4: SET UP SCHEDULE**

### **Triggers Tab:**

**Schedule:**
- **Run on schedule:**  Enable this toggle
- **Timing:**

**Choose one:**

### **Option A: Daily at 3 AM EST (Recommended)**
```
Cron: Custom
Custom cron: 0 7 * * *
```
*(7 UTC = 3 AM EST)*

---

### **Option B: Multiple Times Daily**
```
Every 6 hours: 0 */6 * * *
Every 4 hours: 0 */4 * * *
```

---

### **Option C: After Business Hours**
```
6 PM EST daily: 0 22 * * *
```

---

## **STEP 5: ADVANCED SETTINGS (OPTIONAL)**

**Advanced Settings:**

**Threads:** `4` (parallel execution)

**Target name:** `prod`

**Run timeout:** `0` (no timeout, or set to `60` for 1 hour max)

**Defer to a previous run state:** Leave unchecked (unless you have incremental models)

---

## **🔧 STEP 6: NOTIFICATIONS (OPTIONAL)**

**Notifications Tab:**

**Email notifications:**
- ✅ **Send email on failure**
- ✅ **Send email on success** (optional)

**Add your email address**

**Slack notifications (if you have Slack integration):**
- Configure Slack channel for alerts

---

## ** STEP 7: SAVE AND TEST**

1. **Click "Save"** at the bottom

2. **Test the job immediately:**
   - Click **"Run now"** button
   - Watch it execute in real-time
   - Check for success 

3. **Verify the schedule:**
   - Check "Next Run" time shown in the job details
   - Should show next scheduled time (e.g., "Tomorrow at 3:00 AM")

---



# DBT TRIGGERED BY STEP FUNCTION

```
Files arrive in Google Drive
    ↓
Lambda syncs to S3
    ↓
Step Functions starts
    ↓
Snowpipe loads data
    ↓
 Trigger dbt Cloud job (NEW!)
    ↓
dbt transforms data
    ↓
Dashboard shows fresh data

```

# STEP 1: GET dbt CLOUD API TOKEN

In dbt Cloud:

Click your profile picture (top right)
Account Settings
API Access (or Service Tokens)
Click "Create Token" or "New Service Token"

Fill in:

Token name: Step Functions Trigger
Permissions: Select "Job Admin" or "Member"


Click "Save"
COPY THE TOKEN (you'll only see it once!)

Looks like: dbt_abc123xyz...




# STEP 2: GET dbt JOB ID
In dbt Cloud:

Go to Deploy → Jobs
Create a new job (if you haven't):

Name: Healthcare Transform - API Triggered
Environment: Production
Commands:

dbt run
dbt test

Triggers: UNCHECK "Run on schedule" (we'll trigger via API!)
Save


Get the Job ID:

Click on the job name
Look at the URL: https://cloud.getdbt.com/deploy/[ACCOUNT_ID]/projects/[PROJECT_ID]/jobs/[JOB_ID]
Copy the JOB_ID number (e.g., 123456)

# STEP 3: GET dbt ACCOUNT ID
From the same URL, copy the ACCOUNT_ID (the first number)

# STEP 4: STORE CREDENTIALS IN AWS SECRETS MANAGER
Go to AWS Secrets Manager:

Click "Store a new secret"
Secret type: Other type of secret
Key/value pairs:

json{
  "api_token": "dbt_abc123xyz...",
  "account_id": "12345",
  "job_id": "67890"
}

Secret name: dbt/cloud/api
Create secret

# STEP 5: CREATE LAMBDA FUNCTION
Go to AWS Lambda → Create function:
Settings:

Name: healthcare-trigger-dbt
Runtime: Python 3.11
Execution role: HealthcareDriveIngestionLambdaRole

```python

import json
import boto3
import urllib3
import os

secrets_client = boto3.client('secretsmanager')
http = urllib3.PoolManager()

def get_dbt_credentials():
    """Get dbt Cloud credentials from Secrets Manager"""
    response = secrets_client.get_secret_value(
        SecretId='dbt/cloud/api'
    )
    return json.loads(response['SecretString'])

def lambda_handler(event, context):
    """
    Trigger dbt Cloud job via API after Snowpipe completes
    """
    
    try:
        # Get credentials
        creds = get_dbt_credentials()
        api_token = creds['api_token']
        account_id = creds['account_id']
        job_id = creds['job_id']
        
        # dbt Cloud API endpoint
        url = f"https://cloud.getdbt.com/api/v2/accounts/{account_id}/jobs/{job_id}/run/"
        
        # Request headers
        headers = {
            'Authorization': f'Token {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Request body
        payload = {
            'cause': 'Triggered by Step Functions after Snowpipe load'
        }
        
        # Trigger dbt job
        print(f" Triggering dbt Cloud job {job_id}...")
        
        response = http.request(
            'POST',
            url,
            body=json.dumps(payload).encode('utf-8'),
            headers=headers
        )
        
        if response.status == 200 or response.status == 201:
            result = json.loads(response.data.decode('utf-8'))
            run_id = result['data']['id']
            run_url = result['data']['href']
            
            print(f" dbt job triggered successfully!")
            print(f"   Run ID: {run_id}")
            print(f"   URL: {run_url}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'message': 'dbt Cloud job triggered successfully',
                    'run_id': run_id,
                    'run_url': run_url
                })
            }
        else:
            error_msg = f"API returned status {response.status}: {response.data.decode('utf-8')}"
            print(f" Error: {error_msg}")
            
            return {
                'statusCode': response.status,
                'body': json.dumps({
                    'success': False,
                    'error': error_msg
                })
            }
        
    except Exception as e:
        print(f" Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

```
Click "Deploy"

# STEP 6: UPDATE STEP FUNCTIONS STATE MACHINE
Go to Step Functions → healthcare-data-pipeline-orchestrator → Edit

Add the new state AFTER SendSuccessNotification:

Update

```json

{
  "Comment": "Healthcare Data Pipeline Orchestration with dbt",
  "StartAt": "DebounceCheck",
  "States": {
    "DebounceCheck": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "healthcare-debounce-check",
        "Payload": {
          "bucket.$": "$.bucket",
          "prefix.$": "$.prefix",
          "date.$": "$.date"
        }
      },
      "ResultPath": "$.debounceResult",
      "Next": "ParseDebounceResult"
    },
    "ParseDebounceResult": {
      "Type": "Pass",
      "Parameters": {
        "bucket.$": "$.bucket",
        "prefix.$": "$.prefix",
        "date.$": "$.date",
        "debounceBody.$": "States.StringToJson($.debounceResult.Payload.body)"
      },
      "Next": "CheckAllFiles"
    },
    "CheckAllFiles": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.debounceBody.allFilesPresent",
          "BooleanEquals": true,
          "Next": "Wait30Seconds"
        }
      ],
      "Default": "WaitForMoreFiles"
    },
    "WaitForMoreFiles": {
      "Type": "Wait",
      "Seconds": 30,
      "Next": "DebounceCheck"
    },
    "Wait30Seconds": {
      "Type": "Wait",
      "Seconds": 30,
      "Comment": "Wait 30 seconds to ensure all files are fully written",
      "Next": "TriggerSnowpipe"
    },
    "TriggerSnowpipe": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "healthcare-trigger-snowpipe"
      },
      "ResultPath": "$.snowpipeResult",
      "Retry": [
        {
          "ErrorEquals": ["States.TaskFailed"],
          "IntervalSeconds": 10,
          "MaxAttempts": 3,
          "BackoffRate": 2.0
        }
      ],
      "Next": "WaitForSnowpipeProcessing"
    },
    "WaitForSnowpipeProcessing": {
      "Type": "Wait",
      "Seconds": 60,
      "Comment": "Wait for Snowpipe to process the files",
      "Next": "CheckSnowpipeStatus"
    },
    "CheckSnowpipeStatus": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "healthcare-check-snowpipe-status"
      },
      "ResultPath": "$.statusResult",
      "Next": "ParseStatusResult"
    },
    "ParseStatusResult": {
      "Type": "Pass",
      "Parameters": {
        "bucket.$": "$.bucket",
        "statusBody.$": "States.StringToJson($.statusResult.Payload.body)"
      },
      "Next": "EvaluateStatus"
    },
    "EvaluateStatus": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.statusBody.success",
          "BooleanEquals": true,
          "Next": "SendSuccessNotification"
        }
      ],
      "Default": "SendFailureNotification"
    },
    "SendSuccessNotification": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:healthcare-pipeline-notifications",
        "Subject": " Healthcare Pipeline Success - Triggering dbt",
        "Message.$": "States.Format('Healthcare data pipeline completed successfully!\n\nTimestamp: {}\n\nSnowpipe load complete. Now triggering dbt transformations...', $.statusBody.timestamp)"
      },
      "Next": "TriggerDbt"
    },
    "TriggerDbt": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "healthcare-trigger-dbt"
      },
      "ResultPath": "$.dbtResult",
      "Retry": [
        {
          "ErrorEquals": ["States.TaskFailed"],
          "IntervalSeconds": 10,
          "MaxAttempts": 2,
          "BackoffRate": 2.0
        }
      ],
      "Next": "WaitForDbt"
    },
    "WaitForDbt": {
      "Type": "Wait",
      "Seconds": 300,
      "Comment": "Wait 5 minutes for dbt to complete",
      "Next": "SendDbtCompleteNotification"
    },
    "SendDbtCompleteNotification": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:healthcare-pipeline-notifications",
        "Subject": " Complete Pipeline Success - dbt Finished",
        "Message": "Complete healthcare pipeline finished!\n\n Files synced from Google Drive\n Snowpipe loaded data\n dbt transformed data\n\nDashboard is now updated with fresh data!"
      },
      "Next": "PipelineSuccess"
    },
    "SendFailureNotification": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:healthcare-pipeline-notifications",
        "Subject": " Healthcare Pipeline Failed",
        "Message": "Healthcare data pipeline encountered errors! Please check CloudWatch logs and Snowflake for details."
      },
      "Next": "PipelineFailed"
    },
    "PipelineSuccess": {
      "Type": "Succeed"
    },
    "PipelineFailed": {
      "Type": "Fail",
      "Error": "PipelineExecutionFailed",
      "Cause": "Pipeline execution failed"
    }
  }
}
```

**Don't forget to replace `YOUR_ACCOUNT_ID`!**


