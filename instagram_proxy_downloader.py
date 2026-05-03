#!/usr/bin/env python3
"""
Instagram to YouTube using Third-Party Downloader APIs
Uses external Instagram downloader services to bypass Railway blocking
Works on Railway!
"""
import os
import sys
import time
import json
from datetime import datetime
import subprocess
from pathlib import Path
import random
import shutil
import requests

# Configure output streams
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding='utf-8', line_buffering=True)
    except:
        pass

os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

BASE_DIR = Path(__file__).resolve().parent

# Import Instagrapi (only for getting post URLs)
try:
    from instagrapi import Client
    INSTAGRAPI_AVAILABLE = True
    print("✓ instagrapi available")
except ImportError:
    INSTAGRAPI_AVAILABLE = False
    print("✗ instagrapi not available")

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
MAX_POSTS_PER_CHECK = 3

def run_cmd(cmd, timeout=None):
    """Run command with UTF-8 encoding"""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, 
                            encoding='utf-8', errors='replace', timeout=timeout)
    except:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

class InstagramDownloaderAPI:
    """Use third-party Instagram downloader APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download_from_url(self, post_url):
        """Download Instagram video using third-party API"""
        
        # Try multiple downloader services
        downloaders = [
            self._download_via_rapidapi,
            self._download_via_downloadgram,
            self._download_via_inflact,
            self._download_via_saveinsta,
        ]
        
        for downloader in downloaders:
            try:
                video_url = downloader(post_url)
                if video_url:
                    return video_url
            except Exception as e:
                print(f"  ⚠ Downloader failed: {str(e)[:100]}")
                continue
        
        return None
    
    def _download_via_rapidapi(self, post_url):
        """RapidAPI Instagram Downloader (free tier)"""
        try:
            print(f"  → Trying RapidAPI...")
            
            # Extract shortcode from URL
            import re
            match = re.search(r'/p/([A-Za-z0-9_-]+)', post_url)
            if not match:
                return None
            
            shortcode = match.group(1)
            
            api_url = f"https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index"
            
            headers = {
                'X-RapidAPI-Key': os.getenv('RAPIDAPI_KEY', ''),
                'X-RapidAPI-Host': 'instagram-downloader-download-instagram-videos-stories.p.rapidapi.com'
            }
            
            params = {'url': post_url}
            
            if not headers['X-RapidAPI-Key']:
                print(f"  ⚠ No RapidAPI key (set RAPIDAPI_KEY env var)")
                return None
            
            response = self.session.get(api_url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('media'):
                    video_url = result['media']
                    print(f"  ✓ Found video URL via RapidAPI")
                    return video_url
            
            return None
        except Exception as e:
            print(f"  ⚠ RapidAPI error: {str(e)[:100]}")
            return None
    
    def _download_via_downloadgram(self, post_url):
        """Downloadgram.com"""
        try:
            print(f"  → Trying Downloadgram.com...")
            
            api_url = "https://downloadgram.org/reel-downloader.php"
            
            data = {
                'url': post_url,
                'submit': ''
            }
            
            response = self.session.post(api_url, data=data, timeout=30)
            
            if response.status_code == 200:
                import re
                # Look for video download link
                video_match = re.search(r'href="(https://[^"]+\.mp4[^"]*)"', response.text)
                
                if video_match:
                    video_url = video_match.group(1)
                    print(f"  ✓ Found video URL via Downloadgram")
                    return video_url
            
            return None
        except Exception as e:
            print(f"  ⚠ Downloadgram error: {str(e)[:100]}")
            return None
    
    def _download_via_inflact(self, post_url):
        """Inflact.com downloader"""
        try:
            print(f"  → Trying Inflact.com...")
            
            api_url = "https://inflact.com/downloader/instagram/video"
            
            data = {
                'url': post_url
            }
            
            response = self.session.post(api_url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('url'):
                    video_url = result['url']
                    print(f"  ✓ Found video URL via Inflact")
                    return video_url
            
            return None
        except Exception as e:
            print(f"  ⚠ Inflact error: {str(e)[:100]}")
            return None
    
    def _download_via_saveinsta(self, post_url):
        """SaveInsta.app API"""
        try:
            print(f"  → Trying SaveInsta.app...")
            
            api_url = "https://v3.saveinsta.app/api/ajaxSearch"
            
            data = {
                'q': post_url,
                'lang': 'en'
            }
            
            response = self.session.post(api_url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'ok':
                    # Parse HTML to find download link
                    html = result.get('data', '')
                    
                    # Look for video download link
                    import re
                    video_match = re.search(r'href="([^"]+)"[^>]*>Download', html)
                    
                    if video_match:
                        video_url = video_match.group(1)
                        print(f"  ✓ Found video URL via SaveInsta")
                        return video_url
            
            return None
        except Exception as e:
            print(f"  ⚠ SaveInsta error: {e}")
            return None
    
    def _download_via_instadownloader(self, post_url):
        """InstaDownloader.co API"""
        try:
            print(f"  → Trying InstaDownloader.co...")
            
            api_url = "https://instadownloader.co/wp-json/aio-dl/video-data/"
            
            data = {
                'url': post_url
            }
            
            response = self.session.post(api_url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('medias'):
                    for media in result['medias']:
                        if media.get('url'):
                            video_url = media['url']
                            print(f"  ✓ Found video URL via InstaDownloader")
                            return video_url
            
            return None
        except Exception as e:
            print(f"  ⚠ InstaDownloader error: {e}")
            return None
    
    def _download_via_snapinsta(self, post_url):
        """SnapInsta.app API"""
        try:
            print(f"  → Trying SnapInsta.app...")
            
            api_url = "https://snapinsta.app/api/ajaxSearch"
            
            data = {
                'q': post_url,
                'lang': 'en'
            }
            
            response = self.session.post(api_url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'ok':
                    html = result.get('data', '')
                    
                    import re
                    video_match = re.search(r'href="([^"]+)"[^>]*download', html, re.IGNORECASE)
                    
                    if video_match:
                        video_url = video_match.group(1)
                        print(f"  ✓ Found video URL via SnapInsta")
                        return video_url
            
            return None
        except Exception as e:
            print(f"  ⚠ SnapInsta error: {e}")
            return None

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
            print("⚠ YouTube upload disabled")
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

class InstagramMonitor:
    def __init__(self):
        self.temp_dir = BASE_DIR / 'temp_downloads'
        self.temp_dir.mkdir(exist_ok=True)
        
        self.tracking_file = BASE_DIR / 'processed_posts.json'
        self.processed = self._load_tracking()
        
        self.uploader = YouTubeUploader()
        self.downloader_api = InstagramDownloaderAPI()
        
        self.audio_tracks = [BASE_DIR / 'Track 1.mpeg', BASE_DIR / 'Track 2.mpeg']
        
        print("✓ Using public scraper APIs (no Instagram blocking)")
    
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
            print(f"  ⚠ Could not delete: {e}")
    
    def _download_video_file(self, video_url, filename):
        """Download video from URL"""
        try:
            print(f"  → Downloading video file...")
            
            response = requests.get(video_url, stream=True, timeout=120)
            
            if response.status_code == 200:
                video_path = self.temp_dir / filename
                
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"  ✓ Downloaded: {video_path.name}")
                return video_path
            
            return None
        except Exception as e:
            print(f"  ✗ Download error: {e}")
            return None
    
    def _add_watermark(self, video_path):
        """Add watermark"""
        try:
            output_path = video_path.parent / f"{video_path.stem}_watermarked.mp4"
            
            cmd = [
                'ffmpeg', '-i', str(video_path),
                '-vf', "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='Lahori Twins':fontsize=28:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2",
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                '-c:a', 'copy', '-y', str(output_path)
            ]
            
            result = run_cmd(cmd, timeout=300)
            
            if result.returncode == 0 and output_path.exists():
                print(f"  ✓ Watermark added")
                self._cleanup(video_path)
                return output_path
            
            return video_path
        except Exception as e:
            print(f"  ⚠ Watermark error: {e}")
            return video_path
    
    def check_account(self, username):
        """Check Instagram account for new posts"""
        try:
            print(f"\n→ Checking @{username}")
            
            # Get recent posts using public scraper API instead of instagrapi
            posts = self._get_posts_via_scraper(username)
            
            if not posts:
                print(f"  ✗ Could not get posts")
                return
            
            print(f"  → Found {len(posts)} recent posts")
            
            uploaded_count = 0
            
            for post in posts[:MAX_POSTS_PER_CHECK]:
                post_code = post.get('code')
                
                if not post_code or post_code in self.processed:
                    continue
                
                print(f"\n  → Post: {post_code}")
                print(f"    Likes: {post.get('likes', 0)}")
                
                # Build Instagram URL
                post_url = f"https://www.instagram.com/p/{post_code}/"
                print(f"    URL: {post_url}")
                
                # Get video download URL from third-party API
                video_url = self.downloader_api.download_from_url(post_url)
                
                if video_url:
                    # Download video file
                    video_path = self._download_video_file(video_url, f"{post_code}.mp4")
                    
                    if video_path and video_path.exists():
                        # Add watermark
                        video_path = self._add_watermark(video_path)
                        
                        # Upload to YouTube
                        caption = post.get('caption', '')
                        title = caption[:80] if caption else f"{username} post"
                        desc = caption if caption else DEFAULT_HASHTAGS
                        
                        if DEFAULT_HASHTAGS not in desc:
                            desc = f"{desc}\n\n{DEFAULT_HASHTAGS}"
                        
                        success = self.uploader.upload(video_path, title, desc)
                        
                        if success:
                            uploaded_count += 1
                            self._cleanup(video_path)
                else:
                    print(f"  ✗ Could not get download URL")
                
                # Mark as processed
                self.processed.append(post_code)
                self._save_tracking()
                
                if len(self.processed) > 1000:
                    self.processed = self.processed[-1000:]
                    self._save_tracking()
                
                time.sleep(random.randint(15, 30))
            
            if uploaded_count > 0:
                print(f"\n  ✓ Uploaded {uploaded_count} video(s)")
            else:
                print(f"\n  → No new videos")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    def _get_posts_via_scraper(self, username):
        """Get posts using public scraper API (no Instagram API calls)"""
        try:
            # Try multiple public scraper APIs
            scrapers = [
                lambda: self._scrape_via_rapidapi(username),
                lambda: self._scrape_via_apify(username),
            ]
            
            for scraper in scrapers:
                try:
                    posts = scraper()
                    if posts:
                        return posts
                except Exception as e:
                    print(f"  ⚠ Scraper failed: {str(e)[:100]}")
                    continue
            
            return []
        except Exception as e:
            print(f"  ✗ Scraper error: {e}")
            return []
    
    def _scrape_via_rapidapi(self, username):
        """Use RapidAPI Instagram scraper"""
        try:
            print(f"  → Getting posts via RapidAPI...")
            
            api_key = os.getenv('RAPIDAPI_KEY', '')
            if not api_key:
                print(f"  ⚠ No RapidAPI key")
                return []
            
            # Try to get user posts - we'll construct URLs manually since API might not have posts endpoint
            # Instead, we'll use a simpler approach: just get the latest post codes from the profile
            
            # For now, let's use a workaround: manually construct post URLs
            # This is a limitation of the free API tier
            
            print(f"  ⚠ RapidAPI endpoint doesn't support post listing")
            print(f"  → Trying alternative method...")
            
            # Alternative: Use public Instagram profile page scraping
            return self._scrape_public_profile(username)
            
        except Exception as e:
            print(f"  ⚠ RapidAPI scraper error: {str(e)[:100]}")
            return []
    
    def _scrape_public_profile(self, username):
        """Scrape public Instagram profile page directly"""
        try:
            print(f"  → Scraping public profile page...")
            
            url = f"https://www.instagram.com/{username}/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                import re
                
                # Extract post shortcodes from the page
                # Instagram embeds data in script tags
                shortcode_pattern = r'"shortcode":"([A-Za-z0-9_-]+)"'
                shortcodes = re.findall(shortcode_pattern, response.text)
                
                if shortcodes:
                    # Remove duplicates and take first few
                    unique_codes = list(dict.fromkeys(shortcodes))[:MAX_POSTS_PER_CHECK]
                    
                    posts = []
                    for code in unique_codes:
                        posts.append({
                            'code': code,
                            'likes': 0,
                            'caption': ''
                        })
                    
                    print(f"  ✓ Found {len(posts)} posts from profile page")
                    return posts
                else:
                    print(f"  ⚠ No posts found on profile page")
            else:
                print(f"  ⚠ Profile page returned status {response.status_code}")
            
            return []
        except Exception as e:
            print(f"  ⚠ Profile scraping error: {str(e)[:100]}")
            return []
    
    def _scrape_via_apify(self, username):
        """Use Apify Instagram scraper"""
        try:
            print(f"  → Getting posts via Apify...")
            
            # Apify requires API token
            api_token = os.getenv('APIFY_TOKEN', '')
            if not api_token:
                print(f"  ⚠ No Apify token")
                return []
            
            # This would require Apify setup
            # Placeholder for now
            return []
        except Exception as e:
            print(f"  ⚠ Apify error: {str(e)[:100]}")
            return []
    
    def monitor(self):
        print(f"\n{'='*60}")
        print(f"Instagram to YouTube - Third-Party Downloader")
        print(f"{'='*60}")
        print(f"Using: External downloader APIs")
        print(f"Check interval: {CHECK_INTERVAL//60} minutes")
        print(f"YouTube: @LahoriTwins")
        print(f"\nMonitoring:")
        for username in INSTAGRAM_ACCOUNTS:
            print(f"  - @{username}")
        print(f"{'='*60}\n")
        
        while True:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking accounts...")
                
                for username in INSTAGRAM_ACCOUNTS:
                    self.check_account(username)
                    time.sleep(30)
                
                print(f"\n→ Next check in {CHECK_INTERVAL//60} minutes\n")
                time.sleep(CHECK_INTERVAL)
            
            except KeyboardInterrupt:
                print("\n\n⚠ Stopped")
                break
            except Exception as e:
                print(f"✗ Error: {e}")
                time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Instagram to YouTube - Starting...")
    print("="*60 + "\n")
    
    monitor = InstagramMonitor()
    monitor.monitor()
