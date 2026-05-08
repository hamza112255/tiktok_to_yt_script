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
from datetime import datetime
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

INSTAGRAM_ACCOUNTS = [
    "i.haiderr",
    "rajab.butt94",
    "sardar_maan_dogar_",
    "nadeemmubarakofficial",
    "shazi.ssb",
    "choudary_hasham.100",
    "jahangir67310",
    "musatariq_12",
    "abdullahkhanhere",
]

SNAPCHAT_ACCOUNTS = [
    "rajab.butt7",
    "i-haiderr",
    "maandogar12",
    "i_shazi10",
    "m_k1k25",
    "nadeemmubarak",
    "jahangir.butt",
]

# Specific story / spotlight URLs
SNAPCHAT_STORY_URLS = [
    "https://www.snapchat.com/@rajab.butt7/--r0KL06Tf6TEY_HSO2L5QAAgbGVlY2NvaWVwAZ3safxmAZ3saXqgAAAAAA",
    "https://www.snapchat.com/@i-haiderr/bxDWFxIIStOqaQBg6BmYnAAAgdXBmc2ZhempvAZ3p1pUhAZ3p1ltlAAAAAA",
    "https://www.snapchat.com/@maandogar12/qtB2_PAyRd69OUyc93IMXQAAgbGJrd3hjaXlrAZ3tyKjOAZ3tyJ5EAAAAAA",
    "https://www.snapchat.com/@i_shazi10/WtyCGS-4R7y4gvBdTXqj1gAAgeHZtbW5zbG1vAZ3tyO9KAZ3txwpVAAAAAA",
    "https://www.snapchat.com/@m_k1k25/YunQmyv4QJKM_Jrk06cjxAAAgdGN0dm11cHBlAZ3p0S1CAZ3p0SwmAAAAAA",
    "https://www.snapchat.com/@nadeemmubarak/pdlTYa8PQ4yhyP6mR4iAXQAAgc3BtaGFlZGF4AZ3tLyEPAZ3tLxdMAAAAAA",
]

TIKTOK_ACCOUNTS = [
    "rajabsfamily2",
    "buttisback0.07",
    "nadeemmubarakofficial",
    "i.haiderr",
    "maandogardogarisback",
    "musakhann1003",
    "raajabbutt1",
    "man.dogar6",
    "haider.shah1400",
    "jahangirbutt914",
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
    except Exception:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _hash(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[:10]


def _rm(path) -> None:
    try:
        if path:
            Path(path).unlink(missing_ok=True)
    except Exception:
        pass


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

    def __init__(self):
        self.yt = None
        self.enabled = False
        if YOUTUBE_AVAILABLE:
            self._auth()

    def _auth(self):
        try:
            token_file  = BASE_DIR / "token.json"
            secret_file = BASE_DIR / "client_secret.json"

            # Accept token JSON blob from env var (headless / Railway)
            token_env = os.getenv("YOUTUBE_TOKEN_JSON")
            if token_env and not token_file.exists():
                token_file.write_text(token_env, encoding="utf-8")

            # Accept base64-encoded client secret from env var
            if not secret_file.exists():
                secret_b64 = os.getenv("YOUTUBE_CLIENT_SECRET_B64")
                if secret_b64:
                    secret_file.write_bytes(base64.b64decode(secret_b64))
                else:
                    print("⚠ client_secret.json not found — YouTube upload disabled")
                    return

            creds = None
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(
                    str(token_file), self.SCOPES
                )

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    token_file.write_text(creds.to_json(), encoding="utf-8")
                elif IS_RAILWAY:
                    print("⚠ YouTube token invalid on Railway — upload disabled")
                    return
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(secret_file), self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    token_file.write_text(creds.to_json(), encoding="utf-8")

            self.yt = build("youtube", "v3", credentials=creds)
            self.enabled = True
            print("✓ YouTube authenticated")
        except Exception as e:
            print(f"✗ YouTube auth failed: {e}")

    def upload(self, video_path: Path, title: str, description: str) -> bool:
        if not self.enabled:
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
            request = self.yt.videos().insert(
                part="snippet,status", body=body, media_body=media
            )
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"    {int(status.progress() * 100)}%")

            vid_id = response["id"]
            print(f"  ✓ Uploaded → https://youtube.com/watch?v={vid_id}")
            return True
        except Exception as e:
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
                    "ffmpeg", "-i", str(video_path),
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
        if not self._audio_tracks:
            print("  ⚠ No audio tracks found — cannot convert image to video")
            return None
        try:
            audio = random.choice(self._audio_tracks)
            out   = img.parent / f"{img.stem}_v.mp4"

            res = _run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "json", str(audio),
                ],
                timeout=15,
            )
            duration = 15.0
            try:
                duration = min(60.0, float(json.loads(res.stdout)["format"]["duration"]))
            except Exception:
                pass

            cmd = [
                "ffmpeg", "-loop", "1", "-i", str(img), "-i", str(audio),
                "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p",
                "-vf",
                "scale=1080:1920:force_original_aspect_ratio=decrease,"
                "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                "-c:a", "aac", "-b:a", "128k", "-shortest", "-y", str(out),
            ]
            res = _run(cmd, timeout=120)
            if res.returncode == 0 and out.exists():
                _rm(img)
                print(f"  ✓ Image → video: {out.name}")
                return out
            print(f"  ⚠ image_to_video failed: {res.stderr[-200:] if res.stderr else ''}")
        except Exception as e:
            print(f"  ⚠ image_to_video: {e}")
        return None

    def add_watermark(self, src: Path) -> Path:
        """Burn a small centred 'Lahori Twins' text into the video."""
        dst = src.parent / f"{src.stem}_wm.mp4"
        wm_filter = (
            f"drawtext={self._font_prefix}"
            f"text='{WATERMARK_TEXT}':"
            f"fontsize={WATERMARK_SIZE}:"
            f"fontcolor=white@0.55:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"shadowcolor=black@0.4:shadowx=1:shadowy=1"
        )
        cmd = [
            "ffmpeg", "-i", str(src),
            "-vf", wm_filter,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy", "-y", str(dst),
        ]
        res = _run(cmd, timeout=300)
        if res.returncode == 0 and dst.exists() and dst.stat().st_size > 1024:
            _rm(src)
            print(f"  ✓ Watermark added")
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
        self, url: str, prefix: str, n: int = MAX_VIDEOS_PER_ACCOUNT
    ) -> list:
        """
        Download up to n newest items from `url` using yt-dlp.
        Returns [(Path, info_dict), ...].
        """
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        safe = prefix[:18].replace("/", "_").replace(".", "_")
        tmpl = str(TEMP_DIR / f"{ts}_{safe}_%(id)s.%(ext)s")

        cmd = [
            "yt-dlp",
            "-o", tmpl,
            "--playlist-end", str(n),
            "--max-filesize", MAX_FILE_SIZE,
            "--no-warnings", "--quiet",
            "--write-info-json",
            "--merge-output-format", "mp4",
        ]
        if self._cookies.exists():
            cmd += ["--cookies", str(self._cookies)]
        cmd.append(url)

        _run(cmd, timeout=300)  # errors handled by checking output files

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
            # Posts
            print(f"  @{user} [posts]")
            for media, info in self.dl.fetch(
                f"https://www.instagram.com/{user}/", f"igp_{user[:12]}"
            ):
                self._handle(media, info, "instagram", user)

            # Reels
            print(f"  @{user} [reels]")
            for media, info in self.dl.fetch(
                f"https://www.instagram.com/{user}/reels/", f"igr_{user[:12]}"
            ):
                self._handle(media, info, "instagram", user)

            # Stories (requires instagram_cookies.txt — silently skipped otherwise)
            print(f"  @{user} [stories]")
            for media, info in self.dl.fetch(
                f"https://www.instagram.com/stories/{user}/",
                f"igs_{user[:12]}",
                n=5,
            ):
                self._handle(media, info, "instagram", user)

    def _run_snapchat(self) -> None:
        print("\n── Snapchat ──────────────────────────────")
        for user in SNAPCHAT_ACCOUNTS:
            print(f"  @{user} [profile]")
            for media, info in self.dl.fetch(
                f"https://www.snapchat.com/@{user}", f"sc_{user[:12]}"
            ):
                self._handle(media, info, "snapchat", user)

        for story_url in SNAPCHAT_STORY_URLS:
            user = story_url.split("@")[1].split("/")[0]
            h    = _hash(story_url)
            print(f"  @{user} [story/{h}]")
            for media, info in self.dl.fetch(story_url, f"scs_{h}"):
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
