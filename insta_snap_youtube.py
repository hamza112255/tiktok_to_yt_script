#!/usr/bin/env python3
"""
Instagram & Snapchat to YouTube Downloader
Optimized for minimal storage usage
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

# Import video processor
try:
    from video_processor import VideoProcessor
    VIDEO_PROCESSOR_AVAILABLE = True
except ImportError:
    VIDEO_PROCESSOR_AVAILABLE = False
    print("⚠ Video processor not available")

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

# Configuration
ACCOUNTS = {
    'instagram': [
        {'user': 'i.haiderr', 'url': 'https://www.instagram.com/i.haiderr/'},
        {'user': 'rajab.butt94', 'url': 'https://www.instagram.com/rajab.butt94/'}
    ],
    'snapchat': [
        {'user': 'i-haiderr', 'url': 'https://www.snapchat.com/add/i-haiderr'},
        {'user': 'rajab.butt7', 'url': 'https://www.snapchat.com/add/rajab.butt7'}
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
        
        if VIDEO_PROCESSOR_AVAILABLE:
            config = self._load_config()
            self.processor = VideoProcessor(config)
        else:
            self.processor = None
        
        self.audio_tracks = [BASE_DIR / 'Track 1.mpeg', BASE_DIR / 'Track 2.mpeg']
    
    def _load_config(self):
        config_file = BASE_DIR / 'config.json'
        if not config_file.exists():
            config_file = BASE_DIR / 'config.defaults.json'
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                'youtube_settings': {
                    'add_watermark': True,
                    'watermark_text': 'Lahori Twins',
                    'skip_female_videos': True,
                    'split_long_videos': False,  # Disabled to save storage
                    'split_duration_seconds': 38
                }
            }
    
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
        except:
            pass
    
    def _get_hash(self, url):
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def _check_copyright(self, text):
        """Check if content has copyright indicators - IMPORTANT for avoiding strikes"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Comprehensive copyright keywords
        copyright_keywords = [
            'copyright', '©', '(c)', 'all rights reserved', 'copyrighted',
            'rights reserved', 'protected content', 'intellectual property',
            'dmca', 'trademark', '™', '®', 'licensed content',
            'unauthorized use', 'permission required', 'proprietary'
        ]
        
        for keyword in copyright_keywords:
            if keyword in text_lower:
                print(f"⚠ Copyright keyword found: '{keyword}'")
                return True
        
        return False
    
    def _image_to_video(self, img_path):
        try:
            print(f"→ Converting image to video")
            
            audio = random.choice([t for t in self.audio_tracks if t.exists()])
            if not audio:
                print("⚠ No audio tracks")
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
            
            # Create video
            cmd = [
                'ffmpeg', '-loop', '1', '-i', str(img_path), '-i', str(audio),
                '-c:v', 'libx264', '-t', str(duration), '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
                '-c:a', 'aac', '-b:a', '128k', '-shortest', '-y', str(out_path)
            ]
            
            result = run_cmd(cmd, timeout=120)
            
            if result.returncode == 0 and out_path.exists():
                print(f"✓ Converted to video")
                self._cleanup(img_path)
                return out_path
            
            return None
        except:
            return None
    
    def download_and_process(self, url, username, platform):
        try:
            url_hash = self._get_hash(url)
            
            if url_hash in self.processed:
                return
            
            print(f"\n→ Checking {platform} @{username}")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_file = self.temp_dir / f"{timestamp}_{username}.%(ext)s"
            
            # Download with yt-dlp
            cmd = [
                'yt-dlp', '-o', str(temp_file),
                '--playlist-end', '1',
                '--max-filesize', '100M',
                '--quiet', '--no-warnings',
                '--write-info-json',
                url
            ]
            
            result = run_cmd(cmd, timeout=180)
            
            if result.returncode != 0:
                return
            
            # Find downloaded files
            files = list(self.temp_dir.glob(f"{timestamp}_{username}.*"))
            video_files = [f for f in files if f.suffix.lower() in {'.mp4', '.mov', '.webm', '.mkv', '.jpg', '.jpeg', '.png'}]
            
            if not video_files:
                return
            
            for file_path in video_files:
                if file_path.suffix == '.json':
                    continue
                
                print(f"✓ Downloaded: {file_path.name}")
                
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
                    print(f"✗ Skipped: Copyright detected")
                    self._cleanup(file_path)
                    continue
                
                # Convert image to video
                if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
                    file_path = self._image_to_video(file_path)
                    if not file_path:
                        continue
                
                # Process video (female detection + watermark)
                if self.processor:
                    should_skip, processed = self.processor.process_video(file_path)
                    
                    if should_skip:
                        print(f"✗ Skipped: Female detected in video")
                        self._cleanup(file_path)
                        continue
                    
                    videos_to_upload = processed
                else:
                    # No video processor - skip female detection
                    print(f"⚠ Video processor unavailable - female detection disabled")
                    videos_to_upload = [file_path]
                
                # Upload each video
                for video in videos_to_upload:
                    title = caption[:80] if caption else f"{username} {platform}"
                    desc = caption if caption else DEFAULT_HASHTAGS
                    
                    if DEFAULT_HASHTAGS not in desc:
                        desc = f"{desc}\n\n{DEFAULT_HASHTAGS}"
                    
                    self.uploader.upload(video, title, desc)
                    self._cleanup(video)
                
                # Mark as processed
                self.processed.append(url_hash)
                self._save_tracking()
                
                # Keep only last 1000 entries
                if len(self.processed) > 1000:
                    self.processed = self.processed[-1000:]
                    self._save_tracking()
        
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def monitor(self):
        print(f"\n{'='*60}")
        print(f"Instagram & Snapchat to YouTube")
        print(f"{'='*60}")
        print(f"Check interval: {CHECK_INTERVAL//60} minutes")
        print(f"YouTube: @LahoriTwins")
        print(f"\nFeatures:")
        print(f"  ✓ Copyright detection: ENABLED")
        print(f"  {'✓' if self.processor else '✗'} Female detection: {'ENABLED' if self.processor else 'DISABLED (no video processor)'}")
        print(f"  ✓ Watermark: ENABLED")
        print(f"  ✗ Video splitting: DISABLED (saves storage)")
        print(f"{'='*60}\n")
        
        while True:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking...")
                
                # Instagram
                for acc in ACCOUNTS['instagram']:
                    self.download_and_process(acc['url'], acc['user'], 'instagram')
                
                # Snapchat
                for acc in ACCOUNTS['snapchat']:
                    self.download_and_process(acc['url'], acc['user'], 'snapchat')
                
                print(f"\n→ Next check in {CHECK_INTERVAL//60} minutes\n")
                time.sleep(CHECK_INTERVAL)
            
            except KeyboardInterrupt:
                print("\n\n⚠ Stopped by user")
                break
            except Exception as e:
                print(f"✗ Error: {e}")
                time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Instagram & Snapchat to YouTube - Starting...")
    print("="*60 + "\n")
    
    downloader = ContentDownloader()
    downloader.monitor()
