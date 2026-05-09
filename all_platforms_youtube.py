#!/usr/bin/env python3
"""
All Platforms → YouTube Uploader
Instagram (posts/reels/stories) + Snapchat + TikTok → @LahoriTwins
Runs every 10 minutes automatically.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ── Stream setup (Railway / Docker compatibility) ────────────────────────
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp_all"
TEMP_DIR.mkdir(exist_ok=True)

IS_RAILWAY = any(
    os.getenv(k)
    for k in [
        "RAILWAY_PROJECT_ID",
        "RAILWAY_SERVICE_ID",
        "RAILWAY_ENVIRONMENT_ID",
        "RAILWAY_DEPLOYMENT_ID",
    ]
)

# ════════════════════════════════════════════════════════════════════════════
#  ACCOUNT LISTS
# ════════════════════════════════════════════════════════════════════════════

# DISABLED - Instagram accounts (uncomment to enable)
# INSTAGRAM_ACCOUNTS = [
#     "i.haiderr",
#     "rajab.butt94",
#     "sardar_maan_dogar_",
#     "nadeemmubarakofficial",
#     "shazi.ssb",
#     "choudary_hasham.100",
#     "jahangir67310",
#     "musatariq_12",
#     "abdullahkhanhere",
# ]
INSTAGRAM_ACCOUNTS = []

# DISABLED - Snapchat accounts (uncomment to enable)
# SNAPCHAT_ACCOUNTS = [
#     "rajab.butt7",
#     "i-haiderr",
#     "maandogar12",
#     "i_shazi10",
#     "m_k1k25",
#     "nadeemmubarak",
#     "jahangir.butt",
# ]
SNAPCHAT_ACCOUNTS = []

# DISABLED - Specific story / spotlight URLs (uncomment to enable)
# SNAPCHAT_STORY_URLS = [
#     "https://www.snapchat.com/@rajab.butt7/--r0KL06Tf6TEY_HSO2L5QAAgbGVlY2NvaWVwAZ3safxmAZ3saXqgAAAAAA",
#     "https://www.snapchat.com/@i-haiderr/bxDWFxIIStOqaQBg6BmYnAAAgdXBmc2ZhempvAZ3p1pUhAZ3p1ltlAAAAAA",
#     "https://www.snapchat.com/@maandogar12/qtB2_PAyRd69OUyc93IMXQAAgbGJrd3hjaXlrAZ3tyKjOAZ3tyJ5EAAAAAA",
#     "https://www.snapchat.com/@i_shazi10/WtyCGS-4R7y4gvBdTXqj1gAAgeHZtbW5zbG1vAZ3tyO9KAZ3txwpVAAAAAA",
#     "https://www.snapchat.com/@m_k1k25/YunQmyv4QJKM_Jrk06cjxAAAgdGN0dm11cHBlAZ3p0S1CAZ3p0SwmAAAAAA",
#     "https://www.snapchat.com/@nadeemmubarak/pdlTYa8PQ4yhyP6mR4iAXQAAgc3BtaGFlZGF4AZ3tLyEPAZ3tLxdMAAAAAA",
# ]
SNAPCHAT_STORY_URLS = []

# ENABLED - TikTok accounts (ACTIVE)
TIKTOK_ACCOUNTS = [
    "lahoritwins",
    "shahbazbukhari145",
    "rajab14family512",
    "buttisback.007",
    "rajabfamily_5567",
]

# ════════════════════════════════════════════════════════════════════════════
#  SETTINGS  (override any via environment variables)
# ════════════════════════════════════════════════════════════════════════════

DEFAULT_TAGS = (
    "#rajabfamily #rajabbutt #viralshorts #maandogar #shazi "
    "#haidershah #haiderlive #jahangir #fyp #foryou #trending"
)
WATERMARK_TEXT = "Lahori Twins"
WATERMARK_SIZE = 16  # px — intentionally small

CHECK_INTERVAL         = int(os.getenv("CHECK_INTERVAL", "600"))   # seconds
MAX_VIDEOS_PER_ACCOUNT = int(os.getenv("MAX_VIDEOS_PER_ACCOUNT", "3"))
MAX_FILE_SIZE          = os.getenv("MAX_FILE_SIZE", "100M")
AUDD_API_KEY           = os.getenv("AUDD_API_KEY", "")

# YouTube Data API v3 quota: 10,000 units/day; each upload costs 1,600 units → ~6 max.
# Keep at 5 by default to leave headroom for other API calls.
MAX_UPLOADS_PER_DAY = int(os.getenv("MAX_UPLOADS_PER_DAY", "5"))

# Only download/upload content published within the last N hours.
# Using hours (not days) so the bot only ever touches truly recent content —
# even after a Railway restart the tracking file is gone, but hour-precision
# means we only look back MAX_VIDEO_AGE_HOURS from *now*, so old videos stay ignored.
# Default: 24 hours. Set to 0 to disable.
MAX_VIDEO_AGE_HOURS = int(os.getenv("MAX_VIDEO_AGE_HOURS", "24"))

# Instagram credentials — get sessionid from browser cookies after logging in
INSTAGRAM_SESSION_ID = os.getenv("INSTAGRAM_SESSION_ID", "")
INSTAGRAM_USERNAME   = os.getenv("INSTAGRAM_USERNAME", "")

# Female detection defaults to OFF on Railway (no GPU / heavy deps)
ENABLE_FEMALE_DETECTION = (
    os.getenv("ENABLE_FEMALE_DETECTION", "false" if IS_RAILWAY else "true").lower()
    == "true"
)
ENABLE_COPYRIGHT_CHECK = os.getenv("ENABLE_COPYRIGHT_CHECK", "true").lower() == "true"

COPYRIGHT_KEYWORDS = [
    "copyright", "©", "(c)", "all rights reserved", "rights reserved",
    "dmca", "trademark", "™", "®", "licensed", "unauthorized", "proprietary",
]

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi"}

# ════════════════════════════════════════════════════════════════════════════
#  YouTube API imports
# ════════════════════════════════════════════════════════════════════════════

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("⚠ google-api-python-client not installed — YouTube upload disabled")

# ════════════════════════════════════════════════════════════════════════════
#  Tiny utilities
# ════════════════════════════════════════════════════════════════════════════


def _run(cmd: list, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        # Binary not installed — return a failed result so callers degrade gracefully
        return subprocess.CompletedProcess(
            cmd, returncode=127, stdout="", stderr=f"Command not found: {cmd[0]}"
        )
    except Exception:
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except Exception as e:
            return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr=str(e))


def _resolve_ffmpeg() -> str:
    """
    Return a path to a working ffmpeg binary.
    Priority:
      1. System ffmpeg in PATH
      2. imageio-ffmpeg pip package (ships its own pre-built binary — works on
         Railway/Docker without any apt/nix package installation needed)
    Returns empty string when nothing is found.
    """
    for candidate in ("ffmpeg", "/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        try:
            r = subprocess.run(
                [candidate, "-version"], capture_output=True, timeout=8
            )
            if r.returncode == 0:
                return candidate
        except Exception:
            pass

    try:
        import imageio_ffmpeg  # noqa: PLC0415
        path = imageio_ffmpeg.get_ffmpeg_exe()
        r    = subprocess.run([path, "-version"], capture_output=True, timeout=8)
        if r.returncode == 0:
            print(f"✓ ffmpeg: using imageio-ffmpeg bundled binary")
            return path
    except Exception:
        pass

    return ""


def _hash(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[:10]


def _rm(path) -> None:
    try:
        if path:
            Path(path).unlink(missing_ok=True)
    except Exception:
        pass


FFMPEG_PATH      = _resolve_ffmpeg()
FFMPEG_AVAILABLE = bool(FFMPEG_PATH)
print(
    f"{'✓' if FFMPEG_AVAILABLE else '⚠'} ffmpeg: "
    + ("available" if FFMPEG_AVAILABLE else "NOT FOUND — watermark + image conversion disabled")
)


def _setup_instagram_cookies() -> None:
    """
    Write instagram_cookies.txt from INSTAGRAM_SESSION_ID env var.
    Called once at startup so both yt-dlp and instaloader can use it.
    Instagram blocks datacenter IPs unless an authenticated session is provided.
    Get your sessionid: log into Instagram in Chrome → F12 → Application →
    Cookies → instagram.com → copy the 'sessionid' value.
    """
    cookies_file = BASE_DIR / "instagram_cookies.txt"
    if not INSTAGRAM_SESSION_ID:
        return
    if cookies_file.exists():
        return  # already written (e.g. mounted volume or previous run)
    content = (
        "# Netscape HTTP Cookie File\n"
        "# Generated from INSTAGRAM_SESSION_ID environment variable\n"
        f".instagram.com\tTRUE\t/\tTRUE\t2147483647\tsessionid\t{INSTAGRAM_SESSION_ID}\n"
    )
    cookies_file.write_text(content, encoding="utf-8")
    print("✓ instagram_cookies.txt written from INSTAGRAM_SESSION_ID")


_setup_instagram_cookies()


def _font_filter_prefix() -> str:
    """
    Return the fontfile= portion of an FFmpeg drawtext filter string.
    Returns empty string to let FFmpeg use its built-in font when no
    suitable font file is found on the current OS.
    """
    sys_name = platform.system()
    if sys_name == "Windows":
        candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
        ]
    elif sys_name == "Darwin":
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        ]

    for p in candidates:
        if os.path.exists(p):
            escaped = p.replace(":", "\\:")
            return f"fontfile='{escaped}':"
    return ""


# ════════════════════════════════════════════════════════════════════════════
#  YouTube Uploader
# ════════════════════════════════════════════════════════════════════════════


class YouTubeUploader:
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    _QUOTA_FILE = BASE_DIR / "yt_quota.json"

    def __init__(self):
        self.yt             = None
        self.enabled        = False
        self.quota_exceeded = False
        self._today_count   = self._load_quota_count()
        if self._today_count >= MAX_UPLOADS_PER_DAY:
            self.quota_exceeded = True
            print(f"⚠ YouTube daily limit already reached ({self._today_count}/{MAX_UPLOADS_PER_DAY}) — uploads paused until tomorrow")
        if YOUTUBE_AVAILABLE:
            self._auth()

    # ── Quota tracking ────────────────────────────────────────────────────

    def _load_quota_count(self) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            data = json.loads(self._QUOTA_FILE.read_text(encoding="utf-8"))
            if data.get("date") == today:
                return int(data.get("count", 0))
        except Exception:
            pass
        return 0

    def _save_quota_count(self) -> None:
        self._QUOTA_FILE.write_text(
            json.dumps({"date": datetime.now().strftime("%Y-%m-%d"), "count": self._today_count}),
            encoding="utf-8",
        )

    def _refresh_quota_if_new_day(self) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            data = json.loads(self._QUOTA_FILE.read_text(encoding="utf-8"))
            if data.get("date") != today:
                self._today_count   = 0
                self.quota_exceeded = False
                self._save_quota_count()
                print(f"  ✓ New day — YouTube upload quota reset (0/{MAX_UPLOADS_PER_DAY})")
        except Exception:
            pass

    def quota_status(self) -> str:
        return f"{self._today_count}/{MAX_UPLOADS_PER_DAY} uploads today"

    # ── Auth ──────────────────────────────────────────────────────────────

    def _get_rotation_project(self) -> int:
        """Get which project to use based on day of month (1-based)."""
        # For Railway: Check environment variables for multiple projects
        if IS_RAILWAY:
            available_projects = []
            for i in range(1, 100):
                if os.getenv(f"YOUTUBE_CLIENT_SECRET_{i}_B64") or os.getenv(f"YOUTUBE_TOKEN_{i}_JSON"):
                    available_projects.append(i)
                elif i > 10:
                    break
            
            if available_projects:
                day_of_month = datetime.now().day
                project_index = (day_of_month - 1) % len(available_projects)
                return available_projects[project_index]
        
        # For Local: Check file system for multiple projects
        else:
            available_projects = []
            for i in range(1, 100):
                if (BASE_DIR / f"client_secret_{i}.json").exists():
                    available_projects.append(i)
                elif i > 10:
                    break
            
            if available_projects:
                day_of_month = datetime.now().day
                project_index = (day_of_month - 1) % len(available_projects)
                return available_projects[project_index]
        
        return 0  # Fall back to default (no rotation)

    def _auth(self):
        try:
            # Determine which project to use
            project_num = self._get_rotation_project()
            
            if project_num > 0:
                # Use rotated credentials
                token_file  = BASE_DIR / f"token_{project_num}.json"
                secret_file = BASE_DIR / f"client_secret_{project_num}.json"
                print(f"🔄 Using Project {project_num} (Day {datetime.now().day} rotation)")
                
                # For Railway: Check environment variables with project number
                if IS_RAILWAY:
                    token_env = os.getenv(f"YOUTUBE_TOKEN_{project_num}_JSON")
                    if token_env and not token_file.exists():
                        token_file.write_text(token_env, encoding="utf-8")
                    
                    if not secret_file.exists():
                        secret_b64 = os.getenv(f"YOUTUBE_CLIENT_SECRET_{project_num}_B64")
                        if secret_b64:
                            secret_file.write_bytes(base64.b64decode(secret_b64))
            else:
                # Fall back to default credentials
                token_file  = BASE_DIR / "token.json"
                secret_file = BASE_DIR / "client_secret.json"
                
                # For Railway: Check default environment variables
                if IS_RAILWAY:
                    token_env = os.getenv("YOUTUBE_TOKEN_JSON")
                    if token_env and not token_file.exists():
                        token_file.write_text(token_env, encoding="utf-8")

            if not secret_file.exists():
                if not IS_RAILWAY or project_num == 0:
                    secret_b64 = os.getenv("YOUTUBE_CLIENT_SECRET_B64")
                    if secret_b64:
                        secret_file.write_bytes(base64.b64decode(secret_b64))
                    else:
                        if project_num > 0:
                            print(f"⚠ client_secret_{project_num}.json not found — YouTube upload disabled")
                        else:
                            print("⚠ client_secret.json not found — YouTube upload disabled")
                        return
                else:
                    if project_num > 0:
                        print(f"⚠ client_secret_{project_num}.json not found — YouTube upload disabled")
                    else:
                        print("⚠ client_secret.json not found — YouTube upload disabled")
                    return

            creds = None
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(str(token_file), self.SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    token_file.write_text(creds.to_json(), encoding="utf-8")
                elif IS_RAILWAY:
                    print("⚠ YouTube token invalid on Railway — upload disabled")
                    return
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(str(secret_file), self.SCOPES)
                    creds = flow.run_local_server(port=0)
                    token_file.write_text(creds.to_json(), encoding="utf-8")

            self.yt = build("youtube", "v3", credentials=creds)
            self.enabled = True
            print(f"✓ YouTube authenticated ({self.quota_status()})")
        except Exception as e:
            print(f"✗ YouTube auth failed: {e}")

    # ── Upload ────────────────────────────────────────────────────────────

    def upload(self, video_path: Path, title: str, description: str) -> bool:
        if not self.enabled:
            return False

        # Reset counter if it's a new calendar day
        self._refresh_quota_if_new_day()

        if self.quota_exceeded or self._today_count >= MAX_UPLOADS_PER_DAY:
            print(f"  ⏸ Daily limit ({MAX_UPLOADS_PER_DAY} uploads) reached — skipping until tomorrow")
            self.quota_exceeded = True
            return False

        try:
            print(f"  ↑ Uploading: {video_path.name}")
            clean_title = title.strip()[:90]
            if "#shorts" not in clean_title.lower():
                clean_title = f"{clean_title} #Shorts"

            body = {
                "snippet": {
                    "title":       clean_title[:100],
                    "description": description[:5000],
                    "tags":        ["shorts", "viral", "pakistan", "lahoritwins"],
                    "categoryId":  "24",  # Entertainment
                },
                "status": {
                    "privacyStatus":           "public",
                    "selfDeclaredMadeForKids": False,
                },
            }
            media   = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
            request = self.yt.videos().insert(part="snippet,status", body=body, media_body=media)

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"    {int(status.progress() * 100)}%")

            self._today_count += 1
            self._save_quota_count()
            vid_id = response["id"]
            print(f"  ✓ Uploaded [{self._today_count}/{MAX_UPLOADS_PER_DAY} today] → https://youtube.com/watch?v={vid_id}")
            return True

        except Exception as e:
            err = str(e)
            if "quotaExceeded" in err:
                print(f"  ⚠ YouTube API quota exhausted — uploads paused until midnight (Pacific)")
                self.quota_exceeded = True
                return False
            print(f"  ✗ Upload failed: {e}")
            return False


# ════════════════════════════════════════════════════════════════════════════
#  Copyright Checker
# ════════════════════════════════════════════════════════════════════════════


class CopyrightChecker:
    def check_text(self, text: str) -> bool:
        if not ENABLE_COPYRIGHT_CHECK or not text:
            return False
        tl = text.lower()
        for kw in COPYRIGHT_KEYWORDS:
            if kw in tl:
                print(f"  ⚠ Copyright keyword: '{kw}'")
                return True
        return False

    def check_audio(self, video_path: Path) -> bool:
        """Send a 10-second audio fingerprint to AudD API."""
        if not ENABLE_COPYRIGHT_CHECK or not AUDD_API_KEY:
            return False
        snippet = TEMP_DIR / f"_snip_{_hash(str(video_path))}.mp3"
        try:
            _run(
                [
                    FFMPEG_PATH, "-i", str(video_path),
                    "-t", "10", "-vn", "-ar", "44100",
                    "-ac", "1", "-b:a", "64k", "-y", str(snippet),
                ],
                timeout=30,
            )
            if not snippet.exists():
                return False

            import requests as _req

            with open(snippet, "rb") as fh:
                resp = _req.post(
                    "https://api.audd.io/",
                    data={
                        "api_token": AUDD_API_KEY,
                        "return":    "apple_music,spotify",
                    },
                    files={"file": fh},
                    timeout=20,
                )
            data = resp.json()
            if data.get("status") == "success" and data.get("result"):
                song = data["result"].get("title", "unknown")
                print(f"  ⚠ Copyrighted music detected: {song}")
                return True
        except Exception:
            pass
        finally:
            _rm(snippet)
        return False


# ════════════════════════════════════════════════════════════════════════════
#  Female Detector  (DeepFace, optional)
# ════════════════════════════════════════════════════════════════════════════


class FemaleDetector:
    def __init__(self):
        self._df    = None
        self._ready = None

    def _load(self) -> bool:
        if self._ready is None:
            try:
                from deepface import DeepFace  # noqa: PLC0415

                self._df    = DeepFace
                self._ready = True
                print("✓ DeepFace loaded for gender detection")
            except Exception as e:
                print(f"⚠ DeepFace not available ({e}) — female detection disabled")
                self._ready = False
        return self._ready

    def has_female(self, video_path: Path) -> bool:
        if not ENABLE_FEMALE_DETECTION or not self._load():
            return False
        try:
            import cv2  # noqa: PLC0415

            cap   = cv2.VideoCapture(str(video_path))
            fps   = max(1, int(cap.get(cv2.CAP_PROP_FPS)))
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            step  = fps * 3
            n     = min(8, max(1, total // step if step else 1))
            hits  = 0

            print(f"  → Checking {n} frames for female presence…")
            for i in range(n):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
                ok, frame = cap.read()
                if not ok:
                    break
                try:
                    result = self._df.analyze(
                        frame,
                        actions=["gender"],
                        enforce_detection=False,
                        silent=True,
                    )
                    faces = result if isinstance(result, list) else [result]
                    if any(
                        f.get("dominant_gender", "").lower() == "woman"
                        for f in faces
                    ):
                        hits += 1
                except Exception:
                    pass

            cap.release()
            rate = hits / n if n else 0
            if rate > 0.3:
                print(f"  ⚠ Female detected ({rate * 100:.0f}% of frames) — skipping")
                return True
            print(f"  ✓ No female detected ({n} frames checked)")
            return False
        except Exception as e:
            print(f"  ⚠ Gender check error: {e}")
            return False


# ════════════════════════════════════════════════════════════════════════════
#  Video Processor  (watermark + image → video)
# ════════════════════════════════════════════════════════════════════════════


class VideoProcessor:
    def __init__(self):
        self._font_prefix = _font_prefix = _font_filter_prefix()
        self._audio_tracks = [t for t in [
            BASE_DIR / "Track 1.mpeg",
            BASE_DIR / "Track 2.mpeg",
        ] if t.exists()]

    def image_to_video(self, img: Path) -> Optional[Path]:
        """Convert a static image to an MP4 with background music."""
        if not FFMPEG_AVAILABLE:
            print("  ⚠ ffmpeg not available — skipping image→video conversion")
            _rm(img)
            return None
        if not self._audio_tracks:
            print("  ⚠ No audio tracks found — cannot convert image to video")
            return None
        try:
            audio = random.choice(self._audio_tracks)
            out   = img.parent / f"{img.stem}_v.mp4"

            # Use system ffprobe if available; imageio-ffmpeg does NOT ship ffprobe.
            duration = 15.0
            for ffprobe_candidate in ("ffprobe", "/usr/bin/ffprobe", "/usr/local/bin/ffprobe"):
                res = _run(
                    [
                        ffprobe_candidate, "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "json", str(audio),
                    ],
                    timeout=15,
                )
                if res.returncode == 0:
                    try:
                        duration = min(60.0, float(json.loads(res.stdout)["format"]["duration"]))
                    except Exception:
                        pass
                    break

            cmd = [
                FFMPEG_PATH, "-loop", "1", "-i", str(img), "-i", str(audio),
                "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p",
                "-vf",
                "scale=1080:1920:force_original_aspect_ratio=decrease,"
                "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                "-c:a", "aac", "-b:a", "128k", "-shortest", "-y", str(out),
            ]
            res = _run(cmd, timeout=120)
            if res.returncode == 0 and out.exists() and out.stat().st_size > 1024:
                _rm(img)
                print(f"  ✓ Image → video: {out.name}")
                return out
            # Show first 800 chars of stderr — ffmpeg errors appear at the start,
            # progress lines appear at the end (those are useless for diagnosis).
            err_snippet = (res.stderr or "")[:800].strip()
            print(f"  ⚠ image_to_video failed (rc={res.returncode}): {err_snippet}")
        except Exception as e:
            print(f"  ⚠ image_to_video: {e}")
        return None

    def add_watermark(self, src: Path) -> Path:
        """Burn a small centred 'Lahori Twins' text into the video."""
        if not FFMPEG_AVAILABLE:
            return src   # upload as-is when ffmpeg is missing
        dst = src.parent / f"{src.stem}_wm.mp4"

        def _try_watermark(font_prefix: str) -> bool:
            wm_filter = (
                f"drawtext={font_prefix}"
                f"text='{WATERMARK_TEXT}':"
                f"fontsize={WATERMARK_SIZE}:"
                f"fontcolor=white@0.55:"
                f"x=(w-text_w)/2:y=(h-text_h)/2:"
                f"shadowcolor=black@0.4:shadowx=1:shadowy=1"
            )
            cmd = [
                FFMPEG_PATH, "-i", str(src),
                "-vf", wm_filter,
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "copy", "-y", str(dst),
            ]
            res = _run(cmd, timeout=300)
            if res.returncode == 0 and dst.exists() and dst.stat().st_size > 1024:
                return True
            err_snippet = (res.stderr or "")[:800].strip()
            print(f"  ⚠ Watermark attempt failed (rc={res.returncode}): {err_snippet}")
            if dst.exists():
                dst.unlink(missing_ok=True)
            return False

        # First attempt: use the system font file (if found).
        if _try_watermark(self._font_prefix):
            _rm(src)
            print("  ✓ Watermark added")
            return dst

        # Second attempt: no fontfile= — let ffmpeg use its built-in font.
        # imageio-ffmpeg static builds have drawtext but may not have the font path.
        if self._font_prefix and _try_watermark(""):
            _rm(src)
            print("  ✓ Watermark added (built-in font)")
            return dst

        print("  ⚠ Watermark failed — uploading original")
        return src


# ════════════════════════════════════════════════════════════════════════════
#  yt-dlp Downloader
# ════════════════════════════════════════════════════════════════════════════


class Downloader:
    def __init__(self):
        self._cookies = BASE_DIR / "instagram_cookies.txt"

    def fetch(
        self,
        url: str,
        prefix: str,
        n: int = MAX_VIDEOS_PER_ACCOUNT,
        extra_args: Optional[list] = None,
    ) -> list:
        """
        Download up to n newest items from `url` using yt-dlp.
        Returns [(Path, info_dict), ...].
        extra_args are appended to the yt-dlp command before the URL.
        """
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        safe = prefix[:18].replace("/", "_").replace(".", "_")
        tmpl = str(TEMP_DIR / f"{ts}_{safe}_%(id)s.%(ext)s")

        cmd = [
            "yt-dlp",
            "-o", tmpl,
            "--playlist-end", str(n),
            "--max-filesize", MAX_FILE_SIZE,
            "--no-warnings",
            "--write-info-json",
            "--merge-output-format", "mp4",
            "--ignore-errors",      # skip individual bad files without aborting the playlist
        ]
        if MAX_VIDEO_AGE_HOURS > 0:
            # yt-dlp --dateafter is day-precision only (YYYYMMDD).
            # We floor to the start of the cutoff day so we never miss a video
            # posted earlier today; the instaloader path uses hour-precision instead.
            cutoff_dt = datetime.now() - timedelta(hours=MAX_VIDEO_AGE_HOURS)
            cmd += ["--dateafter", cutoff_dt.strftime("%Y%m%d")]
        if FFMPEG_PATH:
            cmd += ["--ffmpeg-location", FFMPEG_PATH]
        if self._cookies.exists():
            cmd += ["--cookies", str(self._cookies)]
        if extra_args:
            cmd += extra_args
        cmd.append(url)

        res = _run(cmd, timeout=300)
        if res.returncode != 0:
            # Surface the last meaningful error line so we know why it failed
            err_lines = [l for l in (res.stderr or "").splitlines() if l.strip()]
            if err_lines:
                print(f"    yt-dlp warn: {err_lines[-1][:140]}")

        results = []
        for media in sorted(TEMP_DIR.glob(f"{ts}_{safe}_*")):
            if media.suffix == ".json":
                continue
            ext = media.suffix.lower()
            if ext not in VIDEO_EXTS | IMAGE_EXTS:
                _rm(media)
                continue

            info  = {}
            jfile = media.parent / f"{media.stem}.info.json"
            if jfile.exists():
                try:
                    info = json.loads(jfile.read_text(encoding="utf-8"))
                except Exception:
                    pass
                _rm(jfile)

            results.append((media, info))

        return results

    def fetch_instaloader(
        self, username: str, n: int = MAX_VIDEOS_PER_ACCOUNT
    ) -> list:
        """
        Download latest Instagram posts/reels via instaloader.
        Works for public profiles without any login credentials.
        Falls back silently when instaloader is not installed.
        """
        try:
            import instaloader as il
        except ImportError:
            print("  ⚠ instaloader not installed — pip install instaloader")
            return []

        ts       = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        work_dir = TEMP_DIR / f"il_{username[:12]}_{ts[-8:]}"
        work_dir.mkdir(exist_ok=True)
        captions: dict = {}

        try:
            L = il.Instaloader(
                dirname_pattern=str(work_dir),
                filename_pattern=f"{ts}_{{shortcode}}",
                download_videos=True,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                post_metadata_txt_pattern="",
                compress_json=False,
                max_connection_attempts=2,
                quiet=True,
            )

            # Authenticate with sessionid cookie when available.
            # Instagram blocks unauthenticated requests from datacenter IPs (Railway).
            # Get your sessionid: log into Instagram in Chrome → F12 → Application
            # → Cookies → instagram.com → copy 'sessionid' → set INSTAGRAM_SESSION_ID.
            if INSTAGRAM_SESSION_ID:
                L.context._session.cookies.set(
                    "sessionid", INSTAGRAM_SESSION_ID, domain=".instagram.com"
                )
                if INSTAGRAM_USERNAME:
                    L.context.username = INSTAGRAM_USERNAME

            cutoff_dt = (
                datetime.utcnow() - timedelta(hours=MAX_VIDEO_AGE_HOURS)
                if MAX_VIDEO_AGE_HOURS > 0 else None
            )
            profile = il.Profile.from_username(L.context, username)
            count   = 0
            for post in profile.get_posts():
                if count >= n:
                    break
                # instaloader gives hour-precision dates — stop as soon as we
                # hit a post older than MAX_VIDEO_AGE_HOURS (posts come newest-first).
                if cutoff_dt is not None:
                    try:
                        post_dt = post.date_utc.replace(tzinfo=None)
                        if post_dt < cutoff_dt:
                            break
                    except Exception:
                        pass
                captions[post.shortcode] = post.caption or ""
                try:
                    L.download_post(post, target=work_dir)
                except Exception as e:
                    print(f"    ⚠ {e}")
                count += 1
        except Exception as e:
            print(f"  ⚠ instaloader @{username}: {e}")

        results = []
        for f in sorted(work_dir.rglob("*")):
            if f.is_dir():
                continue
            if f.suffix.lower() in {".txt", ".json", ".xz"}:
                _rm(f)
                continue
            if f.suffix.lower() not in VIDEO_EXTS | IMAGE_EXTS:
                _rm(f)
                continue
            # filename_pattern = "{ts}_{shortcode}.ext"
            sc      = f.stem.rsplit("_", 1)[-1] if "_" in f.stem else f.stem
            caption = captions.get(sc, "")
            results.append((f, {
                "id":          f.stem,
                "description": caption,
                "title":       caption[:100] if caption else "",
            }))

        return results


# ════════════════════════════════════════════════════════════════════════════
#  Main Bot
# ════════════════════════════════════════════════════════════════════════════


class AllPlatformsBot:
    def __init__(self):
        self._tracking_file = BASE_DIR / "processed_all.json"
        self._processed     = self._load_tracking()
        self.uploader  = YouTubeUploader()
        self.copyright = CopyrightChecker()
        self.female    = FemaleDetector()
        self.vp        = VideoProcessor()
        self.dl        = Downloader()

    # ── Tracking ──────────────────────────────────────────────────────────

    def _load_tracking(self) -> set:
        if self._tracking_file.exists():
            try:
                return set(
                    json.loads(self._tracking_file.read_text(encoding="utf-8"))
                )
            except Exception:
                pass
        return set()

    def _save_tracking(self) -> None:
        keep = list(self._processed)[-3000:]
        self._tracking_file.write_text(
            json.dumps(keep, indent=2), encoding="utf-8"
        )

    def _mark_done(self, key: str) -> None:
        self._processed.add(key)
        self._save_tracking()

    # ── Metadata helpers ──────────────────────────────────────────────────

    @staticmethod
    def _make_meta(info: dict) -> tuple:
        raw = (
            info.get("description") or
            info.get("title")       or
            info.get("fulltitle")   or
            ""
        ).strip()
        title = raw[:90] if raw else DEFAULT_TAGS[:90]
        desc  = raw       if raw else DEFAULT_TAGS
        if DEFAULT_TAGS not in desc:
            desc = f"{desc}\n\n{DEFAULT_TAGS}"
        return title, desc

    # ── Single-video pipeline ─────────────────────────────────────────────

    def _handle(
        self, media: Path, info: dict, platform: str, username: str
    ) -> None:
        vid_id = info.get("id") or _hash(media.name)
        key    = f"{platform}:{username}:{vid_id}"

        if key in self._processed:
            _rm(media)
            return

        # 1. Copyright check on caption / title
        meta_text = (info.get("description") or "") + " " + (info.get("title") or "")
        if self.copyright.check_text(meta_text):
            print(f"  ✗ Metadata copyright — skip: {media.name}")
            _rm(media)
            self._mark_done(key)
            return

        # 2. Convert image → video (add music)
        if media.suffix.lower() in IMAGE_EXTS:
            media = self.vp.image_to_video(media)
            if not media:
                return

        # 3. Audio copyright via AudD (only if API key set)
        if AUDD_API_KEY and self.copyright.check_audio(media):
            print(f"  ✗ Audio copyright — skip: {media.name}")
            _rm(media)
            self._mark_done(key)
            return

        # 4. Female detection
        if self.female.has_female(media):
            _rm(media)
            self._mark_done(key)
            return

        # 5. Add watermark
        media = self.vp.add_watermark(media)

        # 6. Upload to YouTube
        title, desc = self._make_meta(info)
        ok = self.uploader.upload(media, title, desc)

        # 7. Delete local file
        _rm(media)
        if ok:
            self._mark_done(key)

    # ── Per-platform runners ──────────────────────────────────────────────

    def _run_instagram(self) -> None:
        print("\n── Instagram ─────────────────────────────")
        for user in INSTAGRAM_ACCOUNTS:
            # Posts + Reels: instaloader works for public profiles without login.
            # yt-dlp requires cookies for Instagram profile browsing.
            print(f"  @{user} [posts/reels]")
            for media, info in self.dl.fetch_instaloader(user):
                self._handle(media, info, "instagram", user)

            # Stories: yt-dlp with instagram_cookies.txt (skip silently without them)
            print(f"  @{user} [stories]")
            for media, info in self.dl.fetch(
                f"https://www.instagram.com/stories/{user}/",
                f"igs_{user[:12]}",
                n=5,
            ):
                self._handle(media, info, "instagram", user)

    def _run_snapchat(self) -> None:
        print("\n── Snapchat ──────────────────────────────")
        # yt-dlp does NOT support generic Snapchat profile pages.
        # Only specific story/spotlight URLs (with the hash fragment) are tried.
        # --allow-unplayable-formats bypasses yt-dlp's unusual-extension safety check.
        snap_extra = ["--allow-unplayable-formats"]
        for story_url in SNAPCHAT_STORY_URLS:
            user = story_url.split("@")[1].split("/")[0]
            h    = _hash(story_url)
            print(f"  @{user} [story]")
            for media, info in self.dl.fetch(
                story_url, f"sc_{h}", extra_args=snap_extra
            ):
                self._handle(media, info, "snapchat", user)

    def _run_tiktok(self) -> None:
        print("\n── TikTok ────────────────────────────────")
        for user in TIKTOK_ACCOUNTS:
            print(f"  @{user}")
            for media, info in self.dl.fetch(
                f"https://www.tiktok.com/@{user}", f"tt_{user[:12]}"
            ):
                self._handle(media, info, "tiktok", user)

    # ── Cycle + main loop ─────────────────────────────────────────────────

    def _cleanup_temp(self) -> None:
        for f in TEMP_DIR.iterdir():
            if f.is_file():
                _rm(f)

    def cycle(self) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'═'*54}\n  Cycle: {ts}\n{'═'*54}")
        try:
            self._run_instagram()
            self._run_snapchat()
            self._run_tiktok()
        except Exception as e:
            print(f"✗ Cycle error: {e}")
        finally:
            self._cleanup_temp()

    def run(self) -> None:
        print("\n" + "═" * 54)
        print("  All Platforms → YouTube @LahoriTwins")
        print("═" * 54)
        print(f"  Instagram accounts : {len(INSTAGRAM_ACCOUNTS)}")
        print(f"  Snapchat accounts  : {len(SNAPCHAT_ACCOUNTS)} + {len(SNAPCHAT_STORY_URLS)} story URLs")
        print(f"  TikTok accounts    : {len(TIKTOK_ACCOUNTS)}")
        print(f"  Interval           : {CHECK_INTERVAL // 60} min")
        print(f"  Instagram session  : {'SET ✓' if INSTAGRAM_SESSION_ID else 'NOT SET ⚠ (IG blocked from Railway)'}")
        print(f"  Female detection   : {'ON' if ENABLE_FEMALE_DETECTION else 'OFF'}")
        print(f"  Copyright check    : {'ON' if ENABLE_COPYRIGHT_CHECK else 'OFF'}")
        print(f"  AudD fingerprint   : {'ON' if AUDD_API_KEY else 'OFF (keyword-only)'}")
        print(f"  YouTube upload     : {'ON' if self.uploader.enabled else 'OFF (no creds)'}")
        print("═" * 54)

        while True:
            self.cycle()
            print(f"\n  ⏱  Next check in {CHECK_INTERVAL // 60} min…")
            time.sleep(CHECK_INTERVAL)


# ════════════════════════════════════════════════════════════════════════════
#  Entry point
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    bot = AllPlatformsBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n  Stopped by user.")
