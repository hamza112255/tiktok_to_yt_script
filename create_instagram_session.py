#!/usr/bin/env python3
"""
Create Instagram session file for Railway
Run this LOCALLY to generate session file
"""
import instaloader
from pathlib import Path

print("\n" + "="*60)
print("Instagram Session Creator for Railway")
print("="*60 + "\n")

username = input("Enter your Instagram username: ").strip()
password = input("Enter your Instagram password: ").strip()

print(f"\n→ Logging into Instagram as @{username}...")

try:
    loader = instaloader.Instaloader()
    loader.login(username, password)
    
    print("✓ Login successful!")
    
    # Save session
    session_file = Path(f"session-{username}")
    
    if session_file.exists():
        print(f"✓ Session file created: {session_file}")
        
        # Read and encode session
        import base64
        with open(session_file, 'rb') as f:
            session_data = f.read()
        
        encoded = base64.b64encode(session_data).decode('utf-8')
        
        output_file = Path('instagram_session_b64.txt')
        output_file.write_text(encoded, encoding='utf-8')
        
        print(f"✓ Encoded session saved to: {output_file}")
        print("\n" + "="*60)
        print("Next steps:")
        print("="*60)
        print("1. Copy content from instagram_session_b64.txt")
        print("2. Go to Railway → Variables")
        print("3. Add new variable:")
        print(f"   Name: INSTAGRAM_SESSION_B64")
        print(f"   Value: <paste content from instagram_session_b64.txt>")
        print("4. Add variable:")
        print(f"   Name: INSTAGRAM_SESSION_USERNAME")
        print(f"   Value: {username}")
        print("5. Railway will redeploy automatically")
        print("="*60 + "\n")
    else:
        print("✗ Session file not created")
        print("This might be due to 2FA or Instagram security")
        
except Exception as e:
    print(f"✗ Login failed: {e}")
    print("\nPossible reasons:")
    print("1. Wrong username/password")
    print("2. 2FA enabled (disable temporarily)")
    print("3. Instagram security check required")
    print("4. Account locked/suspended")
    print("\nSolutions:")
    print("- Login to Instagram on browser first")
    print("- Disable 2FA temporarily")
    print("- Use a different account")
