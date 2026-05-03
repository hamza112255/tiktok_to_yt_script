#!/usr/bin/env python3
"""
Instagram to YouTube Downloader
Uses Instaloader for reliable Instagram downloads
100% Working Solution
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

# Configure output streams
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding='utf-8', line_buffering=True)
    except:
        pass

os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

BASE_DIR = Path(__file__).resolve().parent

# Import Instaloader
try:
    import instaloader
    INSTALOADER_AVAILABLE = True
    print("✓ Instaloader available")
except ImportError:
    INSTALOADER_AVAILABLE = False
    print("✗ Instaloader not available - install with: pip install instaloader")

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

DEFAULT_HASHTAGS = "#rajabfamily #rajabbutt #viralshorts #maandogar #shezi #haidershah #haiderlive #jahangir"
CHECK_INTERVAL = 600  # 10 minutes
MAX_POSTS_PER_CHECK = 3  # Download max 3 latest posts per account

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

class InstagramDownloader:
    def __init__(self):
        self.temp_dir = BASE_DIR / 'temp_instagram'
        self.temp_dir.mkdir(exist_ok=True)
        
        self.tracking_file = BASE_DIR / 'instagram_processed.json'
        self.processed = self._load_tracking()
        
        self.uploader = YouTubeUploader()
        
        self.audio_tracks = [BASE_DIR / 'Track 1.mpeg', BASE_DIR / 'Track 2.mpeg']
        
        # Initialize Instaloader with session
        if INSTALOADER_AVAILABLE:
            self.loader = instaloader.Instaloader(
                download_videos=True,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=True,
                compress_json=False,
                post_metadata_txt_pattern='',
                dirname_pattern=str(self.temp_dir)
            )
            
            # Try to load session from file first (if exists from previous run)
            instagram_username = os.getenv('INSTAGRAM_USERNAME', 'rebel_jallal')
            session_file = BASE_DIR / f"session-{instagram_username}"
            
            session_loaded = False
            
            # Try loading existing session file
            if session_file.exists():
                try:
                    print(f"→ Loading existing session for @{instagram_username}...")
                    self.loader.load_session_from_file(instagram_username, str(session_file))
                    print("✓ Session loaded from file")
                    session_loaded = True
                except Exception as e:
                    print(f"⚠ Session file load failed: {e}")
            
            # Try loading session from environment variable
            if not session_loaded:
                session_b64 = os.getenv('INSTAGRAM_SESSION_B64')
                session_username = os.getenv('INSTAGRAM_SESSION_USERNAME', instagram_username)
                
                if session_b64:
                    try:
                        import base64
                        print(f"→ Loading Instagram session from environment...")
                        
                        # Decode and save session file
                        session_data = base64.b64decode(session_b64)
                        session_file = BASE_DIR / f"session-{session_username}"
                        session_file.write_bytes(session_data)
                        
                        # Load session
                        self.loader.load_session_from_file(session_username, str(session_file))
                        print("✓ Instagram session loaded successfully")
                        session_loaded = True
                    except Exception as e:
                        print(f"⚠ Session load failed: {e}")
            
            # If no session loaded, try direct login
            if not session_loaded:
                self._try_direct_login()
            
            print("✓ Instaloader initialized")
        else:
            self.loader = None
            print("✗ Instaloader not available")
    
    def _try_direct_login(self):
        """Try direct login with username/password"""
        instagram_username = os.getenv('INSTAGRAM_USERNAME', 'rebel_jallal')
        instagram_password = os.getenv('INSTAGRAM_PASSWORD', 'RebelJallal123')
        
        if instagram_username and instagram_password:
            try:
                print(f"→ Logging into Instagram as @{instagram_username}...")
                self.loader.login(instagram_username, instagram_password)
                print("✓ Instagram login successful")
                
                # Save session for reuse
                session_file = BASE_DIR / f"session-{instagram_username}"
                self.loader.save_session_to_file(str(session_file))
                print(f"✓ Session saved to {session_file.name}")
            except Exception as e:
                print(f"⚠ Instagram login failed: {e}")
                print("→ Will try without authentication (may be blocked)")
        else:
            print("→ Will try without authentication (may be blocked)")
    
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
    
    def _add_watermark(self, video_path):
        """Add watermark to video"""
        try:
            output_path = video_path.parent / f"{video_path.stem}_watermarked.mp4"
            
            cmd = [
                'ffmpeg', '-i', str(video_path),
                '-vf', "drawtext=fontfile=C\\\\:/Windows/Fonts/arial.ttf:text='Lahori Twins':fontsize=28:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2:shadowcolor=black@0.5:shadowx=1:shadowy=1",
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
                '-vf', "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,drawtext=fontfile=C\\\\:/Windows/Fonts/arial.ttf:text='Lahori Twins':fontsize=28:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2",
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
    
    def download_from_account(self, username):
        """Download latest posts from Instagram account using Instaloader"""
        if not self.loader:
            print(f"  ✗ Instaloader not available")
            return
        
        try:
            print(f"\n→ Checking Instagram @{username}")
            
            # Get profile with retry logic
            max_retries = 3
            profile = None
            
            for attempt in range(max_retries):
                try:
                    profile = instaloader.Profile.from_username(self.loader.context, username)
                    break
                except instaloader.exceptions.ConnectionException as e:
                    if '403' in str(e) or 'Forbidden' in str(e):
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 30
                            print(f"  ⚠ 403 error, waiting {wait_time}s before retry...")
                            time.sleep(wait_time)
                        else:
                            print(f"  ✗ Profile blocked after {max_retries} attempts")
                            return
                    else:
                        raise
            
            if not profile:
                print(f"  ✗ Could not load profile")
                return
            
            print(f"  → Profile found: {profile.full_name}")
            print(f"  → Posts: {profile.mediacount}")
            
            # Download latest posts
            downloaded_count = 0
            
            for post in profile.get_posts():
                if downloaded_count >= MAX_POSTS_PER_CHECK:
                    break
                
                # Check if already processed
                post_id = post.shortcode
                if post_id in self.processed:
                    continue
                
                print(f"\n  → Post: {post_id}")
                print(f"    Type: {'Video' if post.is_video else 'Image'}")
                print(f"    Likes: {post.likes}")
                
                # Get caption
                caption = post.caption if post.caption else ""
                
                # Check copyright
                if self._check_copyright(caption):
                    print(f"  ✗ Skipped: Copyright detected")
                    self.processed.append(post_id)
                    self._save_tracking()
                    continue
                
                # Download post with retry
                try:
                    print(f"  → Downloading...")
                    
                    # Add delay before download to avoid rate limiting
                    time.sleep(random.randint(3, 8))
                    
                    self.loader.download_post(post, target=str(self.temp_dir / username))
                    
                    # Find downloaded files
                    post_dir = self.temp_dir / username
                    if not post_dir.exists():
                        print(f"  ✗ Download failed")
                        continue
                    
                    # Find video or image files
                    video_files = list(post_dir.glob(f"*{post_id}*.mp4"))
                    image_files = list(post_dir.glob(f"*{post_id}*.jpg"))
                    
                    video_path = None
                    
                    if video_files:
                        video_path = video_files[0]
                        print(f"  ✓ Downloaded video: {video_path.name}")
                        
                        # Add watermark
                        video_path = self._add_watermark(video_path)
                    
                    elif image_files:
                        image_path = image_files[0]
                        print(f"  ✓ Downloaded image: {image_path.name}")
                        
                        # Convert to video
                        video_path = self._image_to_video(image_path)
                    
                    if video_path and video_path.exists():
                        # Upload to YouTube
                        title = caption[:80] if caption else f"{username} Instagram post"
                        desc = caption if caption else DEFAULT_HASHTAGS
                        
                        if DEFAULT_HASHTAGS not in desc:
                            desc = f"{desc}\n\n{DEFAULT_HASHTAGS}"
                        
                        success = self.uploader.upload(video_path, title, desc)
                        
                        if success:
                            downloaded_count += 1
                            self._cleanup(video_path)
                            self._cleanup(post_dir)
                    
                    # Mark as processed
                    self.processed.append(post_id)
                    self._save_tracking()
                    
                    # Keep only last 1000 entries
                    if len(self.processed) > 1000:
                        self.processed = self.processed[-1000:]
                        self._save_tracking()
                    
                    # Delay between posts
                    time.sleep(random.randint(10, 20))
                
                except instaloader.exceptions.ConnectionException as e:
                    if '429' in str(e) or 'rate limit' in str(e).lower():
                        print(f"  ⚠ Rate limited, waiting 5 minutes...")
                        time.sleep(300)
                    else:
                        print(f"  ✗ Error downloading post: {e}")
                    continue
                except Exception as e:
                    print(f"  ✗ Error downloading post: {e}")
                    continue
            
            if downloaded_count > 0:
                print(f"\n  ✓ Downloaded and uploaded {downloaded_count} post(s)")
            else:
                print(f"\n  → No new posts found")
        
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"  ✗ Profile @{username} not found")
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            print(f"  ✗ Profile @{username} is private")
        except instaloader.exceptions.LoginRequiredException:
            print(f"  ✗ Login required to access @{username}")
            print(f"  → Make sure INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD are set")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    def monitor(self):
        print(f"\n{'='*60}")
        print(f"Instagram to YouTube Downloader")
        print(f"{'='*60}")
        print(f"Using: Instaloader (100% Working)")
        print(f"Check interval: {CHECK_INTERVAL//60} minutes")
        print(f"YouTube: @LahoriTwins")
        print(f"\nAccounts:")
        for username in INSTAGRAM_ACCOUNTS:
            print(f"  - @{username}")
        print(f"\nFeatures:")
        print(f"  ✓ Copyright detection: ENABLED")
        print(f"  ✓ Watermark: ENABLED")
        print(f"  ✓ Image to video: ENABLED")
        print(f"  ✓ Auto upload: ENABLED")
        print(f"{'='*60}\n")
        
        if not INSTALOADER_AVAILABLE:
            print("✗ ERROR: Instaloader not installed!")
            print("→ Install with: pip install instaloader")
            return
        
        while True:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking all accounts...")
                
                for username in INSTAGRAM_ACCOUNTS:
                    self.download_from_account(username)
                    time.sleep(10)  # Delay between accounts
                
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
    print("Instagram to YouTube - Starting...")
    print("="*60 + "\n")
    
    downloader = InstagramDownloader()
    downloader.monitor()
