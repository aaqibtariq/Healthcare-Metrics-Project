## Use of code
## 1. Incremental Loading 

Tracks which files have been processed before in a state file stored in S3
Only downloads files that are:

New (never seen before)
Modified (changed since last download)


Skips unchanged files to save time and costs

## 2. State Management

Stores a checkpoint file at s3://your-bucket/state/drive_checkpoint.json
Tracks:

Last time each file was processed
Google Drive modification timestamp
S3 location of last upload



## 3. Partitioned S3 Storage

Organizes files by date: landing/google_drive/load_dt=2026-02-12/filename.csv
This format is Snowflake/Snowpipe friendly for automatic data warehouse loading

## 4. Allowlist Filtering

Can filter which files to process using ALLOWLIST environment variable
Example: ALLOWLIST=NH_ProviderInfo_Oct2024.csv,other_file.csv

## 5. CSV-Only

Only processes CSV files: mimeType='text/csv'
Skips Google Docs, PDFs, etc.


```python

import os
import json
import io
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ---------- AWS clients ----------
s3 = boto3.client("s3")
secrets = boto3.client("secretsmanager")

# ---------- Config from env ----------
S3_BUCKET = os.environ["S3_BUCKET"]
RAW_PREFIX = os.environ.get("RAW_PREFIX", "landing").strip("/")
STATE_KEY = os.environ.get("STATE_KEY", "state/drive_checkpoint.json")
GOOGLE_SECRET_NAME = os.environ["GOOGLE_SECRET_NAME"]
DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]

ALLOWLIST = [
    x.strip() for x in os.environ.get("ALLOWLIST", "").split(",") if x.strip()
]

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
    # Partition by load date for Snowflake/Snowpipe friendliness
    s3_key = f"{RAW_PREFIX}/google_drive/load_dt={load_dt}/{filename}"
    s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=data)
    return s3_key


def list_drive_files(service):
    q = f"'{DRIVE_FOLDER_ID}' in parents and trashed=false and mimeType='text/csv'"
    resp = service.files().list(
        q=q,
        fields="files(id,name,mimeType,modifiedTime,size)",
        pageSize=1000
    ).execute()
    return resp.get("files", [])


def lambda_handler(event, context):
    run_ts = utc_now_iso()
    load_dt = run_ts[:10]  # YYYY-MM-DD

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
            print(f" Skipping unchanged: {name}")
            skipped += 1
            continue

        print(f" Processing ({reason}): {name}")
        data = download_file(service, file_id)
        s3_key = upload_to_s3(data, name, load_dt)
        print(f" Uploaded to s3://{S3_BUCKET}/{s3_key}")

        # update state for this file
        state["files"][name] = {
            "file_id": file_id,
            "drive_modifiedTime": f.get("modifiedTime"),
            "last_processed": run_ts,
            "last_s3_key": s3_key,
        }
        copied += 1

    state["last_run"] = run_ts
    save_state(state)

    print(f"SUMMARY: copied={copied}, skipped={skipped}, reasons={reasons}")
    return {
        "statusCode": 200,
        "copied": copied,
        "skipped": skipped,
        "reasons": reasons,
        "state_key": STATE_KEY
    }

```
