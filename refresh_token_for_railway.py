#!/usr/bin/env python3
"""
Refresh YouTube token and encode for Railway
Run this locally when your token expires
"""
import base64
from pathlib import Path

print("\n" + "="*60)
print("YouTube Token Refresh for Railway")
print("="*60 + "\n")

print("Step 1: Refreshing YouTube token...")
print("This will open a browser for authentication.\n")

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    token_file = Path('token.json')
    client_secret_file = Path('client_secret.json')
    
    if not client_secret_file.exists():
        print("✗ client_secret.json not found!")
        print("Make sure client_secret.json is in this folder.")
        exit(1)
    
    creds = None
    
    # Try to load existing token
    if token_file.exists():
        print("→ Loading existing token...")
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    
    # Refresh or get new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("→ Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✓ Token refreshed successfully!")
            except Exception as e:
                print(f"⚠ Refresh failed: {e}")
                print("→ Getting new token...")
                creds = None
        
        if not creds:
            print("→ Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secret_file), 
                SCOPES
            )
            creds = flow.run_local_server(port=0)
            print("✓ Authentication successful!")
    
    # Save token
    token_file.write_text(creds.to_json(), encoding='utf-8')
    print("✓ token.json saved\n")
    
    # Encode for Railway
    print("Step 2: Encoding for Railway...")
    content = token_file.read_text(encoding='utf-8')
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    output_file = Path('token_b64.txt')
    output_file.write_text(encoded, encoding='utf-8')
    
    print(f"✓ Encoded to {output_file}\n")
    
    print("="*60)
    print("✓ Success!")
    print("="*60 + "\n")
    
    print("Next steps:")
    print("1. Go to Railway dashboard")
    print("2. Click your service → Variables")
    print("3. Update YOUTUBE_TOKEN_JSON variable")
    print("4. Paste content from token_b64.txt")
    print("5. Railway will automatically redeploy\n")
    
    print("="*60 + "\n")

except ImportError:
    print("✗ YouTube API libraries not installed!")
    print("Run: pip install google-api-python-client google-auth-oauthlib")
    exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)
