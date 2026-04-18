# How to Refresh YouTube Token

Your YouTube token has expired. Follow these simple steps to refresh it:

## Prerequisites

Make sure you have `client_secret.json` in this folder. If you don't have it:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID (select **Desktop app**)
3. Download the JSON file
4. Save it as `client_secret.json` in this folder

## Steps to Refresh Token

### Option 1: Using Batch File (Easiest)

1. **Double-click** `refresh_token.bat`
2. Press ENTER when prompted
3. Your browser will open for authentication
4. Sign in with your YouTube account
5. Grant permissions
6. Copy the encoded values shown in the console
7. Update Railway environment variables

### Option 2: Using Python Script

1. Open terminal/command prompt in this folder
2. Run:
   ```bash
   python refresh_youtube_token.py
   ```
3. Follow the on-screen instructions
4. Copy the encoded values
5. Update Railway environment variables

## What the Script Does

1. ✓ Deletes old expired token
2. ✓ Opens browser for YouTube authentication
3. ✓ Generates new `token.json`
4. ✓ Encodes credentials for Railway
5. ✓ Saves encoded values to `railway_credentials.txt`

## Update Railway

After running the script, you'll get two encoded values:

1. Go to [Railway Dashboard](https://railway.app/)
2. Select your project
3. Click on your service
4. Go to **Variables** tab
5. Update these variables:
   - `YOUTUBE_CLIENT_SECRET_B64` → paste first value
   - `YOUTUBE_TOKEN_JSON` → paste second value
6. Save and redeploy

## Troubleshooting

### "client_secret.json not found"
- Download OAuth credentials from Google Cloud Console
- Make sure it's named exactly `client_secret.json`
- Place it in the same folder as the script

### "redirect_uri_mismatch" error
- You created **Web app** credentials instead of **Desktop app**
- Delete the credentials in Google Cloud Console
- Create new ones as **Desktop app**
- Download and try again

### "Google API libraries not installed"
Run:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Files Created

After running the script, you'll have:
- `token.json` - Your new YouTube token (keep this safe!)
- `railway_credentials.txt` - Encoded values for Railway (you can delete after updating Railway)

## Security Note

- Never commit `token.json` or `client_secret.json` to GitHub
- These files are already in `.gitignore`
- The encoded values in Railway are safe to use

## Need Help?

If you encounter any issues, check:
1. You're using the correct Google account
2. YouTube Data API v3 is enabled in Google Cloud Console
3. OAuth consent screen is configured
4. You have the correct `client_secret.json` file
