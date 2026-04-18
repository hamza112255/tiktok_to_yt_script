import os
import sys
import time
import json
import re
from datetime import datetime
import subprocess
from pathlib import Path

def _configure_output_streams():
    """Keep logs visible in containerized/non-interactive environments."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', line_buffering=True)
        except Exception:
            try:
                stream.reconfigure(line_buffering=True)
            except Exception:
                pass

_configure_output_streams()

print("DEBUG: Starting imports...")
sys.stdout.flush()

# Fix console encoding for Unicode characters and subprocess output
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

IS_RAILWAY = any(
    os.getenv(name) for name in (
        'RAILWAY_PROJECT_ID',
        'RAILWAY_SERVICE_ID',
        'RAILWAY_ENVIRONMENT_ID',
        'RAILWAY_DEPLOYMENT_ID',
    )
)
IS_NON_INTERACTIVE = IS_RAILWAY or not sys.stdin.isatty()

print("DEBUG: Importing video processor...")
sys.stdout.flush()

# Import video processor
try:
    from video_processor import VideoProcessor
    VIDEO_PROCESSOR_AVAILABLE = True
    print("DEBUG: Video processor imported successfully")
except ImportError as e:
    VIDEO_PROCESSOR_AVAILABLE = False
    print(f"Warning: Video processor not available: {e}")

sys.stdout.flush()

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.m4v', '.mkv', '.webm'}

BASE_DIR = Path(__file__).resolve().parent

print("DEBUG: Importing YouTube API libraries...")
sys.stdout.flush()

def run_command(cmd, timeout=None):
    """Run subprocess command with proper UTF-8 encoding"""
    try:
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace',
            timeout=timeout
        )
    except Exception as e:
        # Fallback without encoding parameter for older Python
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )

def resolve_path(path_value):
    path = Path(path_value)
    return path if path.is_absolute() else (BASE_DIR / path)

print("DEBUG: Importing YouTube API libraries...")
sys.stdout.flush()

# YouTube API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    YOUTUBE_API_AVAILABLE = True
    print("DEBUG: YouTube API libraries imported successfully")
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("DEBUG: YouTube API libraries not available")

sys.stdout.flush()

print("DEBUG: Defining load_config function...")
sys.stdout.flush()

def load_config():
    """Load configuration from config.json file"""
    config_file = BASE_DIR / 'config.json'
    
    if not config_file.exists():
        print(f"⚠ Config file not found: {config_file}")
        print("Creating default config file...")
        
        default_config = {
            "tiktok_username": "username",
            "check_interval_minutes": 5,
            "youtube_settings": {
                "channel_name": "My YouTube Channel",
                "shorts_folder": "youtube_ready/shorts",
                "main_videos_folder": "youtube_ready/main",
                "auto_organize": True,
                "organize_by_date": False,
                "auto_upload_to_youtube": False,
                "always_prompt_account": False,
                "title_suffix": " | TikTok",
                "use_tiktok_hashtags": False,
                "skip_copyrighted": True,
                "skip_non_original_audio": True,
                "copyright_keywords": ["copyright", "all rights reserved", "(c)"],
                "copyright_risk_action": "skip",
                "copyright_risk_privacy": "private",
                "upload_as_shorts": True,
                "video_privacy": "private",
                "default_title_prefix": "",
                "default_description": "#shorts #tiktok",
                "add_watermark": False,
                "watermark_text": "Lahori Twins",
                "skip_female_videos": False,
                "split_long_videos": False,
                "split_duration_seconds": 30,
                "min_segment_duration_seconds": 20
            },
            "download_settings": {
                "video_quality": "high",
                "remove_watermark": True,
                "save_video_info": True,
                "download_latest_only": True,
                "max_videos_per_check": 1
            },
            "notifications": {
                "show_download_progress": True,
                "play_sound_on_new_video": False
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"✓ Created {config_file.name}")
        print(f"→ Please edit {config_file.name} and set your TikTok username\n")
        return default_config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"✗ Error reading config file: {e}")
        return None

print("DEBUG: Defining YouTubeUploader class...")
sys.stdout.flush()

class YouTubeUploader:
    """Handle YouTube uploads"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, config):
        self.config = config
        self.youtube = None
        self.enabled = config['youtube_settings'].get('auto_upload_to_youtube', False)
        
        if self.enabled:
            if not YOUTUBE_API_AVAILABLE:
                print("⚠ YouTube API libraries not installed!")
                print("→ Run: pip install google-api-python-client google-auth-oauthlib")
                self.enabled = False
            else:
                self._authenticate()
    
    def _authenticate(self):
        """Authenticate with YouTube API"""
        try:
            creds = None
            token_file = BASE_DIR / 'token.json'
            client_secret_file = BASE_DIR / 'client_secret.json'
            force_prompt = self.config['youtube_settings'].get('always_prompt_account', False)
            token_exists = token_file.exists()
            interactive_auth_allowed = not IS_NON_INTERACTIVE
            
            if force_prompt and not interactive_auth_allowed:
                print("always_prompt_account is enabled, but interactive auth is unavailable here.")
                print("-> Ignoring always_prompt_account and trying the saved token instead.")
                force_prompt = False
            
            # Check if client_secret.json exists
            if not client_secret_file.exists():
                print("⚠ client_secret.json not found!")
                print("→ Download OAuth credentials from Google Cloud Console")
                print("→ Save as 'client_secret.json' in this folder")
                print("→ See SETUP_AND_RUN.txt for step-by-step setup")
                self.enabled = False
                return
            
            # Warn if credentials are not Desktop App type (recommended for scripts)
            try:
                secret_data = json.loads(client_secret_file.read_text(encoding='utf-8'))
                if 'installed' not in secret_data and 'web' in secret_data:
                    print("⚠ client_secret.json looks like a Web OAuth client.")
                    print("→ For this script, create OAuth credentials as: Desktop app")
                    print("→ See SETUP_AND_RUN.txt (Section 5.4)")
            except Exception:
                pass
            
            # Load existing token
            if force_prompt and token_exists:
                print("Note: always_prompt_account is enabled; ignoring saved token.json.")
            if token_exists and not force_prompt:
                creds = Credentials.from_authorized_user_file(str(token_file), self.SCOPES)
            
            # Refresh or get new token
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("-> Refreshing YouTube token...")
                    try:
                        creds.refresh(Request())
                        print("✓ YouTube token refreshed successfully")
                    except Exception as refresh_error:
                        print(f"Saved YouTube token could not be refreshed: {refresh_error}")
                        creds = None
                
                if not creds or not creds.valid:
                    if not interactive_auth_allowed:
                        print("Interactive YouTube OAuth is disabled in Railway/non-interactive mode.")
                        print("-> Generate a fresh token.json locally and redeploy, or set AUTO_UPLOAD_TO_YOUTUBE=false.")
                        self.enabled = False
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_file), self.SCOPES)
                    try:
                        try:
                            creds = flow.run_local_server(port=0, access_type='offline', prompt='select_account consent')
                        except TypeError:
                            creds = flow.run_local_server(port=0)
                    except Exception:
                        try:
                            creds = flow.run_console(access_type='offline', prompt='select_account consent')
                        except TypeError:
                            creds = flow.run_console()
                
                # Save token
                if creds:
                    token_file.write_text(creds.to_json(), encoding='utf-8')
                    if not creds.refresh_token:
                        print("⚠ No refresh token received; you may be asked to authorize again later.")
                        print("→ If that happens, delete token.json and re-run once to re-authorize.")
            
            self.youtube = build('youtube', 'v3', credentials=creds)
            print("✓ YouTube API authenticated successfully!")
            
        except Exception as e:
            print(f"✗ YouTube authentication failed: {e}")
            self.enabled = False
    
    def upload_video(self, video_path, title, description, privacy=None):
        """Upload video to YouTube"""
        if not self.enabled or not self.youtube:
            return False
        
        try:
            print(f"→ Uploading to YouTube: {video_path.name}")
            
            # Prepare video metadata
            privacy = privacy or self.config['youtube_settings'].get('video_privacy', 'private')
            is_shorts = self.config['youtube_settings'].get('upload_as_shorts', True)
            
            # Add #Shorts to title if uploading as Shorts
            if is_shorts and '#Shorts' not in title and '#shorts' not in title:
                title = f"{title} #Shorts"
            
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description[:5000],  # YouTube description limit
                    'tags': ['shorts', 'tiktok', 'viral'],
                    'categoryId': '24'  # Entertainment category
                },
                'status': {
                    'privacyStatus': privacy,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload video
            media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
            
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"  → Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            print(f"✓ Uploaded to YouTube!")
            print(f"  → Video ID: {video_id}")
            print(f"  → URL: {video_url}")
            print(f"  → Privacy: {privacy}")
            
            return True
            
        except Exception as e:
            print(f"✗ YouTube upload failed: {e}")
            return False

print("DEBUG: Defining TikTokToYouTube class...")
sys.stdout.flush()

class TikTokToYouTube:
    def __init__(self, config):
        self.config = config
        self.username = config['tiktok_username'].replace('@', '')
        self.check_interval = config['check_interval_minutes'] * 60  # Convert to seconds
        
        # YouTube settings
        self.channel_name = config['youtube_settings'].get('channel_name', 'My YouTube Channel')
        self.channel_id = config['youtube_settings'].get('channel_id', '')
        
        # YouTube folders from config
        self.youtube_folder = resolve_path('youtube_ready')
        shorts_root = resolve_path(config['youtube_settings'].get('shorts_folder', 'youtube_ready/shorts'))
        main_root = resolve_path(config['youtube_settings'].get('main_videos_folder', 'youtube_ready/main'))
        
        # Create channel-specific folders if channel name is provided
        if self.channel_name and self.channel_name != "My YouTube Channel":
            safe_channel_name = "".join(c for c in self.channel_name if c.isalnum() or c in (' ', '-', '_')).strip()
            self.shorts_folder = shorts_root / safe_channel_name
            self.main_folder = main_root / safe_channel_name
        else:
            self.shorts_folder = shorts_root
            self.main_folder = main_root
        
        self.downloads_folder = resolve_path('downloaded_videos')
        self.tracking_file = BASE_DIR / 'downloaded_videos.json'
        
        self._setup_folders()
        self.downloaded_ids = self._load_tracking()
        
        # Initialize YouTube uploader
        self.youtube_uploader = YouTubeUploader(config)
        
        # Initialize video processor
        if VIDEO_PROCESSOR_AVAILABLE:
            self.video_processor = VideoProcessor(config)
        else:
            self.video_processor = None
    
    def _is_video_file(self, path):
        return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    
    def _ytdlp_cookies_args(self):
        cookies_file = BASE_DIR / 'cookies.txt'
        return ['--cookies', str(cookies_file)] if cookies_file.exists() else []
    
    def _dedupe_hashtags(self, tags):
        result = []
        seen = set()
        
        for tag in tags or []:
            tag = tag.strip()
            if not tag:
                continue
            if not tag.startswith('#'):
                tag = f"#{tag}"
            key = tag.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(tag)
        
        return result
    
    def _extract_hashtags(self, text):
        if not text:
            return []
        tags = re.findall(r"#\\w+", text)
        return self._dedupe_hashtags(tags)
    
    def _strip_hashtags(self, text):
        if not text:
            return ""
        cleaned = re.sub(r"#\\w+", "", text)
        return " ".join(cleaned.split())
    
    def _get_info_path(self, video_path):
        shorts_path = None
        try:
            video_path.relative_to(self.shorts_folder)
            shorts_path = video_path
        except ValueError:
            try:
                rel = video_path.relative_to(self.main_folder)
                shorts_path = self.shorts_folder / rel
            except ValueError:
                shorts_path = None
        
        if not shorts_path:
            return None
        
        return shorts_path.parent / f"{shorts_path.stem}_info.txt"
    
    def _read_info_metadata(self, video_path):
        info = {}
        info_path = self._get_info_path(video_path)
        if not info_path or not info_path.exists():
            return info
        
        try:
            with open(info_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("Title:"):
                        info['title'] = line.split(":", 1)[1].strip()
                    elif line.startswith("Hashtags:"):
                        tags_value = line.split(":", 1)[1].strip()
                        info['hashtags'] = self._dedupe_hashtags(tags_value.split())
                    elif line.startswith("Audio:"):
                        info['audio'] = line.split(":", 1)[1].strip()
                    elif line.startswith("Artist:"):
                        info['artist'] = line.split(":", 1)[1].strip()
        except Exception:
            return info
        
        return info
    
    def _fetch_tiktok_metadata(self, video_url):
        try:
            cmd = ['yt-dlp']
            cmd.extend(self._ytdlp_cookies_args())
            cmd.extend([
                '--skip-download',
                '--no-playlist',
                '--quiet',
                '--no-warnings',
                '--print', 'title',
                '--print', 'track',
                '--print', 'artist',
                video_url
            ])
            
            result = run_command(cmd, timeout=60)
            if result.returncode != 0:
                return {}
            
            lines = [line.strip() for line in result.stdout.splitlines()]
            fields = ['title', 'track', 'artist']
            data = {}
            for i, field in enumerate(fields):
                if i < len(lines):
                    value = lines[i]
                    if value and value.upper() not in {"NA", "N/A"}:
                        data[field] = value
            
            caption = data.get('title', '')
            if caption:
                data['caption'] = caption
                data['hashtags'] = self._extract_hashtags(caption)
            
            return data
        except Exception:
            return {}
    
    def _build_title(self, caption, hashtags):
        title_prefix = self.config['youtube_settings'].get('default_title_prefix', '')
        title_suffix = self.config['youtube_settings'].get('title_suffix', '')
        
        base_text = self._strip_hashtags(caption) if caption else ""
        if not base_text:
            base_text = caption or "TikTok Video"
        
        if title_suffix and not base_text.endswith(title_suffix):
            base_text = f"{base_text}{title_suffix}"
        
        base_title = f"{title_prefix}{base_text}".strip()
        base_title = base_title[:100].rstrip()
        
        if not hashtags:
            return base_title
        
        tags_text = " ".join(hashtags)
        candidate = f"{base_title} {tags_text}".strip()
        if len(candidate) <= 100:
            return candidate
        
        trimmed = base_title
        for tag in hashtags:
            if len(trimmed) + 1 + len(tag) <= 100:
                trimmed = f"{trimmed} {tag}"
            else:
                break
        
        if trimmed != base_title:
            return trimmed
        
        return base_title[:100].rstrip()
    
    def _build_description(self, caption, hashtags):
        default_description = self.config['youtube_settings'].get('default_description', '')
        
        parts = []
        caption_text = self._strip_hashtags(caption) if caption else ""
        if caption_text:
            parts.append(caption_text)
        
        default_text = self._strip_hashtags(default_description)
        if default_text:
            parts.append(default_text)
        
        combined_tags = self._dedupe_hashtags(self._extract_hashtags(default_description) + (hashtags or []))
        if combined_tags:
            parts.append(" ".join(combined_tags))
        
        return "\n\n".join(p for p in parts if p).strip()
    
    def _get_upload_decision(self, metadata):
        default_privacy = self.config['youtube_settings'].get('video_privacy', 'private')
        risk_action = str(self.config['youtube_settings'].get('copyright_risk_action', 'skip')).lower()
        risk_privacy = self.config['youtube_settings'].get('copyright_risk_privacy', 'private')
        
        caption = (metadata or {}).get('caption', '') or ""
        caption_lower = caption.lower()
        keywords = self.config['youtube_settings'].get('copyright_keywords', [])
        for keyword in keywords:
            if keyword and keyword.lower() in caption_lower and self.config['youtube_settings'].get('skip_copyrighted', False):
                if risk_action == 'private':
                    return True, risk_privacy, f"keyword '{keyword}'"
                return False, None, f"keyword '{keyword}'"
        
        if self.config['youtube_settings'].get('skip_non_original_audio', False):
            audio = (metadata or {}).get('audio', '') or ""
            if audio and "original sound" not in audio.lower():
                if risk_action == 'private':
                    return True, risk_privacy, "non-original audio"
                return False, None, "non-original audio"
        
        return True, default_privacy, None
    
    def _skip_upload(self, video_path, reason):
        skip_root = resolve_path(self.config['youtube_settings'].get(
            'skip_folder',
            'youtube_ready/skipped_copyright'
        ))
        skip_root.mkdir(parents=True, exist_ok=True)
        
        relative_path = None
        source_root = None
        try:
            relative_path = video_path.relative_to(self.shorts_folder)
            source_root = self.shorts_folder
        except ValueError:
            try:
                relative_path = video_path.relative_to(self.main_folder)
                source_root = self.main_folder
            except ValueError:
                relative_path = None
        
        if relative_path is None:
            return
        
        dest_path = skip_root / relative_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import shutil
            shutil.move(str(video_path), str(dest_path))
        except Exception as e:
            print(f"⚠ Could not move skipped video: {e}")
            return
        
        other_root = self.main_folder if source_root == self.shorts_folder else self.shorts_folder
        other_path = other_root / relative_path
        self._safe_delete(other_path)
        
        info_path = self._get_info_path(video_path)
        if info_path and info_path.exists():
            info_dest = dest_path.parent / info_path.name
            try:
                import shutil
                shutil.move(str(info_path), str(info_dest))
            except Exception:
                pass
        
        self._cleanup_empty_folders(dest_path.parent, skip_root)
        self._cleanup_empty_folders((self.shorts_folder / relative_path).parent, self.shorts_folder)
        self._cleanup_empty_folders((self.main_folder / relative_path).parent, self.main_folder)
        
        print(f"→ Skipped upload ({reason}). Moved to: {dest_path.parent}")
    
    def _safe_delete(self, path):
        try:
            if path and path.exists():
                path.unlink()
        except Exception as e:
            print(f"⚠ Could not delete {path}: {e}")
    
    def _cleanup_empty_folders(self, folder, stop_at):
        try:
            current = folder
            while current and current.exists() and current != stop_at:
                if any(current.iterdir()):
                    break
                current.rmdir()
                current = current.parent
        except Exception:
            return
    
    def _cleanup_uploaded_video(self, uploaded_path):
        """Delete uploaded video (and its duplicate copy/info file) from local folders"""
        relative_path = None
        try:
            relative_path = uploaded_path.relative_to(self.shorts_folder)
        except ValueError:
            try:
                relative_path = uploaded_path.relative_to(self.main_folder)
            except ValueError:
                relative_path = None
        
        if relative_path is None:
            self._safe_delete(uploaded_path)
            return
        
        shorts_path = self.shorts_folder / relative_path
        main_path = self.main_folder / relative_path
        
        self._safe_delete(shorts_path)
        self._safe_delete(main_path)
        
        info_path = shorts_path.parent / f"{shorts_path.stem}_info.txt"
        self._safe_delete(info_path)
        
        self._cleanup_empty_folders(shorts_path.parent, self.shorts_folder)
        self._cleanup_empty_folders(main_path.parent, self.main_folder)
    
    def _get_title_from_info_file(self, video_path):
        info = self._read_info_metadata(video_path)
        title = info.get('title')
        if title and title.lower() != "n/a":
            return title
        return None
    
    def _get_title_from_filename(self, video_path):
        try:
            import re
            match = re.match(r'^\\d{8}_\\d{6}_(.+?)_(\\d+)(?:_part\\d+)?$', video_path.stem)
            if match:
                name_part = match.group(1).strip()
                if name_part.lower() in {"manual", "video", "untitled"}:
                    return "TikTok Video"
                # Clean up the title
                title = name_part.replace("_", " ").strip()
                return title if title else "TikTok Video"
        except Exception:
            pass
        
        return video_path.stem.replace("_", " ").strip() if video_path.stem else None
    
    def _build_upload_metadata(self, video_path, metadata=None):
        info = self._read_info_metadata(video_path)
        
        caption = None
        hashtags = []
        audio = None
        artist = None
        
        if metadata:
            caption = metadata.get('caption') or metadata.get('title')
            hashtags = metadata.get('hashtags') or []
            audio = metadata.get('audio') or metadata.get('track')
            artist = metadata.get('artist')
        
        if not caption:
            caption = info.get('title') or self._get_title_from_filename(video_path) or "TikTok Video"
        
        if not hashtags:
            if info.get('hashtags'):
                hashtags = info.get('hashtags')
            else:
                hashtags = self._extract_hashtags(caption)
        
        if isinstance(hashtags, str):
            hashtags = hashtags.split()
        
        hashtags = self._dedupe_hashtags(hashtags)
        
        if not audio:
            audio = info.get('audio')
        if not artist:
            artist = info.get('artist')
        
        use_hashtags = self.config['youtube_settings'].get('use_tiktok_hashtags', True)
        tags_to_use = hashtags if use_hashtags else []
        
        title = self._build_title(caption, tags_to_use)
        description = self._build_description(caption, tags_to_use)
        
        merged = {
            'caption': caption,
            'hashtags': hashtags,
            'audio': audio,
            'artist': artist
        }
        
        return title, description, merged
    
    def _list_pending_videos(self):
        """List pending videos from shorts folder only (main folder is just a backup)"""
        pending = {}
        
        # Only check shorts folder for uploads (main folder is just a backup copy)
        if not self.shorts_folder.exists():
            return []
        
        for file_path in self.shorts_folder.rglob('*'):
            if not self._is_video_file(file_path):
                continue
            
            try:
                rel = file_path.relative_to(self.shorts_folder)
            except ValueError:
                continue
            
            key = str(rel).lower()
            if key in pending:
                continue
            
            pending[key] = file_path
        
        try:
            return sorted(pending.values(), key=lambda p: p.stat().st_mtime)
        except Exception:
            return [p for p in pending.values() if p.exists()]
    
    def upload_pending_videos(self):
        """Upload any existing videos in youtube_ready first (oldest first), then delete them"""
        if not self.youtube_uploader.enabled:
            return 0
        
        pending_videos = self._list_pending_videos()
        if not pending_videos:
            return 0
        
        print(f"→ Found {len(pending_videos)} pending video(s) in folders. Uploading oldest first...")
        
        uploaded_count = 0
        for video_path in pending_videos:
            # Process video (watermark, female detection, split)
            if self.video_processor:
                should_skip, processed_files = self.video_processor.process_video(video_path)
                
                if should_skip:
                    # Skip this video (e.g., female detected)
                    self._safe_delete(video_path)
                    continue
                
                # Use processed files for upload
                video_files_to_upload = processed_files
            else:
                video_files_to_upload = [video_path]
            
            # Upload each processed file
            for idx, video_file in enumerate(video_files_to_upload):
                # Build title without part numbers
                title, description, meta = self._build_upload_metadata(video_file)
                
                should_upload, privacy, reason = self._get_upload_decision(meta)
                if not should_upload:
                    self._skip_upload(video_file, reason)
                    continue
                if reason:
                    print(f"-> Upload policy match ({reason}). Uploading as {privacy}.")
                
                success = self.youtube_uploader.upload_video(video_file, title, description, privacy=privacy)
                if not success:
                    print("⚠ Pending upload failed; will retry on next check.")
                    break
                
                self._cleanup_uploaded_video(video_file)
                uploaded_count += 1
        
        if uploaded_count:
            print(f"✓ Uploaded and deleted {uploaded_count} pending video(s)")
        
        return uploaded_count
    
    def _setup_folders(self):
        """Create necessary folders"""
        self.downloads_folder.mkdir(parents=True, exist_ok=True)
        self.youtube_folder.mkdir(parents=True, exist_ok=True)
        self.shorts_folder.mkdir(parents=True, exist_ok=True)
        self.main_folder.mkdir(parents=True, exist_ok=True)
        print(f"✓ Folders created: {self.youtube_folder}")
    
    def _load_tracking(self):
        """Load previously downloaded video IDs"""
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_tracking(self):
        """Save downloaded video IDs"""
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.downloaded_ids, f, indent=2)
    
    def check_manual_urls(self):
        """Check for manually added URLs in video_urls.txt"""
        url_file = BASE_DIR / 'video_urls.txt'
        if not url_file.exists():
            return []
        
        try:
            with open(url_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            urls = []
            for line in lines:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#') and 'tiktok.com' in line:
                    urls.append(line)
            
            return urls
        except Exception as e:
            print(f"✗ Error reading video_urls.txt: {e}")
            return []
    
    def download_from_url(self, url):
        """Download a TikTok video from URL"""
        try:
            # Extract video ID from URL
            import re
            match = re.search(r'/video/(\d+)', url)
            if not match:
                print(f"✗ Invalid URL format: {url}")
                return None
            
            video_id = match.group(1)
            
            if video_id in self.downloaded_ids:
                print(f"→ Video {video_id} already downloaded, skipping")
                return None
            
            print(f"→ Downloading from URL: {url}")
            
            metadata = self._fetch_tiktok_metadata(url)
            title_for_filename = metadata.get('title') or "manual"
            
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_title = "".join(c for c in title_for_filename[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_title:
                safe_title = "video"
            filename = f"{timestamp}_{safe_title}_{video_id}.mp4"
            
            # Organize by date if enabled
            if self.config['youtube_settings'].get('organize_by_date', False):
                date_folder = datetime.now().strftime('%Y-%m-%d')
                shorts_path = self.shorts_folder / date_folder / filename
                main_path = self.main_folder / date_folder / filename
                
                # Create date folders
                (self.shorts_folder / date_folder).mkdir(parents=True, exist_ok=True)
                (self.main_folder / date_folder).mkdir(parents=True, exist_ok=True)
            else:
                shorts_path = self.shorts_folder / filename
                main_path = self.main_folder / filename
            
            # Download using yt-dlp
            cmd = ['yt-dlp']
            cmd.extend(self._ytdlp_cookies_args())
            cmd.extend([
                '-o', str(shorts_path),
                '--no-playlist',
                '--quiet',
                '--no-warnings',
                url
            ])
            
            result = run_command(cmd, timeout=180)
            
            if result.returncode != 0:
                print(f"✗ Failed to download from URL")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}")
                return None
            
            # Copy to main folder
            if shorts_path.exists():
                import shutil
                shutil.copy2(shorts_path, main_path)
            else:
                print(f"✗ Video file not found after download")
                return None
            
            # Save video info if enabled
            if self.config['download_settings'].get('save_video_info', True):
                info_filename = f"{timestamp}_{safe_title}_{video_id}_info.txt"
                
                if self.config['youtube_settings'].get('organize_by_date', False):
                    info_path = self.shorts_folder / date_folder / info_filename
                else:
                    info_path = self.shorts_folder / info_filename
                
                title_for_info = metadata.get('title') or title_for_filename
                hashtags = metadata.get('hashtags') or self._extract_hashtags(title_for_info)
                
                with open(info_path, 'w', encoding='utf-8') as f:
                    f.write(f"TikTok Video Information\n")
                    f.write(f"========================\n\n")
                    f.write(f"Video ID: {video_id}\n")
                    f.write(f"Title: {title_for_info}\n")
                    if hashtags:
                        f.write(f"Hashtags: {' '.join(hashtags)}\n")
                    if metadata.get('track'):
                        f.write(f"Audio: {metadata.get('track')}\n")
                    if metadata.get('artist'):
                        f.write(f"Artist: {metadata.get('artist')}\n")
                    f.write(f"Author: @{self.username}\n")
                    f.write(f"Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Original URL: {url}\n")
                    if self.channel_name:
                        f.write(f"\nYouTube Channel: {self.channel_name}\n")
                    if self.channel_id:
                        f.write(f"YouTube Channel ID: {self.channel_id}\n")
            
            # Track this video
            self.downloaded_ids.append(video_id)
            self._save_tracking()
            
            print(f"✓ Downloaded: {filename}")
            print(f"  → Saved to: {shorts_path.parent}")
            
            # Process video (watermark, female detection, split)
            if self.video_processor:
                should_skip, processed_files = self.video_processor.process_video(shorts_path)
                
                if should_skip:
                    # Skip this video (e.g., female detected)
                    self._safe_delete(shorts_path)
                    self._safe_delete(main_path)
                    return None
                
                # Use processed files for upload
                video_files_to_upload = processed_files
            else:
                video_files_to_upload = [shorts_path]
            
            # Upload to YouTube if enabled
            if self.youtube_uploader.enabled:
                for idx, video_file in enumerate(video_files_to_upload):
                    # Update main_path for each part
                    if len(video_files_to_upload) > 1:
                        part_main_path = main_path.parent / video_file.name
                        if shorts_path.exists() and video_file != shorts_path:
                            import shutil
                            shutil.copy2(video_file, part_main_path)
                    else:
                        part_main_path = main_path
                    
                    # Build title without part numbers
                    title, description, meta = self._build_upload_metadata(video_file, metadata)
                    
                    should_upload, privacy, reason = self._get_upload_decision(meta)
                    if not should_upload:
                        self._skip_upload(video_file, reason)
                    else:
                        if reason:
                            print(f"-> Upload policy match ({reason}). Uploading as {privacy}.")
                        uploaded = self.youtube_uploader.upload_video(video_file, title, description, privacy=privacy)
                        if uploaded:
                            self._cleanup_uploaded_video(video_file)
            
            return filename
            
        except subprocess.TimeoutExpired:
            print(f"⚠ Download timeout for URL: {url}")
            return None
        except Exception as e:
            print(f"✗ Error downloading from URL: {e}")
            return None
    
    def get_tiktok_videos(self):
        """Fetch latest videos from TikTok user using yt-dlp"""
        try:
            # Check if we should only download latest
            download_latest_only = self.config['download_settings'].get('download_latest_only', True)
            max_videos = self.config['download_settings'].get('max_videos_per_check', 1)
            
            if download_latest_only:
                print(f"→ Fetching latest {max_videos} video(s) from @{self.username}...")
            else:
                print(f"→ Fetching videos from @{self.username} (please wait, this can take up to 3 minutes)...")
            
            # Use yt-dlp to get video list
            url = f"https://www.tiktok.com/@{self.username}"
            
            # Limit playlist items based on settings
            playlist_end = max_videos if download_latest_only else 10
            
            cmd = ['yt-dlp']
            cmd.extend(self._ytdlp_cookies_args())
            cmd.extend([
                '--flat-playlist',
                '--print', 'id',
                '--print', 'title',
                '--playlist-end', str(playlist_end),
                '--no-warnings',
                '--quiet',
                '--socket-timeout', '30',
                '--retries', '3',
                url
            ])
            
            result = run_command(cmd, timeout=180)
            
            # Debug: check both stdout and stderr
            if result.stderr:
                stderr_preview = result.stderr[:200].strip()
                if stderr_preview and 'WARNING' not in stderr_preview:
                    print(f"  → yt-dlp stderr: {stderr_preview}")
            
            if not result.stdout or not result.stdout.strip():
                print(f"  → yt-dlp returned empty output")
                print(f"  → This usually means TikTok is blocking or rate-limiting")
                return []
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if 'Unable to download' in error_msg or 'not found' in error_msg.lower():
                    print(f"⚠ User @{self.username} not found or account is private")
                elif 'HTTP Error 403' in error_msg or 'Forbidden' in error_msg:
                    print(f"⚠ TikTok is blocking requests. This is common.")
                    print(f"→ The script will keep trying every {self.check_interval//60} minutes")
                else:
                    print(f"⚠ Error: {error_msg[:200]}")
                return []
            
            # Parse output
            lines = result.stdout.strip().split('\n')
            videos = []
            
            # Debug: print raw output
            if lines and lines[0]:
                print(f"  → Raw output lines: {len(lines)}")
            
            for i in range(0, len(lines), 2):
                if i + 1 < len(lines):
                    video_id = lines[i].strip()
                    title = lines[i + 1].strip()
                    
                    if video_id and video_id != '':
                        videos.append({
                            'video_id': video_id,
                            'title': title if title else 'untitled'
                        })
                        print(f"  → Found video: {video_id[:20]}... - {title[:30]}...")
            
            if videos:
                if download_latest_only:
                    print(f"✓ Found latest video")
                else:
                    print(f"✓ Found {len(videos)} videos")
            else:
                print(f"⚠ No videos found for @{self.username}")
                print(f"→ Possible reasons:")
                print(f"   - Account doesn't exist or is private")
                print(f"   - TikTok is temporarily blocking requests")
                print(f"   - Network connectivity issues")
            
            return videos
                
        except FileNotFoundError:
            print(f"✗ yt-dlp not installed!")
            print(f"→ Installing yt-dlp...")
            self._install_ytdlp()
            return []
        except subprocess.TimeoutExpired:
            print(f"⚠ Request timeout after 3 minutes.")
            print(f"→ This usually means TikTok is blocking or network is very slow")
            print(f"→ The script will automatically retry in {self.check_interval//60} minutes")
            print(f"→ TIP: Try using a VPN if this keeps happening")
            return []
        except Exception as e:
            print(f"✗ Error fetching videos: {e}")
            return []
    
    def _install_ytdlp(self):
        """Install yt-dlp"""
        try:
            print("→ Installing yt-dlp (this may take a minute)...")
            run_command([sys.executable, '-m', 'pip', 'install', 'yt-dlp'], timeout=300)
            print("✓ yt-dlp installed successfully!")
            print("→ Please run the script again")
        except Exception as e:
            print(f"✗ Failed to install yt-dlp: {e}")
            print("→ Please install manually: pip install yt-dlp")
    
    def _get_videos_alternative(self):
        """Alternative method - not needed with yt-dlp"""
        return []
    
    def download_video(self, video_info):
        """Download a single TikTok video using yt-dlp"""
        try:
            video_id = video_info.get('video_id')
            if not video_id or video_id in self.downloaded_ids:
                return None
            
            print(f"→ Downloading video {video_id}...")
            
            video_url = f"https://www.tiktok.com/@{self.username}/video/{video_id}"
            
            metadata = {}
            if self.config['youtube_settings'].get('skip_non_original_audio', False):
                metadata = self._fetch_tiktok_metadata(video_url)
            
            title_for_filename = metadata.get('title') or video_info.get('title', 'untitled')
            
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            title = title_for_filename[:50]
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_title:
                safe_title = "video"
            filename = f"{timestamp}_{safe_title}_{video_id}.mp4"
            
            # Organize by date if enabled
            if self.config['youtube_settings'].get('organize_by_date', False):
                date_folder = datetime.now().strftime('%Y-%m-%d')
                shorts_path = self.shorts_folder / date_folder / filename
                main_path = self.main_folder / date_folder / filename
                
                # Create date folders
                (self.shorts_folder / date_folder).mkdir(parents=True, exist_ok=True)
                (self.main_folder / date_folder).mkdir(parents=True, exist_ok=True)
            else:
                shorts_path = self.shorts_folder / filename
                main_path = self.main_folder / filename
            
            # Download using yt-dlp
            
            cmd = ['yt-dlp']
            cmd.extend(self._ytdlp_cookies_args())
            cmd.extend([
                '-o', str(shorts_path),
                '--no-playlist',
                '--quiet',
                '--no-warnings',
                video_url
            ])
            
            result = run_command(cmd, timeout=180)
            
            if result.returncode != 0:
                print(f"✗ Failed to download video {video_id}")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}")
                return None
            
            # Copy to main folder
            if shorts_path.exists():
                import shutil
                shutil.copy2(shorts_path, main_path)
            else:
                print(f"✗ Video file not found after download")
                return None
            
            # Save video info if enabled
            if self.config['download_settings']['save_video_info']:
                info_filename = f"{timestamp}_{safe_title}_{video_id}_info.txt"
                
                if self.config['youtube_settings'].get('organize_by_date', False):
                    info_path = self.shorts_folder / date_folder / info_filename
                else:
                    info_path = self.shorts_folder / info_filename
                
                title_for_info = metadata.get('title') or video_info.get('title', 'N/A')
                hashtags = metadata.get('hashtags') or self._extract_hashtags(title_for_info)
                
                with open(info_path, 'w', encoding='utf-8') as f:
                    f.write(f"TikTok Video Information\n")
                    f.write(f"========================\n\n")
                    f.write(f"Video ID: {video_id}\n")
                    f.write(f"Title: {title_for_info}\n")
                    if hashtags:
                        f.write(f"Hashtags: {' '.join(hashtags)}\n")
                    if metadata.get('track'):
                        f.write(f"Audio: {metadata.get('track')}\n")
                    if metadata.get('artist'):
                        f.write(f"Artist: {metadata.get('artist')}\n")
                    f.write(f"Author: @{self.username}\n")
                    f.write(f"Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Original URL: {video_url}\n")
                    if self.channel_name:
                        f.write(f"\nYouTube Channel: {self.channel_name}\n")
                    if self.channel_id:
                        f.write(f"YouTube Channel ID: {self.channel_id}\n")
            
            # Track this video
            self.downloaded_ids.append(video_id)
            self._save_tracking()
            
            print(f"✓ Downloaded: {filename}")
            print(f"  → Saved to: {shorts_path.parent}")
            
            # Process video (watermark, female detection, split)
            if self.video_processor:
                should_skip, processed_files = self.video_processor.process_video(shorts_path)
                
                if should_skip:
                    # Skip this video (e.g., female detected)
                    self._safe_delete(shorts_path)
                    self._safe_delete(main_path)
                    return None
                
                # Use processed files for upload
                video_files_to_upload = processed_files
            else:
                video_files_to_upload = [shorts_path]
            
            # Upload to YouTube if enabled
            if self.youtube_uploader.enabled:
                if 'title' not in metadata and video_info.get('title'):
                    metadata['title'] = video_info.get('title')
                
                for idx, video_file in enumerate(video_files_to_upload):
                    # Update main_path for each part
                    if len(video_files_to_upload) > 1:
                        part_main_path = main_path.parent / video_file.name
                        if shorts_path.exists() and video_file != shorts_path:
                            import shutil
                            shutil.copy2(video_file, part_main_path)
                    else:
                        part_main_path = main_path
                    
                    # Build title without part numbers
                    title, description, meta = self._build_upload_metadata(video_file, metadata)
                    
                    should_upload, privacy, reason = self._get_upload_decision(meta)
                    if not should_upload:
                        self._skip_upload(video_file, reason)
                    else:
                        if reason:
                            print(f"-> Upload policy match ({reason}). Uploading as {privacy}.")
                        uploaded = self.youtube_uploader.upload_video(video_file, title, description, privacy=privacy)
                        if uploaded:
                            self._cleanup_uploaded_video(video_file)
            
            return filename
            
        except subprocess.TimeoutExpired:
            print(f"⚠ Download timeout for video {video_id} (video may be too large)")
            return None
        except Exception as e:
            print(f"✗ Error downloading video: {e}")
            return None
    
    def monitor(self):
        """Continuously monitor TikTok account for new videos"""
        print(f"\n{'='*60}")
        print(f"TikTok to YouTube Video Downloader")
        print(f"{'='*60}")
        print(f"Monitoring: @{self.username}")
        print(f"Check interval: {self.check_interval} seconds ({self.check_interval//60} minutes)")
        if self.channel_name:
            print(f"YouTube Channel: {self.channel_name}")
        if self.channel_id:
            print(f"Channel ID: {self.channel_id}")
        print(f"YouTube Shorts folder: {self.shorts_folder.absolute()}")
        print(f"YouTube Main folder: {self.main_folder.absolute()}")
        print(f"Watermark removal: {'Enabled' if self.config['download_settings']['remove_watermark'] else 'Disabled'}")
        print(f"Save video info: {'Enabled' if self.config['download_settings']['save_video_info'] else 'Disabled'}")
        print(f"Organize by date: {'Enabled' if self.config['youtube_settings'].get('organize_by_date', False) else 'Disabled'}")
        print(f"Auto-restart: {'Enabled' if self.config.get('auto_restart', {}).get('enabled', True) else 'Disabled'}")
        print(f"\nTIP: Add video URLs to 'video_urls.txt' for manual downloads")
        print(f"{'='*60}\n")
        
        retry_count = 0
        max_retries = self.config.get('auto_restart', {}).get('max_retries', 999999)
        
        while retry_count < max_retries:
            try:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new videos...")
                
                # Upload old videos first (if any), then delete them after upload
                self.upload_pending_videos()
                
                # First, check for manual URLs
                manual_urls = self.check_manual_urls()
                if manual_urls:
                    print(f"✓ Found {len(manual_urls)} manual URL(s) in video_urls.txt")
                    for url in manual_urls:
                        self.download_from_url(url)
                
                # Then try automatic fetching
                videos = self.get_tiktok_videos()
                
                if videos:
                    new_count = 0
                    download_latest_only = self.config['download_settings'].get('download_latest_only', True)
                    max_videos = self.config['download_settings'].get('max_videos_per_check', 1)
                    
                    if download_latest_only:
                        # Download up to the latest N videos (and skip ones already downloaded)
                        for video in videos[:max_videos]:
                            result = self.download_video(video)
                            if result:
                                new_count += 1
                    else:
                        # Download all videos
                        for video in videos:
                            result = self.download_video(video)
                            if result:
                                new_count += 1
                    
                    if new_count > 0:
                        print(f"✓ Downloaded {new_count} new video(s)")
                    else:
                        print("→ No new videos found (already downloaded)")
                else:
                    if not manual_urls:
                        print("→ No videos retrieved")
                        print("TIP: Add URLs manually to video_urls.txt to bypass blocking")
                
                print(f"→ Next check in {self.check_interval} seconds ({self.check_interval//60} minutes)...\n")
                time.sleep(self.check_interval)
                
                # Reset retry count on successful check
                retry_count = 0
                
            except KeyboardInterrupt:
                print("\n\n⚠ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"✗ Error in monitoring loop: {e}")
                
                if self.config.get('auto_restart', {}).get('restart_on_error', True):
                    retry_count += 1
                    print(f"→ Auto-restart enabled. Retry {retry_count}/{max_retries}")
                    print(f"→ Retrying in {self.check_interval} seconds...\n")
                    time.sleep(self.check_interval)
                else:
                    print("→ Auto-restart disabled. Exiting...")
                    break

if __name__ == "__main__":
    print("DEBUG: Reached main entry point")
    sys.stdout.flush()
    
    print("\n" + "="*60)
    print("TikTok to YouTube - Starting...")
    print("="*60 + "\n")
    
    print("DEBUG: Loading configuration...")
    sys.stdout.flush()
    
    # Load configuration
    config = load_config()
    
    print("DEBUG: Configuration loaded")
    sys.stdout.flush()
    
    if not config:
        print("✗ Failed to load configuration. Exiting...")
        exit(1)
    
    # Check if username is set
    if config['tiktok_username'] == "username" or not config['tiktok_username']:
        print("⚠ WARNING: TikTok username not configured!")
        print("\nPlease edit 'config.json' and set the 'tiktok_username' field")
        print("Example: \"tiktok_username\": \"khaby.lame\"\n")
        
        if IS_NON_INTERACTIVE:
            print("-> This environment cannot answer interactive prompts.")
            print("-> Set TIKTOK_USERNAME in Railway variables or update config.json before deploying.")
            exit(1)
        
        response = input("Do you want to enter the username now? (y/n): ")
        if response.lower() == 'y':
            username = input("Enter TikTok username (without @): ").strip().replace('@', '')
            if username:
                config['tiktok_username'] = username
                # Save to config file
                with open(BASE_DIR / 'config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                print(f"✓ Configuration saved with username: @{username}\n")
            else:
                print("✗ No username provided. Exiting...")
                exit(1)
        else:
            exit(1)
    
    # Display configuration
    print("="*60)
    print("CONFIGURATION")
    print("="*60)
    print(f"TikTok Username: @{config['tiktok_username']}")
    print(f"Check Interval: {config['check_interval_minutes']} minutes")
    if config['youtube_settings'].get('channel_name'):
        print(f"YouTube Channel: {config['youtube_settings']['channel_name']}")
    if config['youtube_settings'].get('channel_id'):
        print(f"Channel ID: {config['youtube_settings']['channel_id']}")
    print(f"Shorts Folder: {config['youtube_settings']['shorts_folder']}")
    print(f"Main Videos Folder: {config['youtube_settings']['main_videos_folder']}")
    print(f"Remove Watermark: {config['download_settings']['remove_watermark']}")
    print(f"Save Video Info: {config['download_settings']['save_video_info']}")
    print(f"Organize by Date: {config['youtube_settings'].get('organize_by_date', False)}")
    print(f"Auto-restart: {config.get('auto_restart', {}).get('enabled', True)}")
    print("="*60 + "\n")
    
    # Start monitoring
    try:
        monitor = TikTokToYouTube(config)
        monitor.monitor()
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        print("Please check your configuration and try again.")
        exit(1)
