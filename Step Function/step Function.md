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

# STATE MACHINE Code
```sql

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
