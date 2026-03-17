#  SCHEDULED TRIGGER 

- Set up a CloudWatch Events rule to run the Lambda on a schedule (e.g., every hour, every day).

Steps:

- 1. Go to Amazon EventBridge → Rules → Create rule
- 2. Configure:

- Name: healthcare-drive-sync-schedule
- Description: "Trigger Google Drive sync hourly"
- Event bus: default
- Rule type: Schedule
- 3. Schedule pattern: Choose one:
 
```
Hourly (recommended for testing):
Rate expression: rate(1 hour)
Daily at 2 AM EST:
Cron expression: cron(0 6 * * ? *)
(6 UTC = 2 AM EST)
Every 15 minutes (for frequent updates):
Rate expression: rate(15 minutes)
```
- 4. Select target:
  - Target: AWS Lambda function
  - Function: healthcare-drive-to-s3-ingestion
- 5. Create rule



Your Lambda will now run:

- Every hour (or whatever schedule you chose)
- Check Google Drive for new/modified files
- Download and upload to S3
- Trigger Step Functions automatically
- Complete pipeline runs end-to-end!


Note -

 OPTION B: GOOGLE DRIVE WEBHOOK (ADVANCED)

Set up real-time notifications from Google Drive when files change.

This requires:

- Google Drive API webhook setup
- API Gateway to receive webhooks
- Lambda to process webhook events
- More complex but instant triggers

