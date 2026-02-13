# Lambda Executions

tatus: Succeeded
Test Event Name: test-drive-connection

Response:
{
  "statusCode": 200,
  "copied": 9,
  "skipped": 0,
  "reasons": {
    "new_file": 8,
    "modified": 1,
    "unchanged": 0
  },
  "state_key": "state/drive_checkpoint.json"
}

The area below shows the last 4 KB of the execution log.

Function Logs:
START RequestId: a7e6c06c-8326-4739-b151-7941a2ccaf5c Version: $LATEST
Found 9 CSV file(s) to consider in folder.
🔄 Processing (new_file): NH_QualityMsr_Claims_Oct2024.csv
✅ Uploaded to s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-13/NH_QualityMsr_Claims_Oct2024.csv
🔄 Processing (new_file): NH_QualityMsr_MDS_Oct2024.csv
✅ Uploaded to s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-13/NH_QualityMsr_MDS_Oct2024.csv
🔄 Processing (new_file): FY_2024_SNF_VBP_Facility_Performance.csv
✅ Uploaded to s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-13/FY_2024_SNF_VBP_Facility_Performance.csv
🔄 Processing (new_file): Skilled_Nursing_Facility_Quality_Reporting_Program_Provider_Data_Oct2024.csv
✅ Uploaded to s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-13/Skilled_Nursing_Facility_Quality_Reporting_Program_Provider_Data_Oct2024.csv
🔄 Processing (modified): NH_ProviderInfo_Oct2024.csv
✅ Uploaded to s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-13/NH_ProviderInfo_Oct2024.csv
🔄 Processing (new_file): NH_StateUSAverages_Oct2024.csv
✅ Uploaded to s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-13/NH_StateUSAverages_Oct2024.csv
🔄 Processing (new_file): NH_CovidVaxAverages_20241027.csv
✅ Uploaded to s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-13/NH_CovidVaxAverages_20241027.csv
🔄 Processing (new_file): Swing_Bed_SNF_data_Oct2024.csv
✅ Uploaded to s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-13/Swing_Bed_SNF_data_Oct2024.csv
🔄 Processing (new_file): PBJ_Daily_Nurse_Staffing_Q2_2024.csv
✅ Uploaded to s3://healthcare-metrics-project-at/landing/google_drive/load_dt=2026-02-13/PBJ_Daily_Nurse_Staffing_Q2_2024.csv
SUMMARY: copied=9, skipped=0, reasons={'new_file': 8, 'modified': 1, 'unchanged': 0}
END RequestId: a7e6c06c-8326-4739-b151-7941a2ccaf5c
REPORT RequestId: a7e6c06c-8326-4739-b151-7941a2ccaf5c	Duration: 34014.55 ms	Billed Duration: 35444 ms	Memory Size: 512 MB	Max Memory Used: 444 MB	Init Duration: 1428.68 ms

Request ID: a7e6c06c-8326-4739-b151-7941a2ccaf5c


# Testing Incremental ( Test same again and passed test)

Status: Succeeded
Test Event Name: test-drive-connection

Response:
{
  "statusCode": 200,
  "copied": 0,
  "skipped": 9,
  "reasons": {
    "new_file": 0,
    "modified": 0,
    "unchanged": 9
  },
  "state_key": "state/drive_checkpoint.json"
}

The area below shows the last 4 KB of the execution log.

Function Logs:
START RequestId: 44cc2e90-96c7-4b0f-8e26-41b741012369 Version: $LATEST
Found 9 CSV file(s) to consider in folder.
⏭️ Skipping unchanged: NH_QualityMsr_Claims_Oct2024.csv
⏭️ Skipping unchanged: NH_QualityMsr_MDS_Oct2024.csv
⏭️ Skipping unchanged: FY_2024_SNF_VBP_Facility_Performance.csv
⏭️ Skipping unchanged: Skilled_Nursing_Facility_Quality_Reporting_Program_Provider_Data_Oct2024.csv
⏭️ Skipping unchanged: NH_ProviderInfo_Oct2024.csv
⏭️ Skipping unchanged: NH_StateUSAverages_Oct2024.csv
⏭️ Skipping unchanged: NH_CovidVaxAverages_20241027.csv
⏭️ Skipping unchanged: Swing_Bed_SNF_data_Oct2024.csv
⏭️ Skipping unchanged: PBJ_Daily_Nurse_Staffing_Q2_2024.csv
SUMMARY: copied=0, skipped=9, reasons={'new_file': 0, 'modified': 0, 'unchanged': 9}
END RequestId: 44cc2e90-96c7-4b0f-8e26-41b741012369
REPORT RequestId: 44cc2e90-96c7-4b0f-8e26-41b741012369	Duration: 660.77 ms	Billed Duration: 661 ms	Memory Size: 512 MB	Max Memory Used: 444 MB

Request ID: 44cc2e90-96c7-4b0f-8e26-41b741012369
