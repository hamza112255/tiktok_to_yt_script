"""
YouTube Token Refresh Script
This script will help you authenticate with YouTube and generate a new token.json
Then it will automatically encode it for Railway deployment.
"""
import os
import sys
import json
import base64
from pathlib import Path

print("="*60)
print("YouTube Token Refresh & Railway Encoder")
print("="*60)
print()

# Check if client_secret.json exists
if not Path('client_secret.json').exists():
    print("❌ ERROR: client_secret.json not found!")
    print()
    print("Please download your OAuth credentials from Google Cloud Console:")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Create OAuth 2.0 Client ID (Desktop app)")
    print("3. Download the JSON file")
    print("4. Save it as 'client_secret.json' in this folder")
    print()
    sys.exit(1)

print("✓ Found client_secret.json")
print()

# Import YouTube API libraries
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    print("❌ ERROR: Google API libraries not installed!")
    print()
    print("Please install them with:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    print()
    sys.exit(1)

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

print("Starting YouTube authentication...")
print()
print("A browser window will open for you to:")
print("1. Select your Google account")
print("2. Grant YouTube upload permissions")
print("3. The browser will show 'Authentication successful'")
print()
input("Press ENTER to continue...")
print()

try:
    # Delete old token if exists
    token_file = Path('token.json')
    if token_file.exists():
        print("→ Removing old token.json...")
        token_file.unlink()
    
    # Start OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        SCOPES
    )
    
    print("→ Opening browser for authentication...")
    print()
    
    try:
        # Try to run local server (preferred method)
        creds = flow.run_local_server(
            port=0,
            access_type='offline',
            prompt='consent'
        )
    except Exception as e:
        print(f"⚠ Local server method failed: {e}")
        print("→ Trying console method...")
        print()
        # Fallback to console method
        creds = flow.run_console(
            access_type='offline',
            prompt='consent'
        )
    
    # Save the credentials
    token_file.write_text(creds.to_json(), encoding='utf-8')
    
    print()
    print("✓ Authentication successful!")
    print("✓ token.json created")
    print()
    
    # Check if refresh token is present
    if not creds.refresh_token:
        print("⚠ WARNING: No refresh token received!")
        print("  You may need to re-authenticate later.")
        print("  To fix: Delete token.json and run this script again.")
        print()
    else:
        print("✓ Refresh token obtained (token will auto-refresh)")
        print()
    
    # Now encode for Railway
    print("="*60)
    print("Encoding credentials for Railway...")
    print("="*60)
    print()
    
    # Read the files
    with open('client_secret.json', 'r', encoding='utf-8') as f:
        client_secret = f.read()
    
    with open('token.json', 'r', encoding='utf-8') as f:
        token = f.read()
    
    # Encode to base64
    client_secret_b64 = base64.b64encode(client_secret.encode('utf-8')).decode('utf-8')
    token_b64 = base64.b64encode(token.encode('utf-8')).decode('utf-8')
    
    print("✓ Credentials encoded successfully!")
    print()
    print("="*60)
    print("COPY THESE TO RAILWAY ENVIRONMENT VARIABLES")
    print("="*60)
    print()
    print("Variable Name: YOUTUBE_CLIENT_SECRET_B64")
    print("Value:")
    print(client_secret_b64)
    print()
    print("-"*60)
    print()
    print("Variable Name: YOUTUBE_TOKEN_JSON")
    print("Value:")
    print(token_b64)
    print()
    print("="*60)
    print()
    print("NEXT STEPS:")
    print("="*60)
    print("1. Go to Railway dashboard: https://railway.app/")
    print("2. Select your project")
    print("3. Click on your service")
    print("4. Go to 'Variables' tab")
    print("5. Find 'YOUTUBE_CLIENT_SECRET_B64' and update its value")
    print("6. Find 'YOUTUBE_TOKEN_JSON' and update its value")
    print("7. Click 'Deploy' or wait for auto-deploy")
    print()
    print("✓ Done! Your YouTube token is now ready for Railway.")
    print("="*60)
    
    # Save to file for easy copy
    output_file = Path('railway_credentials.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("RAILWAY ENVIRONMENT VARIABLES\n")
        f.write("="*60 + "\n\n")
        f.write("Variable Name: YOUTUBE_CLIENT_SECRET_B64\n")
        f.write("Value:\n")
        f.write(client_secret_b64 + "\n\n")
        f.write("-"*60 + "\n\n")
        f.write("Variable Name: YOUTUBE_TOKEN_JSON\n")
        f.write("Value:\n")
        f.write(token_b64 + "\n\n")
        f.write("="*60 + "\n")
    
    print()
    print(f"✓ Credentials also saved to: {output_file}")
    print("  You can copy from this file if needed.")
    print()

except Exception as e:
    print()
    print(f"❌ ERROR: {e}")
    print()
    print("If you see 'redirect_uri_mismatch' error:")
    print("1. Make sure you created 'Desktop app' credentials (not Web app)")
    print("2. Download the correct client_secret.json")
    print()
    sys.exit(1)
