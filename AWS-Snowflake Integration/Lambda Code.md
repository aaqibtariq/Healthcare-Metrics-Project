
## Update Lambda Environment Variables

- DDB_FILE_TABLE_NAME = healthcare_file_ingestion_state
- DDB_EXEC_TABLE_NAME = healthcare_pipeline_execution_state

## Updated Lambda Code 

it has following 

- DynamoDB Integration
- File State Tracking
- Pipeline Execution Tracking
```python

import os
import json
import io
from datetime import datetime, timezone
import hashlib

import boto3
from botocore.exceptions import ClientError

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ---------- AWS clients ----------
s3 = boto3.client("s3")
secrets = boto3.client("secretsmanager")
dynamodb = boto3.resource("dynamodb")

# ---------- Config from env ----------
S3_BUCKET = os.environ["S3_BUCKET"]
RAW_PREFIX = os.environ.get("RAW_PREFIX", "landing").strip("/")
STATE_KEY = os.environ.get("STATE_KEY", "state/drive_checkpoint.json")
GOOGLE_SECRET_NAME = os.environ["GOOGLE_SECRET_NAME"]
DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]

ALLOWLIST = [
    x.strip() for x in os.environ.get("ALLOWLIST", "").split(",") if x.strip()
]

# DynamoDB tables (env var recommended)
DDB_FILE_TABLE_NAME = os.environ.get("DDB_FILE_TABLE_NAME", "healthcare_file_ingestion_state")
DDB_EXEC_TABLE_NAME = os.environ.get("DDB_EXEC_TABLE_NAME", "healthcare_pipeline_execution_state")

file_state_table = dynamodb.Table(DDB_FILE_TABLE_NAME)
execution_table = dynamodb.Table(DDB_EXEC_TABLE_NAME)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_google_creds():
    secret_str = secrets.get_secret_value(SecretId=GOOGLE_SECRET_NAME)["SecretString"]
    secret = json.loads(secret_str)

    # Secret must contain: client_id, client_secret, refresh_token
    return Credentials(
        token=None,
        refresh_token=secret["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=secret["client_id"],
        client_secret=secret["client_secret"],
        scopes=SCOPES,
    )


def load_state():
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=STATE_KEY)
        return json.loads(obj["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
            return {"last_run": None, "files": {}}
        raise


def save_state(state):
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=STATE_KEY,
        Body=json.dumps(state, indent=2).encode("utf-8"),
        ContentType="application/json",
    )


def should_process(file_info, state):
    name = file_info["name"]
    modified = file_info.get("modifiedTime")

    prev = state["files"].get(name)
    if not prev:
        return True, "new_file"

    last_drive_modified = prev.get("drive_modifiedTime")
    if (not last_drive_modified) or (modified and modified > last_drive_modified):
        return True, "modified"

    return False, "unchanged"


def download_file(service, file_id):
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    return buf.getvalue()


def upload_to_s3(data: bytes, filename: str, load_dt: str):
    """
    Upload the file to S3 and return both key + full s3 uri.
    """
    s3_key = f"{RAW_PREFIX}/google_drive/load_dt={load_dt}/{filename}"
    s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=data)
    s3_uri = f"s3://{S3_BUCKET}/{s3_key}"
    return s3_key, s3_uri


def log_file_to_dynamodb(file_metadata: dict):
    """
    Log file ingestion to DynamoDB (non-blocking).
    """
    try:
        file_state_table.put_item(
            Item={
                "file_id": file_metadata["file_id"],
                "file_name": file_metadata["file_name"],
                "source_path": file_metadata.get("source_path", ""),
                "s3_location": file_metadata["s3_location"],
                "last_modified": file_metadata.get("last_modified", ""),
                "ingestion_timestamp": utc_now_iso(),
                "file_size": int(file_metadata.get("file_size", 0)),
                "status": file_metadata.get("status", "INGESTED"),
                "checksum": file_metadata.get("checksum", ""),
                "load_dt": file_metadata.get("load_dt", ""),
                "execution_id": file_metadata.get("execution_id", "")
            }
        )
        print(f"✅ Logged file to DynamoDB: {file_metadata['file_name']}")
    except Exception as e:
        print(f"⚠️ DynamoDB file log failed (continuing): {str(e)}")


def list_drive_files(service):
    q = f"'{DRIVE_FOLDER_ID}' in parents and trashed=false and mimeType='text/csv'"
    resp = service.files().list(
        q=q,
        fields="files(id,name,mimeType,modifiedTime,size,md5Checksum)",
        pageSize=1000
    ).execute()
    return resp.get("files", [])


def lambda_handler(event, context):
    # --------- Pipeline Execution Tracking (START) ---------
    execution_id = f"ingestion_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    try:
        execution_table.put_item(
            Item={
                "execution_id": execution_id,
                "start_time": utc_now_iso(),
                "status": "RUNNING",
                "files_processed": 0,
                "file_list": []
            }
        )
        print(f"🚀 Pipeline execution started: {execution_id}")
    except Exception as e:
        # Don't block the pipeline if execution logging fails
        print(f"⚠️ Could not write execution START to DynamoDB (continuing): {str(e)}")

    # --------- Existing pipeline logic ---------
    run_ts = utc_now_iso()
    load_dt = run_ts[:10]  # YYYY-MM-DD

    files_uploaded_to_s3 = []

    try:
        # Load state (incremental checkpoint)
        state = load_state()

        creds = get_google_creds()
        service = build("drive", "v3", credentials=creds, cache_discovery=False)

        files = list_drive_files(service)

        # Optional allowlist filter
        if ALLOWLIST:
            files = [f for f in files if f["name"] in ALLOWLIST]

        print(f"Found {len(files)} CSV file(s) to consider in folder.")
        copied = 0
        skipped = 0
        reasons = {"new_file": 0, "modified": 0, "unchanged": 0}

        for f in files:
            name = f["name"]
            file_id = f["id"]

            ok, reason = should_process(f, state)
            reasons[reason] += 1

            if not ok:
                print(f"⏭️ Skipping unchanged: {name}")
                skipped += 1
                continue

            print(f"🔄 Processing ({reason}): {name}")
            data = download_file(service, file_id)

            # Upload to S3
            s3_key, s3_uri = upload_to_s3(data, name, load_dt)
            print(f"✅ Uploaded to {s3_uri}")

            # Local checksum (optional)
            local_checksum = hashlib.md5(data).hexdigest()

            # Log to DynamoDB after successful S3 upload
            file_metadata = {
                "file_id": file_id,
                "file_name": name,
                "source_path": f"google_drive/{name}",
                "s3_location": s3_uri,
                "last_modified": f.get("modifiedTime", ""),
                "file_size": int(f.get("size", 0) or 0),
                "checksum": f.get("md5Checksum", "") or local_checksum,
                "status": "INGESTED",
                "load_dt": load_dt,
                "execution_id": execution_id
            }
            log_file_to_dynamodb(file_metadata)

            files_uploaded_to_s3.append({"name": name, "s3_key": s3_key})

            # update S3 state for this file
            state["files"][name] = {
                "file_id": file_id,
                "drive_modifiedTime": f.get("modifiedTime"),
                "last_processed": run_ts,
                "last_s3_key": s3_key,
            }
            copied += 1

        state["last_run"] = run_ts
        save_state(state)

        # --------- Pipeline Execution Tracking (SUCCESS) ---------
        try:
            execution_table.update_item(
                Key={"execution_id": execution_id},
                UpdateExpression="SET #status = :status, end_time = :end_time, files_processed = :count, file_list = :files",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": "SUCCESS",
                    ":end_time": utc_now_iso(),
                    ":count": len(files_uploaded_to_s3),
                    ":files": [f["name"] for f in files_uploaded_to_s3],
                }
            )
            print(f"✅ Pipeline execution SUCCESS: {execution_id}")
        except Exception as e:
            print(f"⚠️ Could not write execution SUCCESS to DynamoDB (continuing): {str(e)}")

        print(f"SUMMARY: copied={copied}, skipped={skipped}, reasons={reasons}")
        return {
            "statusCode": 200,
            "execution_id": execution_id,
            "copied": copied,
            "skipped": skipped,
            "reasons": reasons,
            "state_key": STATE_KEY,
            "ddb_file_table": DDB_FILE_TABLE_NAME,
            "ddb_exec_table": DDB_EXEC_TABLE_NAME
        }

    except Exception as e:
        # --------- Pipeline Execution Tracking (FAILED) ---------
        try:
            execution_table.update_item(
                Key={"execution_id": execution_id},
                UpdateExpression="SET #status = :status, end_time = :end_time, error_message = :error",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": "FAILED",
                    ":end_time": utc_now_iso(),
                    ":error": str(e),
                }
            )
            print(f"❌ Pipeline execution FAILED: {execution_id}")
        except Exception as ee:
            print(f"⚠️ Could not write execution FAILED to DynamoDB: {str(ee)}")

        print(f"Pipeline execution failed: {execution_id}, Error: {str(e)}")
        raise
```
