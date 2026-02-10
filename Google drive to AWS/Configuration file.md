
# Step 1 Architecture

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
-  Create Role




