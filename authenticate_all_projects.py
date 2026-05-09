"""
Authenticate all YouTube API projects to generate token files.
Run this script once after creating multiple client_secret_X.json files.

This will open a browser for each project to authenticate with your YouTube channel.
"""

import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
BASE_DIR = Path(__file__).parent

def authenticate_project(project_number):
    """Authenticate a single project and generate its token file."""
    
    secret_file = BASE_DIR / f"client_secret_{project_number}.json"
    token_file = BASE_DIR / f"token_{project_number}.json"
    
    if not secret_file.exists():
        print(f"✗ client_secret_{project_number}.json not found - skipping")
        return False
    
    if token_file.exists():
        print(f"⚠ token_{project_number}.json already exists")
        response = input(f"  Re-authenticate project {project_number}? (y/n): ").lower()
        if response != 'y':
            print(f"  Skipped project {project_number}")
            return True
    
    print(f"\n{'='*60}")
    print(f"Authenticating Project {project_number}")
    print(f"{'='*60}")
    print(f"Using: {secret_file.name}")
    print(f"Will create: {token_file.name}")
    print()
    
    try:
        creds = None
        
        # Check if token exists and is valid
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired token...")
                creds.refresh(Request())
            else:
                print("Opening browser for authentication...")
                print("→ Login with your YouTube channel account")
                print("→ Grant permissions")
                print()
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(secret_file),
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials
            token_file.write_text(creds.to_json(), encoding='utf-8')
            print(f"✓ Successfully authenticated project {project_number}")
            print(f"✓ Saved: {token_file.name}")
            return True
        else:
            print(f"✓ Project {project_number} already authenticated and valid")
            return True
            
    except Exception as e:
        print(f"✗ Failed to authenticate project {project_number}: {e}")
        return False

def main():
    print("="*60)
    print("YouTube API Multi-Project Authentication")
    print("="*60)
    print()
    print("This script will authenticate all your YouTube API projects.")
    print("Make sure you have created:")
    print("  • client_secret_1.json")
    print("  • client_secret_2.json")
    print("  • client_secret_3.json")
    print("  • ... (and so on)")
    print()
    
    # Find all client_secret files
    secret_files = sorted(BASE_DIR.glob("client_secret_*.json"))
    
    if not secret_files:
        print("✗ No client_secret_X.json files found!")
        print()
        print("Please create them first:")
        print("1. Go to Google Cloud Console")
        print("2. Create multiple projects")
        print("3. Enable YouTube Data API v3 for each")
        print("4. Create OAuth credentials for each")
        print("5. Download and rename as client_secret_1.json, client_secret_2.json, etc.")
        sys.exit(1)
    
    print(f"Found {len(secret_files)} client_secret files:")
    for sf in secret_files:
        print(f"  • {sf.name}")
    print()
    
    input("Press Enter to start authentication process...")
    print()
    
    # Authenticate each project
    success_count = 0
    for secret_file in secret_files:
        # Extract project number from filename
        try:
            project_num = secret_file.stem.split('_')[-1]
            if authenticate_project(project_num):
                success_count += 1
        except Exception as e:
            print(f"✗ Error processing {secret_file.name}: {e}")
        print()
    
    # Summary
    print("="*60)
    print("Authentication Summary")
    print("="*60)
    print(f"Successfully authenticated: {success_count}/{len(secret_files)} projects")
    print()
    
    if success_count == len(secret_files):
        print("✓ All projects authenticated successfully!")
        print()
        print("You can now run your main script.")
        print("It will automatically rotate between projects daily.")
    else:
        print("⚠ Some projects failed to authenticate.")
        print("Please check the errors above and try again.")

if __name__ == "__main__":
    main()
