"""
Simple test to check if we can fetch TikTok videos
"""
import subprocess
import sys

# Fix encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

username = "rajabsfamily89"
url = f"https://www.tiktok.com/@{username}"

print(f"Testing video fetch from @{username}...")
print(f"URL: {url}\n")

cmd = [
    'yt-dlp',
    '--flat-playlist',
    '--print', 'id',
    '--print', 'title',
    '--playlist-end', '1',
    '--no-warnings',
    '--quiet',
    url
]

try:
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        encoding='utf-8',
        errors='replace',
        timeout=60
    )
    
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        
        # Debug output
        print(f"stdout length: {len(result.stdout)}")
        print(f"stderr length: {len(result.stderr)}")
        if result.stderr:
            print(f"stderr: {result.stderr[:200]}")
        
        print(f"Success! Found {len(lines)//2} video(s)\n")
        
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                video_id = lines[i].strip()
                title = lines[i + 1].strip()
                print(f"Video ID: {video_id}")
                print(f"Title: {title}\n")
    else:
        print(f"Error: {result.stderr}")
        
except Exception as e:
    print(f"Exception: {e}")
