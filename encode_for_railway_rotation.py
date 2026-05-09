"""
Encode multiple YouTube API credentials for Railway deployment with rotation.
This script encodes all your client_secret_X.json and token_X.json files.
"""

import base64
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent

def encode_file(file_path):
    """Encode a file to base64."""
    try:
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            return encoded
        return None
    except Exception as e:
        print(f"✗ Error encoding {file_path.name}: {e}")
        return None

def find_projects():
    """Find all available projects."""
    projects = []
    for i in range(1, 100):
        secret_file = BASE_DIR / f"client_secret_{i}.json"
        token_file = BASE_DIR / f"token_{i}.json"
        
        if secret_file.exists():
            projects.append({
                'num': i,
                'secret_file': secret_file,
                'token_file': token_file,
                'has_secret': True,
                'has_token': token_file.exists()
            })
        elif i > 10:
            break
    
    return projects

def main():
    print("="*70)
    print("YouTube API Rotation - Railway Encoding")
    print("="*70)
    print()
    
    # Find all projects
    projects = find_projects()
    
    if not projects:
        print("✗ No credential files found!")
        print()
        print("Make sure you have:")
        print("  • client_secret_1.json, client_secret_2.json, etc.")
        print("  • token_1.json, token_2.json, etc.")
        print()
        print("Run 'python authenticate_all_projects.py' first to generate tokens.")
        return
    
    print(f"Found {len(projects)} project(s):")
    for proj in projects:
        status = "✓" if proj['has_token'] else "✗ Missing token"
        print(f"  Project {proj['num']}: {status}")
    print()
    
    # Check for missing tokens
    missing_tokens = [p['num'] for p in projects if not p['has_token']]
    if missing_tokens:
        print("⚠ WARNING: Some projects are missing token files!")
        print(f"  Projects without tokens: {', '.join(map(str, missing_tokens))}")
        print()
        print("Run 'python authenticate_all_projects.py' to generate missing tokens.")
        print()
        response = input("Continue anyway? (y/n): ").lower()
        if response != 'y':
            print("Aborted.")
            return
        print()
    
    # Encode all projects
    print("="*70)
    print("Encoding Credentials")
    print("="*70)
    print()
    
    encoded_data = []
    
    for proj in projects:
        print(f"Project {proj['num']}:")
        
        # Encode client_secret
        secret_encoded = encode_file(proj['secret_file'])
        if secret_encoded:
            print(f"  ✓ Encoded {proj['secret_file'].name}")
            encoded_data.append({
                'var_name': f"YOUTUBE_CLIENT_SECRET_{proj['num']}_B64",
                'value': secret_encoded,
                'description': f"Project {proj['num']} client secret"
            })
        else:
            print(f"  ✗ Failed to encode {proj['secret_file'].name}")
        
        # Encode token
        if proj['has_token']:
            token_encoded = encode_file(proj['token_file'])
            if token_encoded:
                print(f"  ✓ Encoded {proj['token_file'].name}")
                encoded_data.append({
                    'var_name': f"YOUTUBE_TOKEN_{proj['num']}_JSON",
                    'value': token_encoded,
                    'description': f"Project {proj['num']} token"
                })
            else:
                print(f"  ✗ Failed to encode {proj['token_file'].name}")
        
        print()
    
    if not encoded_data:
        print("✗ No credentials were encoded!")
        return
    
    # Save to file
    output_file = BASE_DIR / "railway_rotation_credentials.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("Railway Environment Variables - YouTube Quota Rotation\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total Projects: {len(projects)}\n")
        f.write(f"Rotation: Day-based (Day 1,4,7... → Project 1, etc.)\n\n")
        f.write("="*70 + "\n")
        f.write("COPY THESE TO RAILWAY ENVIRONMENT VARIABLES\n")
        f.write("="*70 + "\n\n")
        
        for item in encoded_data:
            f.write(f"Variable Name:\n{item['var_name']}\n\n")
            f.write(f"Value:\n{item['value']}\n\n")
            f.write("-"*70 + "\n\n")
        
        f.write("="*70 + "\n")
        f.write("SETUP INSTRUCTIONS\n")
        f.write("="*70 + "\n\n")
        f.write("1. Go to your Railway project dashboard\n")
        f.write("2. Click on your service\n")
        f.write("3. Go to 'Variables' tab\n")
        f.write("4. For each variable above:\n")
        f.write("   - Click 'New Variable'\n")
        f.write("   - Copy the Variable Name\n")
        f.write("   - Copy the Value (entire base64 string)\n")
        f.write("   - Click 'Add'\n")
        f.write("5. Deploy your service\n\n")
        f.write("The rotation will happen automatically based on the day!\n\n")
    
    print("="*70)
    print("✓ Encoding Complete!")
    print("="*70)
    print()
    print(f"Credentials saved to: {output_file.name}")
    print()
    print("Next Steps:")
    print("1. Open railway_rotation_credentials.txt")
    print("2. Copy each environment variable to Railway")
    print("3. Push your code to GitHub")
    print("4. Railway will automatically deploy with rotation")
    print()
    print("="*70)
    print()
    
    # Display summary
    print("Environment Variables to Add:")
    print("-"*70)
    for item in encoded_data:
        print(f"  • {item['var_name']}")
    print()
    print(f"Total: {len(encoded_data)} variables")
    print()
    
    # Show rotation schedule
    print("="*70)
    print("Rotation Schedule Preview")
    print("="*70)
    print()
    from datetime import datetime
    day = datetime.now().day
    for offset in range(7):
        future_day = (day + offset - 1) % 31 + 1
        project_index = (future_day - 1) % len(projects)
        project_num = projects[project_index]['num']
        marker = "← TODAY" if offset == 0 else ""
        print(f"  Day {future_day:2} → Project {project_num} {marker}")
    print()

if __name__ == "__main__":
    main()
