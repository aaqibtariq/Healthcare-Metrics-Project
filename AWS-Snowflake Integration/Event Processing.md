# Event Processing -  Enable S3 Event Notifications to EventBridge

## Why This Step:

S3 needs to notify EventBridge when new files arrive so the pipeline can automatically trigger. Every S3 action (PutObject, DeleteObject, etc.) in this bucket will now generate an EventBridge event.

## Enabe Amazon EventBridge:
 - Open AWS Console → S3
 - Navigate to your bucket
 - Click on the "Properties" tab
 - Scroll down to "Event notifications"
 - Find the section "Amazon EventBridge"
 - Click "Edit"
 - Enable "Send notifications to Amazon EventBridge for all events in this bucket"
 - Click "Save changes"

## Create EventBridge Rule

- Open AWS Console → Amazon EventBridge
- Click "Rules" in the left sidebar
- Click "Create rule"
- Configure Basic Details:
```json
Name: healthcare-s3-file-arrival-trigger
Description: Triggers data pipeline when files land in S3 landing zone
Event bus: default
Rule type: Rule with an event pattern
```
Under Event -> Select 
- S3 Object store
- Click Event Pattern Filler
- On right side under Event pattern (filter) Enter this json code

```json

{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {
      "name": ["healthcare-namet"]
    },
    "object": {
      "key": [{
        "prefix": "landing/google_drive/"
      }]
    }
  }
}
```
- Scroll down and click on Test event pattern - optional
- Click Use Own Event
- Enter this
```json
{
  "version": "0",
  "id": "test-event-123",
  "detail-type": "Object Created",
  "source": "aws.s3",
  "account": "number",
  "time": "2024-02-25T10:00:00Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:s3:::healthcare-name"
  ],
  "detail": {
    "version": "0",
    "bucket": {
      "name": "healthcare-name"
    },
    "object": {
      "key": "landing/google_drive/load_dt=2024-02-25/test-file.csv",
      "size": 1024,
      "etag": "d4****",
      "sequencer": "0061****"
    },
    "request-id": "C3D13FE****",
    "requester": "123456****",
    "source-ip-address": "192.***",
    "reason": "PutObject"
  }
}
```
- Click Run Test
- It should Display "The test event(s) matches the Event pattern (filter)."
- For Target Select - CloudWatch log group for now instead of Step Function
- Log group name: /aws/events/healthcare-pipeline-test -> Retention: 1 day
- Create

## Test

- Upload any csv in your S3 bucket for test  > s3://healthcare-name/landing/google_drive/test.csv
- Go to EventBridge → Rules → Your rule
- Click "Metrics" tab
- You should see "Invocations" count = 1 after 1-2 minutes
- Also CloudWatch → Log groups → /aws/events/healthcare-pipeline-test
- You can delete this Log group test once you setup Step Function

## Note

## **STEP 5.3: Add Batching/Debounce Configuration**

### **Why This Step:**
Prevent multiple pipeline executions when several files arrive simultaneously.

### **Instructions:**

**Note:** EventBridge doesn't have built-in batching, so we'll implement this in DynamoDB state tracking  and in Step Functions 

For now, just document the intended behavior:

**- Create a note in your documentation:**
```
Batching Strategy:
- EventBridge will fire for each file arrival
- Step Functions will implement debounce logic using DynamoDB
- If pipeline executed in last 5 minutes, skip execution
- This batches multiple file arrivals into single pipeline run
```

This will be implemented in next Phase 
