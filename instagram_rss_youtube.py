#!/usr/bin/env python3
"""
Instagram to YouTube via RSS Feed
Uses RSS feeds to get latest Instagram posts (no login required!)
Works on Railway!
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
import shutil
import re

# Configure output streams
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding='utf-8', line_buffering=True)
    except:
        pass

os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

BASE_DIR = Path(__file__).resolve().parent

# Import required libraries
try:
    import feedparser
    RSS_AVAILABLE = True
    print("✓ feedparser available")
except ImportError:
    RSS_AVAILABLE = False
    print("✗ feedparser not available - install with: pip install feedparser")

try:
    import requests
    REQUESTS_AVAILABLE = True
    print("✓ requests available")
except ImportError:
    REQUESTS_AVAILABLE = False
    print("✗ requests not available - install with: pip install requests")

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

# Instagram accounts to monitor
INSTAGRAM_ACCOUNTS = [
    'i.haiderr',
    'rajab.butt94'
]

# RSS Feed URLs (using RSSHub)
RSS_FEEDS = [
    'https://rsshub.app/instagram/user/i.haiderr',
    'https://rsshub.app/instagram/user/rajab.butt94'
]

DEFAULT_HASHTAGS = "#rajabfamily #rajabbutt #viralshorts #maandogar #shezi #haidershah #haiderlive #jahangir"
CHECK_INTERVAL = 600  # 10 minutes
MAX_POSTS_PER_CHECK = 3

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
                    'tags': ['shorts', 'viral', 'instagram'],
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

class InstagramRSSDownloader:
    def __init__(self):
        self.temp_dir = BASE_DIR / 'temp_instagram_rss'
        self.temp_dir.mkdir(exist_ok=True)
        
        self.tracking_file = BASE_DIR / 'instagram_rss_processed.json'
        self.processed = self._load_tracking()
        
        self.uploader = YouTubeUploader()
        
        self.audio_tracks = [BASE_DIR / 'Track 1.mpeg', BASE_DIR / 'Track 2.mpeg']
    
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
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
        except Exception as e:
            print(f"  ⚠ Could not delete {path.name}: {e}")
    
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
    
    def _extract_shortcode_from_url(self, url):
        """Extract Instagram shortcode from URL"""
        match = re.search(r'/p/([A-Za-z0-9_-]+)', url)
        if match:
            return match.group(1)
        match = re.search(r'/reel/([A-Za-z0-9_-]+)', url)
        if match:
            return match.group(1)
        return None
    
    def _download_from_url(self, url):
        """Download Instagram video using yt-dlp"""
        try:
            print(f"  → Downloading from URL...")
            
            shortcode = self._extract_shortcode_from_url(url)
            if not shortcode:
                print(f"  ✗ Could not extract shortcode from URL")
                return None
            
            output_template = str(self.temp_dir / f"{shortcode}.%(ext)s")
            
            cmd = [
                'yt-dlp',
                '--no-warnings',
                '--quiet',
                '--no-check-certificate',
                '-f', 'best',
                '-o', output_template,
                url
            ]
            
            result = run_cmd(cmd, timeout=120)
            
            # Find downloaded file
            video_files = list(self.temp_dir.glob(f"{shortcode}.*"))
            if video_files:
                return video_files[0]
            
            print(f"  ✗ Download failed")
            return None
        except Exception as e:
            print(f"  ✗ Download error: {e}")
            return None
    
    def _add_watermark(self, video_path):
        """Add watermark to video"""
        try:
            output_path = video_path.parent / f"{video_path.stem}_watermarked.mp4"
            
            cmd = [
                'ffmpeg', '-i', str(video_path),
                '-vf', "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='Lahori Twins':fontsize=28:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2:shadowcolor=black@0.5:shadowx=1:shadowy=1",
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                '-c:a', 'copy', '-y', str(output_path)
            ]
            
            result = run_cmd(cmd, timeout=300)
            
            if result.returncode == 0 and output_path.exists():
                print(f"  ✓ Watermark added")
                self._cleanup(video_path)
                return output_path
            else:
                print(f"  ⚠ Watermark failed, using original")
                return video_path
        except Exception as e:
            print(f"  ⚠ Watermark error: {e}")
            return video_path
    
    def _image_to_video(self, img_path):
        """Convert image to video with audio"""
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
                '-vf', "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='Lahori Twins':fontsize=28:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2",
                '-c:a', 'aac', '-b:a', '128k', '-shortest', '-y', str(out_path)
            ]
            
            result = run_cmd(cmd, timeout=120)
            
            if result.returncode == 0 and out_path.exists():
                print(f"  ✓ Converted to video with watermark")
                self._cleanup(img_path)
                return out_path
            
            return None
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def check_rss_feed(self, feed_url, username):
        """Check RSS feed for new posts"""
        if not RSS_AVAILABLE or not REQUESTS_AVAILABLE:
            print(f"  ✗ Required libraries not available")
            return
        
        try:
            print(f"\n→ Checking RSS feed for @{username}")
            
            # Fetch RSS feed
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                print(f"  ⚠ No entries in RSS feed")
                return
            
            print(f"  → Found {len(feed.entries)} entries in feed")
            
            downloaded_count = 0
            
            for entry in feed.entries[:MAX_POSTS_PER_CHECK]:
                # Get post URL
                post_url = entry.link if hasattr(entry, 'link') else None
                if not post_url:
                    continue
                
                # Extract shortcode
                shortcode = self._extract_shortcode_from_url(post_url)
                if not shortcode:
                    continue
                
                # Check if already processed
                if shortcode in self.processed:
                    continue
                
                print(f"\n  → Post: {shortcode}")
                print(f"    URL: {post_url}")
                
                # Get title and description
                title = entry.title if hasattr(entry, 'title') else f"{username} post"
                description = entry.description if hasattr(entry, 'description') else ""
                
                # Check copyright
                if self._check_copyright(title) or self._check_copyright(description):
                    print(f"  ✗ Skipped: Copyright detected")
                    self.processed.append(shortcode)
                    self._save_tracking()
                    continue
                
                # Download video
                video_path = self._download_from_url(post_url)
                
                if video_path and video_path.exists():
                    print(f"  ✓ Downloaded: {video_path.name}")
                    
                    # Add watermark if it's a video
                    if video_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
                        video_path = self._add_watermark(video_path)
                    elif video_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        # Convert image to video
                        video_path = self._image_to_video(video_path)
                    
                    if video_path and video_path.exists():
                        # Upload to YouTube
                        upload_title = title[:80] if title else f"{username} Instagram post"
                        upload_desc = description if description else DEFAULT_HASHTAGS
                        
                        if DEFAULT_HASHTAGS not in upload_desc:
                            upload_desc = f"{upload_desc}\n\n{DEFAULT_HASHTAGS}"
                        
                        success = self.uploader.upload(video_path, upload_title, upload_desc)
                        
                        if success:
                            downloaded_count += 1
                            self._cleanup(video_path)
                
                # Mark as processed
                self.processed.append(shortcode)
                self._save_tracking()
                
                # Keep only last 1000 entries
                if len(self.processed) > 1000:
                    self.processed = self.processed[-1000:]
                    self._save_tracking()
                
                # Delay between posts
                time.sleep(random.randint(5, 10))
            
            if downloaded_count > 0:
                print(f"\n  ✓ Downloaded and uploaded {downloaded_count} post(s)")
            else:
                print(f"\n  → No new posts found")
        
        except Exception as e:
            print(f"  ✗ Error checking RSS feed: {e}")
    
    def monitor(self):
        print(f"\n{'='*60}")
        print(f"Instagram to YouTube via RSS Feed")
        print(f"{'='*60}")
        print(f"Using: RSS Feeds (No login required!)")
        print(f"Check interval: {CHECK_INTERVAL//60} minutes")
        print(f"YouTube: @LahoriTwins")
        print(f"\nMonitoring:")
        for username in INSTAGRAM_ACCOUNTS:
            print(f"  - @{username}")
        print(f"\nFeatures:")
        print(f"  ✓ RSS feed monitoring: ENABLED")
        print(f"  ✓ Copyright detection: ENABLED")
        print(f"  ✓ Watermark: ENABLED")
        print(f"  ✓ Auto upload: ENABLED")
        print(f"{'='*60}\n")
        
        if not RSS_AVAILABLE:
            print("✗ ERROR: feedparser not installed!")
            print("→ Install with: pip install feedparser")
            return
        
        if not REQUESTS_AVAILABLE:
            print("✗ ERROR: requests not installed!")
            print("→ Install with: pip install requests")
            return
        
        while True:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking all RSS feeds...")
                
                for feed_url, username in zip(RSS_FEEDS, INSTAGRAM_ACCOUNTS):
                    self.check_rss_feed(feed_url, username)
                    time.sleep(10)  # Delay between feeds
                
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
    print("Instagram to YouTube via RSS - Starting...")
    print("="*60 + "\n")
    
    downloader = InstagramRSSDownloader()
    downloader.monitor()
