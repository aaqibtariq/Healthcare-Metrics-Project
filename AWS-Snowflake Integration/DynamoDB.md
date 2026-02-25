## Why This Step

Track pipeline execution metadata to implement debounce logic and monitoring.

## Create DynamoDB Table - Pipeline Execution State

- Open AWS Console → DynamoDB
- Click "Create table"
- Configure table settings
- Table name: healthcare_pipeline_execution_state
- Partition key: execution_id (String)
- Sort key: [Leave empty]
- Table settings -> DynamoDB Standard
- Capacity mode -> On-demand or Provisioned -> Read capacity: 5 units and Write capacity: 5 units
-  Encryption -> Encryption at rest: Owned by Amazon DynamoDB
-  Tags (optional)
-  Create

### This table will store:
Table Schema (Attributes to be added by Lambda)
- `execution_id` (Partition Key) - Unique ID for each pipeline run (e.g., "run_20240224_143022")
- `start_time` - ISO timestamp when pipeline started
- `end_time` - ISO timestamp when pipeline completed
- `status` - "RUNNING" | "SUCCESS" | "FAILED"
- `files_processed` - Number of files in this run
- `file_list` - Array of filenames processed
- `snowpipe_status` - Status of Snowpipe ingestion
- `dbt_run_id` - dbt Cloud job run ID
- `error_message` - Error details if failed

## Create DynamoDB Table - File Ingestion State

- DynamoDB Console → Click "Create table
- Table name: healthcare_file_ingestion_state
- Partition key: file_id (String)
- Sort key: [Leave empty]
- Table settings -> DynamoDB Standard
- Capacity mode: On-demand
- Encryption at rest: Owned by Amazon DynamoDB
- Tags (optional)
- Create

## Update Lambda IAM Role - Add DynamoDB Permissions

Lambda needs permission to read/write to the new DynamoDB tables.

### Role update

- Open AWS Console → IAM
- Click "Roles" in left sidebar
- Search for your Lambda role - > HealthcareDriveIngestionLambdaRole
- Click on the role name
- Click "Add permissions" → "Create inline policy
- Click JSON tab and paste:

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
        "arn:aws:dynamodb:us-east-1:YOUR_ACCOUNT_ID:table/healthcare_pipeline_execution_state",
        "arn:aws:dynamodb:us-east-1:YOUR_ACCOUNT_ID:table/healthcare_file_ingestion_state"
      ]
    }
  ]
}
```

**IMPORTANT:** Replace:
- `YOUR_ACCOUNT_ID` with your actual AWS account ID
- `us-east-1` with your region if different

- Click "Next"
- Policy name: HealthcareDynamoDBAccessPolicy
- Click "Create policy


## Update Lambda Code

This will be updated 

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/Google%20drive%20to%20AWS/Google%20drive%20to%20S3.md

Update Lambda Code - Add DynamoDB State Tracking

Why This Step:

Lambda should log file ingestion state to DynamoDB for tracking and debugging.

### Add DynamoDB client at the top
```python
import boto3
import json
from datetime import datetime
import hashlib

# Existing imports...
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')  # ADD THIS

# Table references
file_state_table = dynamodb.Table('healthcare_file_ingestion_state')  # ADD THIS

```

### Add helper function to log file state

```python

def log_file_to_dynamodb(file_metadata):
    """
    Log file ingestion to DynamoDB
    
    Args:
        file_metadata: Dict containing file information
    """
    try:
        file_state_table.put_item(
            Item={
                'file_id': file_metadata['file_id'],
                'file_name': file_metadata['file_name'],
                'source_path': file_metadata.get('source_path', ''),
                's3_location': file_metadata['s3_location'],
                'last_modified': file_metadata['last_modified'],
                'ingestion_timestamp': datetime.now().isoformat(),
                'file_size': file_metadata.get('file_size', 0),
                'status': 'INGESTED',
                'checksum': file_metadata.get('checksum', '')
            }
        )
        print(f"Logged file to DynamoDB: {file_metadata['file_name']}")
    except Exception as e:
        print(f"Error logging to DynamoDB: {str(e)}")
        # Don't fail Lambda if DynamoDB write fails
```
### Update your file upload section to call this function

```python
# Inside your loop where you upload files to S3
for file in files_to_process:
    # ... existing upload code ...
    
    # After successful S3 upload, log to DynamoDB
    file_metadata = {
        'file_id': file['id'],  # Google Drive file ID
        'file_name': file['name'],
        'source_path': f"google_drive/{file['name']}",
        's3_location': f"s3://{bucket_name}/{s3_key}",
        'last_modified': file.get('modifiedTime', ''),
        'file_size': int(file.get('size', 0)),
        'checksum': file.get('md5Checksum', '')
    }
    
    log_file_to_dynamodb(file_metadata)
```

 - Deploy updated Lambda code
 - Save changes
 - Click "Deploy"
 - Trigger Lambda manually or wait for next scheduled run
 - Check CloudWatch Logs for: "Logged file to DynamoDB"

Verify DynamoDB:

- DynamoDB Console → Tables → healthcare_file_ingestion_state
- Click "Explore table items"
- You should see entries for files that were uploaded


### Add Pipeline Execution Tracking

Track when the Lambda runs, even if no files are processed (for monitoring).

Add this at the start of your Lambda handler

def lambda_handler(event, context):
    # Generate execution ID
    execution_id = f"ingestion_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Reference to execution state table
    execution_table = dynamodb.Table('healthcare_pipeline_execution_state')
    
    # Log execution start
    execution_table.put_item(
        Item={
            'execution_id': execution_id,
            'start_time': datetime.now().isoformat(),
            'status': 'RUNNING',
            'files_processed': 0,
            'file_list': []
        }
    )
    
    print(f"Pipeline execution started: {execution_id}")
    
    try:
        # ... your existing Lambda logic ...
        
        # Count files processed
        files_processed_count = len(files_uploaded_to_s3)
        
        # Log execution success
        execution_table.update_item(
            Key={'execution_id': execution_id},
            UpdateExpression='SET #status = :status, end_time = :end_time, files_processed = :count, file_list = :files',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'SUCCESS',
                ':end_time': datetime.now().isoformat(),
                ':count': files_processed_count,
                ':files': [f['name'] for f in files_uploaded_to_s3]
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'execution_id': execution_id,
                'files_processed': files_processed_count
            })
        }
        
    except Exception as e:
        # Log execution failure
        execution_table.update_item(
            Key={'execution_id': execution_id},
            UpdateExpression='SET #status = :status, end_time = :end_time, error_message = :error',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'FAILED',
                ':end_time': datetime.now().isoformat(),
                ':error': str(e)
            }
        )
        
        print(f"Pipeline execution failed: {execution_id}, Error: {str(e)}")
        raise
```

- Deploy code
- Test Lambda
- Verify execution tracking
- DynamoDB → `healthcare_pipeline_execution_state` → Explore items
- You should see execution records with status, timestamps, file counts
