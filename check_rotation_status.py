"""
Quick status checker for YouTube API credential rotation.
Shows which project will be used today and lists all available projects.
"""

from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent

def check_status():
    print("="*60)
    print("YouTube API Credential Rotation Status")
    print("="*60)
    print()
    
    # Find all available projects
    available_projects = []
    for i in range(1, 100):
        secret_file = BASE_DIR / f"client_secret_{i}.json"
        token_file = BASE_DIR / f"token_{i}.json"
        
        if secret_file.exists():
            has_token = "✓" if token_file.exists() else "✗"
            available_projects.append({
                'num': i,
                'secret': True,
                'token': token_file.exists()
            })
        elif i > 10:
            break
    
    if not available_projects:
        print("⚠ No credential rotation configured")
        print()
        print("You're using the default credentials:")
        print("  • client_secret.json")
        print("  • token.json")
        print()
        print("To set up rotation, see: YOUTUBE_QUOTA_ROTATION_GUIDE.md")
        return
    
    # Show available projects
    print(f"Available Projects: {len(available_projects)}")
    print()
    for proj in available_projects:
        status = "✓ Ready" if proj['token'] else "✗ Not authenticated"
        print(f"  Project {proj['num']}: {status}")
        print(f"    • client_secret_{proj['num']}.json")
        if proj['token']:
            print(f"    • token_{proj['num']}.json")
        else:
            print(f"    • token_{proj['num']}.json (missing - run authenticate_all_projects.py)")
    print()
    
    # Calculate which project is used today
    day_of_month = datetime.now().day
    project_index = (day_of_month - 1) % len(available_projects)
    active_project = available_projects[project_index]['num']
    
    print("="*60)
    print(f"Today: {datetime.now().strftime('%B %d, %Y')} (Day {day_of_month})")
    print(f"Active Project: Project {active_project}")
    print("="*60)
    print()
    
    if not available_projects[project_index]['token']:
        print("⚠ WARNING: Active project is not authenticated!")
        print(f"  Run: python authenticate_all_projects.py")
        print()
    else:
        print("✓ Active project is ready to use")
        print()
    
    # Show rotation schedule for next 7 days
    print("Rotation Schedule (Next 7 Days):")
    print("-" * 60)
    for offset in range(7):
        future_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        future_date = future_date.replace(day=day_of_month + offset)
        future_day = future_date.day
        future_index = (future_day - 1) % len(available_projects)
        future_project = available_projects[future_index]['num']
        
        day_name = future_date.strftime('%A')
        date_str = future_date.strftime('%b %d')
        
        marker = "← TODAY" if offset == 0 else ""
        print(f"  {day_name:9} {date_str} (Day {future_day:2}) → Project {future_project} {marker}")
    
    print()
    print("="*60)
    print()
    
    # Check for missing authentications
    missing = [p['num'] for p in available_projects if not p['token']]
    if missing:
        print("⚠ Action Required:")
        print(f"  {len(missing)} project(s) need authentication: {', '.join(map(str, missing))}")
        print(f"  Run: python authenticate_all_projects.py")
    else:
        print("✓ All projects are authenticated and ready!")
    print()

if __name__ == "__main__":
    check_status()
