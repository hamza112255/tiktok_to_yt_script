# Instagram & Snapchat to YouTube Downloader

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup YouTube authentication (one-time)
# Place client_secret.json in this folder

# 3. Run the script
python insta_snap_youtube.py
```

Or double-click: `run_instagram_snapchat.bat`

## ✨ Features

- ✅ Downloads from Instagram & Snapchat automatically
- ✅ Converts images to videos with music (Track 1 & 2)
- ✅ Adds "Lahori Twins" watermark (small, centered)
- ✅ Detects and skips videos with females (AI-powered)
- ✅ Detects and skips copyrighted content
- ✅ Uploads to YouTube automatically
- ✅ Deletes files after upload (saves storage)
- ✅ Runs every 10 minutes
- ✅ Optimized for minimal storage usage

## 📱 Monitored Accounts

### Instagram
- **@i.haiderr** - Posts, Reels, Stories
- **@rajab.butt94** - Posts, Reels, Stories

### Snapchat
- **@i-haiderr** - Snaps, Stories, Spotlights
- **@rajab.butt7** - Snaps, Stories, Spotlights

## 🎵 Audio Tracks

The script uses these audio files for image-to-video conversion:
- `Track 1.mpeg` ✓
- `Track 2.mpeg` ✓

Randomly selects one track when converting images.

## ⚙️ Configuration

Edit `config.json` or `config.defaults.json`:

```json
{
  "youtube_settings": {
    "add_watermark": true,
    "watermark_text": "Lahori Twins",
    "skip_female_videos": true,
    "split_long_videos": true,
    "split_duration_seconds": 38
  }
}
```

## 📋 Requirements

### Software
- Python 3.8+
- FFmpeg (for video processing)
- yt-dlp (for downloading)

### Python Packages
```
yt-dlp
google-api-python-client
google-auth-oauthlib
opencv-python
numpy
pillow
deepface
tf-keras
```

Install all: `pip install -r requirements.txt`

## 🔧 Setup

### 1. Install FFmpeg
See `INSTALL_FFMPEG_WINDOWS.txt` for instructions.

### 2. YouTube Authentication
1. Get `client_secret.json` from Google Cloud Console
2. Follow guide in `GET_CLIENT_SECRET_GUIDE.md`
3. Place `client_secret.json` in this folder
4. Run script once to authenticate

### 3. Verify Audio Tracks
Make sure these files exist:
- `Track 1.mpeg`
- `Track 2.mpeg`

## 🎯 How It Works

### 1. Content Discovery (Every 10 minutes)
- Checks Instagram posts, reels, stories
- Checks Snapchat snaps, stories, spotlights

### 2. Download
- Uses `yt-dlp` to download latest content
- Max file size: 100MB
- Downloads only 1 item per check (saves bandwidth)

### 3. Image Conversion
If content is an image:
- Randomly selects Track 1 or Track 2
- Creates video with image + audio
- Duration: matches audio (max 60 seconds)
- Format: 1080x1920 (YouTube Shorts)

### 4. Content Filtering

#### Copyright Detection
Skips content with keywords:
- "copyright", "©", "(c)"
- "all rights reserved"
- "copyrighted"

#### Female Detection (AI)
- Uses DeepFace AI model
- Samples frames every 3 seconds
- Skips if female detected in >30% of frames

### 5. Video Processing
- Adds watermark (small, centered, semi-transparent)
- Splits videos >38 seconds into multiple parts
- Each part uploaded separately

### 6. YouTube Upload
- **Title**: Caption (first 80 chars) + #Shorts
- **Description**: Caption + default hashtags
- **Privacy**: Public
- **Category**: Entertainment

### 7. Cleanup
- Deletes all files after upload
- Keeps tracking file (prevents re-downloads)

## 📊 Default Hashtags

```
#rajabfamily #rajabbutt #viralshorts #maandogar #shezi #haidershah #haiderlive #jahangir
```

## 🔍 Tracking System

The script maintains `processed.json`:
- Tracks processed content by URL hash
- Prevents re-downloading same content
- Keeps last 1000 entries (auto-cleanup)

## 💾 Storage Optimization

The script is optimized for minimal storage:
1. Downloads to `temp_downloads/` folder
2. Processes immediately
3. Uploads to YouTube
4. Deletes all files
5. Only keeps small tracking file

Typical storage usage: <100MB

## 🐛 Troubleshooting

### "yt-dlp not installed"
```bash
pip install yt-dlp
```

### "ffmpeg not installed"
- Follow `INSTALL_FFMPEG_WINDOWS.txt`
- Add FFmpeg to PATH

### "YouTube API not available"
```bash
pip install google-api-python-client google-auth-oauthlib
```

### "DeepFace not installed"
```bash
pip install deepface tf-keras
```

### "No audio tracks"
- Verify `Track 1.mpeg` and `Track 2.mpeg` exist
- Place them in the same folder as the script

### Download Fails
- Instagram/Snapchat may block automated downloads
- Try using a VPN
- Script will retry every 10 minutes

### Upload Fails
- Check `token.json` is valid
- Run `refresh_youtube_token.py`
- Check YouTube API quota (10,000 units/day)

## 📈 YouTube API Quota

- Daily limit: 10,000 units
- Each upload: ~1,600 units
- Max uploads/day: ~6 videos

## 🔄 Running 24/7

### Option 1: Keep Terminal Open
```bash
python insta_snap_youtube.py
```
Keep window open. Script runs every 10 minutes.

### Option 2: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start program
5. Program: `python`
6. Arguments: `insta_snap_youtube.py`
7. Start in: Script folder path

### Option 3: Deploy to Cloud (Railway)
- See `RAILWAY_DEPLOYMENT.md`
- Runs 24/7 in the cloud
- No need to keep computer on

## 📝 Example Output

```
[10:30:00] Checking...

→ Checking instagram @i.haiderr
✓ Downloaded: 20240115_103005_i.haiderr.mp4
→ Processing video: 20240115_103005_i.haiderr.mp4
✓ No female detected (checked 8 frames)
→ Adding watermark: Lahori Twins
✓ Watermark added
→ Uploading: 20240115_103005_i.haiderr.mp4
  → 100%
✓ Uploaded! ID: abc123xyz

→ Checking snapchat @rajab.butt7
✓ Downloaded: 20240115_103010_rajab.butt7.jpg
→ Converting image to video
✓ Converted to video
→ Uploading: 20240115_103010_rajab.butt7.mp4
  → 100%
✓ Uploaded! ID: xyz789abc

→ Next check in 10 minutes
```

## ⚠️ Important Notes

1. **Respect Terms of Service**: Use responsibly. Instagram, Snapchat, and YouTube have terms of service.

2. **Copyright**: The script tries to detect copyright, but it's not 100% accurate. Review uploads regularly.

3. **Female Detection**: Requires DeepFace and TensorFlow. If not installed, this feature is disabled.

4. **Storage**: Script deletes files after upload, but ensure you have at least 1GB free space.

5. **API Quota**: YouTube limits uploads to ~6 per day. Plan accordingly.

## 📚 Additional Documentation

- `INSTAGRAM_SNAPCHAT_SETUP.md` - Detailed setup guide
- `QUICK_START_INSTAGRAM_SNAPCHAT.txt` - Quick reference
- `GET_CLIENT_SECRET_GUIDE.md` - YouTube authentication
- `INSTALL_FFMPEG_WINDOWS.txt` - FFmpeg installation

## 🆘 Support

If you encounter issues:
1. Check troubleshooting section above
2. Review log output for errors
3. Verify all prerequisites are installed
4. Check internet connection
5. Verify YouTube authentication

## 📄 License

For personal use only. Respect platform Terms of Service.

---

**YouTube Channel**: https://www.youtube.com/@LahoriTwins
