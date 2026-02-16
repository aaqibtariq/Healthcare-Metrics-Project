
# Architecture

Google Drive → AWS Lambda (Python)
-   reads credentials from AWS Secrets Manager
-   writes files to Amazon S3 using AWS IAM role
-   maintains “what was already processed” using a state file in S3 (simple + serverless)

# Note

As we have reuirments of Incremental data/file” Means Here

So we either get 

new files (not seen before), or

updated files (modifiedTime changed)

We do this by storing a lightweight checkpoint like:

last run timestamp, and/or

processed file IDs + modifiedTime

Easiest reliable approach: S3 state file (state/drive_checkpoint.json)

# Step 1 AWS Secret Manager

- Open Secret Manager
- Click store a new secret
- Create a secret named: google/drive/Name
- Secret value (JSON):
```
{
  "client_id": "xxxxx.apps.googleusercontent.com",
  "client_secret": "xxxxx",
  "refresh_token": "xxxxx"
}
```

# Step 2 - S3 Buckets 

-  Aws Console -> S3 -> Create Bucket

-  {Bucket Name}

-  Create Folder 

-  Raw files/



# Step 3 - IAM Role & Policy

## Create Policy

```Json
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
        "arn:aws:s3:::{Bucket Name}",
        "arn:aws:s3:::{Bucket Name}/*"
      ]
    },
    {
      "Sid": "ReadGoogleDriveSecret",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:{Name}*"
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
Name - HealthcareDriveIngestionPolicy

## Create Role

-  Go to IAM → Roles → Create role
-  Trusted entity  -> AWS service
-  Use case: Lambda
-  Click Next
-  Attach HealthcareDriveIngestionPolicy 
-  Role Name - HealthcareDriveIngestionLambdaRole
-  Disciption: Execution role for Lambda that ingests files from Google Drive into S3
-  Create Role

# Step 4 - Lambda

-  Lambda → Functions → Create function
-  Name: healthcare-drive-to-s3-ingestion
-  Runtime: Python 3.11
-  Architecture: x86_64
-  Select: Use an existing role - HealthcareDriveIngestionLambdaRole
-  Click Create function

## Add Environment Variables


-  Go to: Configuration → Environment variables → Edit

-  Add these:

-  S3_BUCKET = { bucket name } 

-  RAW_PREFIX = landing

-  STATE_KEY = state/drive_checkpoint.json

-  GOOGLE_SECRET_NAME = {name get it from Secret Manager}

-  DRIVE_FOLDER_ID = <your Google Drive folder id>

It will look like this:
```
https://drive.google.com/drive/folders/1AbCDefGhIJkLmNoPQRstuVW
DRIVE_FOLDER_ID = 1AbCDefGhIJkLmNoPQRstuVW
```

-  ALLOWLIST = {list csv files like fileone.csv, filetwo.csv}

-  Click Save.


## Increase Timeout + Memory 

-  Go to: Configuration → General configuration → Edit

-  Timeout: 2 minutes (120 seconds)

-  Memory: 512 MB (or 1024 MB if files are big)

-  Click Save.

## Upload Layer to Lambda

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/Google%20drive%20to%20AWS/google_layer.zip 

-  Go to Lambda Console → Layers (left sidebar)
-  Click Create layer
Fill in:

-  Name: google-drive-deps
-  Upload: Choose google_layer.zip
-  Compatible runtimes: Select Python 3.11
-  Compatible architectures: Select x86_64
-  Click Create

##  Attach Layer to Your Function

-  Go to your Lambda function
-  Scroll down to Layers
-  Click Add a layer
-  Select Custom layers
-  Choose google-drive-deps (version 1)
-  Click Add

## Test Code

Add this test code 

https://github.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/Google%20drive%20to%20AWS/Lambda%20Test%20code.md

- Click Deploy
- Nothing is needed in test event connection you can just give it any name and put {} in Json
- Click Test


