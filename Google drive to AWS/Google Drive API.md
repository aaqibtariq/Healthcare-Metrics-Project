# Get Google Drive API Credentials (for AWS Lambda)

# Step 1 Create a Google Cloud Project
  
-  Create Gmail account if you dont have and sign up on Google Cloud free access for 3 months

-  Go to Google Cloud Console → https://console.cloud.google.com

-  Click Select Project → New Project

-  Name it something like:

-  healthcare-drive-ingestion

-  Create the project


# Step 2 Enable Google Drive API

- In the project, go to: APIs & Services → Library

- Search for Google Drive API

- Click Enable

# Step 3 Create OAuth Client ID

-  Go to: APIs & Services → Credentials

-  Click Create Credentials → OAuth client ID

-  Application type: Desktop App

-  Name: drive-lambda-client

-  Create

 Download or copy:

-  client_id

-  client_secret

# Step 4 Configure OAuth Consent Screen

Lambda cannot use API keys — OAuth is required.

-  Go to: APIs & Services → OAuth consent screen
-  Click Branding

-  User type: External

-  App name: Healthcare Drive Ingestion

-  User support email: your email

-  Developer contact info: your email

-  Save & continue

# Step 5 Add Test user

-  Go to: APIs & Services → OAuth consent screen
-  Click Audience
-  Publishing status - Testing
-  User type: External
-  Under Test users - Add your gmail

# Step 6 Generate a Refresh Token One time process

-  Run this once on your local machine

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": "PASTE_CLIENT_ID_HERE",
            "client_secret": "PASTE_CLIENT_SECRET_HERE",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    SCOPES
)

creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
print("ACCESS TOKEN:", creds.token)
print("REFRESH TOKEN:", creds.refresh_token)
```
-  This will open browser where you will sign in using your same test user email and authorize and get token
  
Note : prompt="consent"?

Google may return refresh_token = None if you already authorized the app previously.
prompt="consent" forces it to show the consent screen again and issue a refresh token.

After you get it 

Save these 3 values into AWS Secrets Manager:

```json
{
  "client_id": "...apps.googleusercontent.com",
  "client_secret": "....",
  "refresh_token": "...."
}

```
