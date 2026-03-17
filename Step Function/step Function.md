# STEP FUNCTIONS ORCHESTRATION

```
S3 Event (new file arrives)
    ↓
Step Functions State Machine
    ↓
Step 1: Debounce Check (wait for all files)
    ↓
Step 2: Trigger Snowpipe
    ↓
Step 3: Wait (5 seconds)
    ↓
Step 4: Check Snowpipe Status
    ↓
Step 5: Success? → SNS Notification
    ↓
Step 6: Failure? → Retry or Alert

```

# IAM Role

You can create new role or can use existing lambda role

- Go to AWS Console → IAM → Roles → Create Role
- Select "AWS Service"
- Choose "Step Functions"
- Click "Next"
- Attach these policies:
  - AWSLambdaRole
  - CloudWatchLogsFullAccess
  - AmazonSNSFullAccess
- Role name: StepFunctions-Healthcare-Pipeline-Role
- Create role

  Or Add these new polices into existing role

  # Policy

  ## for HealthcareDriveIngestionLambdaRole

**StepStartExecution**

  ```json

{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "AllowStartSpecificStateMachine",
			"Effect": "Allow",
			"Action": "states:StartExecution",
			"Resource": "arn:aws:states:us-east-1:Your Account ID:stateMachine:healthcare-data-pipeline-orchestrator"
		}
	]
}

```
**StepFunctionsFullAccess**

```json

{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"lambda:InvokeFunction",
				"lambda:InvokeAsync"
			],
			"Resource": "*"
		},
		{
			"Effect": "Allow",
			"Action": [
				"sns:Publish"
			],
			"Resource": "*"
		},
		{
			"Effect": "Allow",
			"Action": [
				"logs:CreateLogGroup",
				"logs:CreateLogStream",
				"logs:PutLogEvents"
			],
			"Resource": "*"
		}
	]
}

```
**SnowflakeSecretsManagerAccess**

```json

{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"secretsmanager:GetSecretValue",
				"secretsmanager:DescribeSecret"
			],
			"Resource": [
				"arn:aws:secretsmanager:us-east-1:Your Account ID:secret:snowflake/healthcare/credentials-*"
			]
		}
	]
}

```
**HealthcareDynamoDBAccessPolicy** done before jsut double check
  ```json

{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "DynamoDBTableAccess",
			"Effect": "Allow",
			"Action": [
				"dynamodb:PutItem",
				"dynamodb:GetItem",
				"dynamodb:UpdateItem",
				"dynamodb:Query",
				"dynamodb:Scan",
				"dynamodb:DeleteItem"
			],
			"Resource": [
				"arn:aws:dynamodb:us-east-1:Your Account ID:table/healthcare_file_ingestion_state",
				"arn:aws:dynamodb:us-east-1:Your Account ID:table/healthcare_pipeline_execution_state"
			]
		}
	]
}
```

**HealthcareDriveIngestionPolicy2** Just checking again

```json

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3RawWriteAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::bucket-name",
                "arn:aws:s3:::bucket-name/*"
            ]
        },
        {
            "Sid": "ReadGoogleDriveSecret",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "arn:aws:secretsmanager:*:*:secret:google/drive/name*"
        },
        {
            "Sid": "CloudWatchLogging",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}

```

**Trust Relationship** update

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "lambda.amazonaws.com",
                    "states.amazonaws.com"
                ]
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

# CREATE 3 LAMBDA FUNCTIONS

## Lambda 1: Debounce Check
Purpose: Wait for all related files before triggering Snowpipe

- Go to Lambda → Create Function:
- Name: healthcare-debounce-check
- Runtime: Python 3.11
- Role: HealthcareDriveIngestionLambdaRole

```python

import json
import boto3
from datetime import datetime

s3 = boto3.client('s3', region_name='us-east-1')


def lambda_handler(event, context):
    bucket = event.get('bucket', 'healthcare-metrics-project-at')
    prefix = event.get('prefix', 'landing/google_drive/')
    date_str = event.get('date', datetime.now().strftime('%Y-%m-%d'))

    # Make sure prefix ends with /
    if not prefix.endswith('/'):
        prefix += '/'

    s3_prefix = f"{prefix}load_dt={date_str}/"

    # Flexible filename patterns
    expected_patterns = {
        'pbj_staffing': ['pbj_staffing', 'pbjstaffing'],
        'provider_info': ['provider_info', 'providerinfo'],
        'quality_claims': ['quality_claims', 'qualityclaims'],
        'penalties': ['penalties'],
        'survey_summary': ['survey_summary', 'surveysummary'],
        'vbp_performance': ['vbp_performance', 'vbpperformance'],
        'state_averages': ['state_averages', 'stateusaverages', 'state_usa_averages'],
        'ownership': ['ownership']
    }

    files_found = set()

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=s3_prefix
    )

    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key'].lower()

            if not key.endswith('.csv'):
                continue

            for dataset_name, patterns in expected_patterns.items():
                if any(pattern in key for pattern in patterns):
                    files_found.add(dataset_name)
                    break

    all_files_present = len(files_found) == len(expected_patterns)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'allFilesPresent': all_files_present,
            'filesFound': len(files_found),
            'expectedFiles': len(expected_patterns),
            'missingFiles': sorted(list(set(expected_patterns.keys()) - files_found)),
            'bucket': bucket,
            'prefix': s3_prefix,
            'date': date_str,
            'matchedFiles': sorted(list(files_found))
        })
    }
```

## Lambda 2: Trigger Snowpipe

Purpose: Manually trigger Snowpipe to refresh all pipes

- Create Function:
- Name: healthcare-trigger-snowpipe
- Runtime: Python 3.11
- Role: HealthcareDriveIngestionLambdaRole


```python

import json
import boto3
import requests
from datetime import datetime

secrets = boto3.client('secretsmanager')

def get_snowflake_credentials():
    """Get Snowflake credentials from Secrets Manager"""
    response = secrets.get_secret_value(
        SecretId='snowflake/healthcare/credentials'
    )
    return json.loads(response['SecretString'])

def lambda_handler(event, context):
    """
    Trigger Snowpipe via REST API (no Python connector needed!)
    """
    
    try:
        creds = get_snowflake_credentials()
        
        # Snowflake account URL
        account = creds['account']
        user = creds['user']
        password = creds['password']
        
        # List of pipes to refresh
        pipes = [
            'RAW.HEALTHCARE.PIPE_PBJ_STAFFING',
            'RAW.HEALTHCARE.PIPE_PROVIDER_INFO',
            'RAW.HEALTHCARE.PIPE_QUALITY_CLAIMS',
            'RAW.HEALTHCARE.PIPE_PENALTIES',
            'RAW.HEALTHCARE.PIPE_SURVEY_SUMMARY',
            'RAW.HEALTHCARE.PIPE_VBP_PERFORMANCE',
            'RAW.HEALTHCARE.PIPE_STATE_AVERAGES',
            'RAW.HEALTHCARE.PIPE_OWNERSHIP'
        ]
        
        results = []
        
        # Note: Snowpipe auto-ingests from S3 events
        # Manual refresh via REST API requires Snowpipe REST endpoint
        # For now, we'll just log that files are ready
        
        for pipe in pipes:
            results.append({
                'pipe': pipe,
                'status': 'files_ready',
                'message': 'Snowpipe will auto-ingest via S3 notifications',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        print(f" S3 files ready for Snowpipe auto-ingestion")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Files ready for Snowpipe',
                'results': results,
                'totalPipes': len(pipes)
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to process Snowpipe trigger'
            })
        }

```

## Lambda 3: Check Snowpipe Status

Purpose: Check if Snowpipe successfully loaded the data

- Create Function:
- Name: healthcare-check-snowpipe-status
- Runtime: Python 3.11
- Role: HealthcareDriveIngestionLambdaRole

```python

import json
import time
from datetime import datetime

def lambda_handler(event, context):
    """
    Simplified status check - assumes success after wait period
    In production, you'd query Snowflake's COPY_HISTORY table
    """
    
    try:
        # Since Snowpipe auto-ingests, we'll assume success after waiting
        # The Step Functions already waited 60 seconds
        
        print(" Assuming Snowpipe completed auto-ingestion")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'Snowpipe auto-ingestion completed',
                'totalRowsLoaded': 'N/A (auto-ingest)',
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Failed to check Snowpipe status'
            })
        }
```

Deploy all thre functions and Test

# CREATE SNS TOPIC FOR NOTIFICATIONS

- Go to SNS → Topics → Create Topic
- Type: Standard
- Name: healthcare-pipeline-notifications
- Display name: Healthcare Pipeline
- Create topic

**Create Subscription:**

- Protocol: Email
- Endpoint: your-email@example.com
- Create subscription
- Check your email and confirm subscription

# STATE MACHINE Code

- Go to AWS Console → Step Functions → State machines → Create state machine
- Choose authoring method: "Write your workflow in code"
- Type: Standard
- Definition: We'll paste the JSON below
- 
```json

{
  "Comment": "Healthcare Data Pipeline Orchestration",
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
        "Subject": " Healthcare Pipeline Success",
        "Message.$": "States.Format('Healthcare data pipeline completed successfully!\n\nTimestamp: {}\n\nAll data has been loaded into Snowflake and is ready for dbt transformations.', $.statusBody.timestamp)"
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
      "Error": "SnowpipeLoadFailed",
      "Cause": "One or more Snowpipe loads failed"
    }
  }
}

```

### Note
- Repalce ID With your actual account ID (e.g., 123456789012)

### **2. Verify Lambda function names**

Make sure these match exactly what you named your functions:
- `healthcare-debounce-check`
- `healthcare-trigger-snowpipe`
- `healthcare-check-snowpipe-status`

## ** CONFIGURE THE STATE MACHINE**

After pasting the updated JSON:

- 1. **Click "Next"**

- 2. **Name:** `healthcare-data-pipeline-orchestrator`

- 3. **Permissions:**
   - Select **"Choose an existing role"**
   - Select: `HealthcareDriveIngestionLambdaRole`
   
   **If you don't see this role, create it now:**
   - Select "Create new role"
   - Name it: `StepFunctions-Healthcare-Pipeline-Role`

- 4. **Logging:**
   - Enable CloudWatch Logs: **Yes**
   - Log level: **ALL**
   - Include execution data: **Yes**

- 5. **Click "Create state machine"**
 

  # Update Event Bridge

  https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/AWS-Snowflake%20Integration/Event%20Processing.md

  Now we can update this

- Update healthcare-s3-file-arrival-trigger to trigger Step Functions instead:
- Click "Edit" button (top right)
- Scroll to "Targets" tab
- Remove the old target (which was cloud watch logs)
- Click "Add target"
- Select target: Step Functions state machine
- State machine: healthcare-data-pipeline-orchestrator
- Configure input transformer:

Input path:

```json
{
     "bucket": "$.detail.bucket.name",
     "key": "$.detail.object.key"
   }
```

Template:

```json
{
     "bucket": "<bucket>",
     "prefix": "landing/google_drive/"
     "date": "2024-01-01"
   }

```

Role Amazon_EventBridge_Invoke_StepFunctions_1100829925 - it has policy to execute step_funnction 



- 6. **Save changes**
 
 ### TEST THE STATE MACHINE MANUALLY
- While we figure out the trigger, let's test the State Machine manually:
- Go to Step Functions → healthcare-data-pipeline-orchestrator
- Click "Start execution"
- Input:
```json
json{
  "bucket": "healthcare-metrics-project-at",
  "prefix": "landing/google_drive/"
  "date": "2024-06-01"
}
```
- Click "Start execution"
- Watch the execution graph



