"""
Test the credential rotation logic without running the full bot.
Shows which project would be used on different days.
"""

from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent

def get_available_projects():
    """Find all available projects."""
    available = []
    for i in range(1, 100):
        if (BASE_DIR / f"client_secret_{i}.json").exists():
            available.append(i)
        elif i > 10:
            break
    return available

def get_project_for_day(day, available_projects):
    """Calculate which project would be used on a given day."""
    if not available_projects:
        return 0
    project_index = (day - 1) % len(available_projects)
    return available_projects[project_index]

def main():
    print("="*70)
    print("YouTube API Credential Rotation Test")
    print("="*70)
    print()
    
    available = get_available_projects()
    
    if not available:
        print("⚠ No rotation configured - using default credentials")
        print()
        print("Create client_secret_1.json, client_secret_2.json, etc. to enable rotation")
        return
    
    print(f"Found {len(available)} projects: {', '.join(map(str, available))}")
    print()
    
    # Show current month rotation
    today = datetime.now()
    print(f"Rotation Schedule for {today.strftime('%B %Y')}")
    print("-"*70)
    
    # Get first and last day of current month
    first_day = today.replace(day=1)
    if today.month == 12:
        last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    current_day = first_day
    while current_day <= last_day:
        day_num = current_day.day
        project = get_project_for_day(day_num, available)
        
        day_name = current_day.strftime('%a')
        date_str = current_day.strftime('%b %d')
        
        marker = " ← TODAY" if current_day.date() == today.date() else ""
        print(f"  {day_name} {date_str} (Day {day_num:2}) → Project {project}{marker}")
        
        current_day += timedelta(days=1)
    
    print()
    print("="*70)
    print()
    
    # Show distribution
    print("Project Usage Distribution:")
    print("-"*70)
    
    days_in_month = (last_day - first_day).days + 1
    for proj in available:
        count = sum(1 for d in range(1, days_in_month + 1) 
                   if get_project_for_day(d, available) == proj)
        percentage = (count / days_in_month) * 100
        bar = "█" * int(percentage / 2)
        print(f"  Project {proj}: {count:2} days ({percentage:5.1f}%) {bar}")
    
    print()
    print("="*70)
    print()
    
    # Show today's selection
    today_project = get_project_for_day(today.day, available)
    print(f"✓ Today (Day {today.day}): Using Project {today_project}")
    print()
    
    # Check if authenticated
    token_file = BASE_DIR / f"token_{today_project}.json"
    if token_file.exists():
        print(f"✓ Project {today_project} is authenticated and ready")
    else:
        print(f"⚠ Project {today_project} needs authentication")
        print(f"  Run: python authenticate_all_projects.py")
    print()

if __name__ == "__main__":
    main()
