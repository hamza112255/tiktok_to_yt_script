#!/usr/bin/env python3
"""
Instagram & Snapchat to YouTube Downloader V2
Uses gallery-dl as fallback for better Instagram/Snapchat support
"""
import os
import sys
import time
import json
import hashlib
from datetime import datetime
import subprocess
from pathlib import Path
import random

# Configure output streams
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding='utf-8', line_buffering=True)
    except:
        pass

os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

BASE_DIR = Path(__file__).resolve().parent

# YouTube API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("⚠ YouTube API not available")

# Configuration - Using direct post URLs instead of profile URLs
ACCOUNTS = {
    'instagram': [
        {
            'user': 'i.haiderr',
            'profile': 'https://www.instagram.com/i.haiderr/',
            'type': 'profile'
        },
        {
            'user': 'rajab.butt94',
            'profile': 'https://www.instagram.com/rajab.butt94/',
            'type': 'profile'
        }
    ],
    'snapchat': [
        {
            'user': 'i-haiderr',
            'profile': 'https://www.snapchat.com/add/i-haiderr',
            'type': 'profile'
        },
        {
            'user': 'rajab.butt7',
            'profile': 'https://www.snapchat.com/add/rajab.butt7',
            'type': 'profile'
        }
    ]
}

DEFAULT_HASHTAGS = "#rajabfamily #rajabbutt #viralshorts #maandogar #shezi #haidershah #haiderlive #jahangir"
CHECK_INTERVAL = 600  # 10 minutes

def run_cmd(cmd, timeout=None):
    """Run command with UTF-8 encoding"""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, 
                            encoding='utf-8', errors='replace', timeout=timeout)
    except:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

class YouTubeUploader:
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self):
        self.youtube = None
        self.enabled = False
        if YOUTUBE_API_AVAILABLE:
            self._auth()
    
    def _auth(self):
        try:
            token_file = BASE_DIR / 'token.json'
            secret_file = BASE_DIR / 'client_secret.json'
            
            if not secret_file.exists():
                print("⚠ client_secret.json not found")
                return
            
            creds = None
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(str(token_file), self.SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(str(secret_file), self.SCOPES)
                    creds = flow.run_local_server(port=0)
                token_file.write_text(creds.to_json(), encoding='utf-8')
            
            self.youtube = build('youtube', 'v3', credentials=creds)
            self.enabled = True
            print("✓ YouTube authenticated")
        except Exception as e:
            print(f"✗ YouTube auth failed: {e}")
    
    def upload(self, video_path, title, description):
        if not self.enabled:
            print("⚠ YouTube upload disabled (not authenticated)")
            return False
        
        try:
            print(f"→ Uploading: {video_path.name}")
            
            if '#Shorts' not in title and '#shorts' not in title:
                title = f"{title} #Shorts"
            
            body = {
                'snippet': {
                    'title': title[:100],
                    'description': description[:5000],
                    'tags': ['shorts', 'viral'],
                    'categoryId': '24'
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
            request = self.youtube.videos().insert(part='snippet,status', body=body, media_body=media)
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"  → {int(status.progress() * 100)}%")
            
            print(f"✓ Uploaded! ID: {response['id']}")
            print(f"  → URL: https://www.youtube.com/watch?v={response['id']}")
            return True
        except Exception as e:
            print(f"✗ Upload failed: {e}")
            return False

class ContentDownloader:
    def __init__(self):
        self.temp_dir = BASE_DIR / 'temp_downloads'
        self.temp_dir.mkdir(exist_ok=True)
        
        self.tracking_file = BASE_DIR / 'processed.json'
        self.processed = self._load_tracking()
        
        self.uploader = YouTubeUploader()
        
        self.audio_tracks = [BASE_DIR / 'Track 1.mpeg', BASE_DIR / 'Track 2.mpeg']
        
        # Check which downloaders are available
        self.check_downloaders()
    
    def check_downloaders(self):
        """Check which download tools are available"""
        print("\n→ Checking available downloaders...")
        
        # Check yt-dlp
        result = run_cmd(['yt-dlp', '--version'], timeout=5)
        if result.returncode == 0:
            print(f"  ✓ yt-dlp: {result.stdout.strip()}")
            self.has_ytdlp = True
        else:
            print(f"  ✗ yt-dlp: not available")
            self.has_ytdlp = False
        
        # Check gallery-dl
        result = run_cmd(['gallery-dl', '--version'], timeout=5)
        if result.returncode == 0:
            print(f"  ✓ gallery-dl: {result.stdout.strip()}")
            self.has_gallerydl = True
        else:
            print(f"  ✗ gallery-dl: not available")
            self.has_gallerydl = False
        
        if not self.has_ytdlp and not self.has_gallerydl:
            print("  ⚠ WARNING: No downloaders available!")
            print("  → Install: pip install yt-dlp gallery-dl")
    
    def _load_tracking(self):
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_tracking(self):
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed, f, indent=2)
    
    def _cleanup(self, path):
        try:
            if path and path.exists():
                path.unlink()
                print(f"  → Deleted: {path.name}")
        except Exception as e:
            print(f"  ⚠ Could not delete {path.name}: {e}")
    
    def _get_hash(self, url):
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def _check_copyright(self, text):
        """Check if content has copyright indicators"""
        if not text:
            return False
        
        text_lower = text.lower()
        copyright_keywords = [
            'copyright', '©', '(c)', 'all rights reserved', 'copyrighted',
            'rights reserved', 'protected content', 'intellectual property',
            'dmca', 'trademark', '™', '®', 'licensed content'
        ]
        
        for keyword in copyright_keywords:
            if keyword in text_lower:
                print(f"  ⚠ Copyright keyword found: '{keyword}'")
                return True
        
        return False
    
    def _image_to_video(self, img_path):
        try:
            print(f"  → Converting image to video")
            
            audio = random.choice([t for t in self.audio_tracks if t.exists()])
            if not audio:
                print("  ⚠ No audio tracks found")
                return None
            
            out_path = img_path.parent / f"{img_path.stem}.mp4"
            
            # Get audio duration
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(audio)]
            result = run_cmd(cmd, timeout=30)
            
            duration = 10
            if result.returncode == 0:
                try:
                    duration = min(float(json.loads(result.stdout)['format']['duration']), 60)
                except:
                    pass
            
            # Create video with watermark
            cmd = [
                'ffmpeg', '-loop', '1', '-i', str(img_path), '-i', str(audio),
                '-c:v', 'libx264', '-t', str(duration), '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,drawtext=fontfile=C\\\\:/Windows/Fonts/arial.ttf:text=\'Lahori Twins\':fontsize=28:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2',
                '-c:a', 'aac', '-b:a', '128k', '-shortest', '-y', str(out_path)
            ]
            
            result = run_cmd(cmd, timeout=120)
            
            if result.returncode == 0 and out_path.exists():
                print(f"  ✓ Converted to video with watermark")
                self._cleanup(img_path)
                return out_path
            
            print(f"  ⚠ Conversion failed")
            return None
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def download_with_ytdlp(self, url, username, platform):
        """Try downloading with yt-dlp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_file = self.temp_dir / f"{timestamp}_{username}.%(ext)s"
        
        cmd = [
            'yt-dlp', '-o', str(temp_file),
            '--playlist-end', '1',
            '--max-filesize', '100M',
            '--no-warnings',
            '--write-info-json',
            '--cookies-from-browser', 'chrome',  # Try using browser cookies
            url
        ]
        
        print(f"  → Trying yt-dlp...")
        result = run_cmd(cmd, timeout=180)
        
        if result.returncode == 0:
            files = list(self.temp_dir.glob(f"{timestamp}_{username}.*"))
            video_files = [f for f in files if f.suffix.lower() in {'.mp4', '.mov', '.webm', '.mkv', '.jpg', '.jpeg', '.png'}]
            return video_files
        
        print(f"  ✗ yt-dlp failed: {result.stderr[:200] if result.stderr else 'Unknown error'}")
        return []
    
    def download_and_process(self, account, platform):
        try:
            url = account['profile']
            username = account['user']
            url_hash = self._get_hash(url)
            
            if url_hash in self.processed:
                return
            
            print(f"\n→ Checking {platform} @{username}")
            
            # Try downloading
            video_files = []
            
            if self.has_ytdlp:
                video_files = self.download_with_ytdlp(url, username, platform)
            
            if not video_files:
                print(f"  ✗ No content found or download failed")
                print(f"  → This is normal - {platform} may block automated downloads")
                print(f"  → The script will keep trying every 10 minutes")
                return
            
            for file_path in video_files:
                if file_path.suffix == '.json':
                    continue
                
                print(f"  ✓ Downloaded: {file_path.name}")
                
                # Read metadata
                info_file = file_path.parent / f"{file_path.stem}.info.json"
                caption = None
                
                if info_file.exists():
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            info = json.load(f)
                            caption = info.get('description') or info.get('title')
                    except:
                        pass
                    self._cleanup(info_file)
                
                # Check copyright
                if self._check_copyright(caption):
                    print(f"  ✗ Skipped: Copyright detected")
                    self._cleanup(file_path)
                    continue
                
                # Convert image to video
                if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
                    file_path = self._image_to_video(file_path)
                    if not file_path:
                        continue
                
                # Upload
                title = caption[:80] if caption else f"{username} {platform}"
                desc = caption if caption else DEFAULT_HASHTAGS
                
                if DEFAULT_HASHTAGS not in desc:
                    desc = f"{desc}\n\n{DEFAULT_HASHTAGS}"
                
                success = self.uploader.upload(file_path, title, desc)
                
                if success:
                    self._cleanup(file_path)
                    
                    # Mark as processed
                    self.processed.append(url_hash)
                    self._save_tracking()
                    
                    # Keep only last 1000 entries
                    if len(self.processed) > 1000:
                        self.processed = self.processed[-1000:]
                        self._save_tracking()
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    def monitor(self):
        print(f"\n{'='*60}")
        print(f"Instagram & Snapchat to YouTube V2")
        print(f"{'='*60}")
        print(f"Check interval: {CHECK_INTERVAL//60} minutes")
        print(f"YouTube: @LahoriTwins")
        print(f"\nFeatures:")
        print(f"  ✓ Copyright detection: ENABLED")
        print(f"  ✓ Watermark: ENABLED")
        print(f"  ✗ Video splitting: DISABLED (saves storage)")
        print(f"  ✗ Female detection: DISABLED (Railway memory limits)")
        print(f"{'='*60}\n")
        
        while True:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking all accounts...")
                
                # Instagram
                for acc in ACCOUNTS['instagram']:
                    self.download_and_process(acc, 'instagram')
                
                # Snapchat
                for acc in ACCOUNTS['snapchat']:
                    self.download_and_process(acc, 'snapchat')
                
                print(f"\n→ Next check in {CHECK_INTERVAL//60} minutes\n")
                time.sleep(CHECK_INTERVAL)
            
            except KeyboardInterrupt:
                print("\n\n⚠ Stopped by user")
                break
            except Exception as e:
                print(f"✗ Error in main loop: {e}")
                time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Instagram & Snapchat to YouTube V2 - Starting...")
    print("="*60 + "\n")
    
    downloader = ContentDownloader()
    downloader.monitor()
