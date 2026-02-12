# What this will do

Test- it's only listing files from Google Drive, not downloading them.

## get_google_creds():

Retrieves Google OAuth credentials from AWS Secrets Manager
Creates a Google API credentials object

## lambda_handler():

Connects to Google Drive API
Lists files in the specified Google Drive folder
Prints file names, types, modified dates, and sizes to CloudWatch logs
Returns a JSON response with file count and names

```python

import os
import json
import boto3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# AWS clients
secrets = boto3.client("secretsmanager")

# Google scopes (read-only)
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_google_creds():
    """
    Reads OAuth refresh-token credentials from AWS Secrets Manager and builds Google Credentials.
    Secret must contain:
      - client_id
      - client_secret
      - refresh_token
    """
    secret_name = os.environ["GOOGLE_SECRET_NAME"]
    secret_str = secrets.get_secret_value(SecretId=secret_name)["SecretString"]
    secret = json.loads(secret_str)

    creds = Credentials(
        token=None,
        refresh_token=secret["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=secret["client_id"],
        client_secret=secret["client_secret"],
        scopes=SCOPES,
    )
    return creds

def lambda_handler(event, context):
    """
    Smoke test:
    - Auth to Google Drive using refresh token
    - List top N files inside DRIVE_FOLDER_ID
    """
    folder_id = os.environ["DRIVE_FOLDER_ID"]

    creds = get_google_creds()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    q = f"'{folder_id}' in parents and trashed=false"
    resp = service.files().list(
        q=q,
        fields="files(id,name,mimeType,modifiedTime,size)",
        pageSize=20
    ).execute()

    files = resp.get("files", [])

    print(f"✅ Google Drive connection OK. Found {len(files)} file(s) in folder: {folder_id}")
    for f in files:
        print(f"- {f.get('name')} | {f.get('mimeType')} | modified={f.get('modifiedTime')} | size={f.get('size')}")

    return {
        "statusCode": 200,
        "found": len(files),
        "sample_files": [f.get("name") for f in files[:10]]
    }


```
