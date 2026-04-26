# 🚀 START HERE - Instagram & Snapchat to YouTube Downloader

## What This Does

Automatically downloads content from Instagram and Snapchat accounts and uploads to your YouTube channel (@LahoriTwins) every 10 minutes.

## ✨ Features

✅ Downloads from Instagram (posts, reels, stories)
✅ Downloads from Snapchat (snaps, stories, spotlights)  
✅ Converts images to videos with music
✅ Adds "Lahori Twins" watermark
✅ Skips videos with females (AI detection)
✅ Skips copyrighted content
✅ Uploads to YouTube automatically
✅ Deletes files after upload (saves storage)

## 📱 Monitored Accounts

**Instagram:**
- @i.haiderr
- @rajab.butt94

**Snapchat:**
- @i-haiderr
- @rajab.butt7

## 🎯 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Setup YouTube Authentication
1. Get `client_secret.json` from Google Cloud Console
2. See `GET_CLIENT_SECRET_GUIDE.md` for instructions
3. Place it in this folder

### Step 3: Run the Script
```bash
python insta_snap_youtube.py
```

Or double-click: `run_instagram_snapchat.bat`

## ✅ Verify Setup

Run this to check if everything is configured:
```bash
python test_setup.py
```

## 📚 Documentation

### Quick Reference
- **START_HERE.md** ← You are here
- **QUICK_START_INSTAGRAM_SNAPCHAT.txt** - Quick commands
- **README_INSTA_SNAP.md** - Full documentation

### Setup Guides
- **INSTAGRAM_SNAPCHAT_SETUP.md** - Detailed setup
- **GET_CLIENT_SECRET_GUIDE.md** - YouTube authentication
- **INSTALL_FFMPEG_WINDOWS.txt** - FFmpeg installation

### Troubleshooting
- **TROUBLESHOOTING.md** - Common issues & solutions
- **test_setup.py** - Verify your setup

### Technical
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **insta_snap_youtube.py** - Main script

## 🔧 Prerequisites

### Required Software
- Python 3.8+ ✓
- FFmpeg ✓
- yt-dlp ✓

### Required Files
- `Track 1.mpeg` ✓ (already in repo)
- `Track 2.mpeg` ✓ (already in repo)
- `client_secret.json` ⚠ (you need to get this)
- `config.json` or `config.defaults.json` ✓ (already in repo)

### Python Packages
All listed in `requirements.txt`:
- yt-dlp
- google-api-python-client
- google-auth-oauthlib
- opencv-python
- numpy
- pillow
- deepface (optional, for female detection)
- tf-keras (optional, for female detection)

## 🎵 Audio Tracks

The script uses these audio files to convert images to videos:
- `Track 1.mpeg` ✓
- `Track 2.mpeg` ✓

Both are already in your repo!

## ⚙️ Configuration

Edit `config.json` to customize:

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

## 🎯 How It Works

```
Every 10 minutes:
1. Check Instagram & Snapchat for new content
2. Download latest posts/reels/stories
3. Convert images to videos (with music)
4. Check for copyright keywords
5. Detect females (AI)
6. Add watermark
7. Split long videos
8. Upload to YouTube
9. Delete all files
```

## 📊 What Gets Uploaded

### Title
- Uses caption from Instagram/Snapchat
- Or: "{username} {platform} #Shorts"

### Description
- Full caption + default hashtags
- Default: `#rajabfamily #rajabbutt #viralshorts #maandogar #shezi #haidershah #haiderlive #jahangir`

### Settings
- Privacy: Public
- Category: Entertainment
- Format: YouTube Shorts (1080x1920)

## 🛡️ Safety Features

### Copyright Detection
Skips content with keywords:
- "copyright", "©", "(c)"
- "all rights reserved"

### Female Detection
- Uses DeepFace AI
- Samples video frames
- Skips if female detected

## 💾 Storage

The script is optimized for minimal storage:
- Downloads to temp folder
- Processes immediately
- Uploads to YouTube
- Deletes all files
- Typical usage: <100MB

## 🚨 Important Notes

1. **YouTube Quota**: Limited to ~6 uploads per day (10,000 API units)
2. **Platform Blocks**: Instagram/Snapchat may block downloads (use VPN if needed)
3. **Female Detection**: Optional feature (requires DeepFace)
4. **Copyright**: Keyword detection is not 100% accurate

## 🐛 Troubleshooting

### Quick Fixes

**"yt-dlp not installed"**
```bash
pip install yt-dlp
```

**"ffmpeg not installed"**
- See `INSTALL_FFMPEG_WINDOWS.txt`

**"YouTube authentication failed"**
```bash
python refresh_youtube_token.py
```

**"No audio tracks found"**
- Verify `Track 1.mpeg` and `Track 2.mpeg` exist

**More issues?**
- See `TROUBLESHOOTING.md` for detailed solutions

## 📈 Monitoring

The script prints detailed logs:
```
[10:30:00] Checking...

→ Checking instagram @i.haiderr
✓ Downloaded: 20240115_103005_i.haiderr.mp4
→ Processing video
✓ No female detected
→ Adding watermark: Lahori Twins
✓ Watermark added
→ Uploading: 20240115_103005_i.haiderr.mp4
  → 100%
✓ Uploaded! ID: abc123xyz

→ Next check in 10 minutes
```

## 🔄 Running 24/7

### Option 1: Keep Terminal Open
```bash
python insta_snap_youtube.py
```
Keep window open. Script runs automatically.

### Option 2: Windows Task Scheduler
1. Open Task Scheduler
2. Create task to run at startup
3. Program: `python`
4. Arguments: `insta_snap_youtube.py`

### Option 3: Deploy to Cloud
- See `RAILWAY_DEPLOYMENT.md`
- Runs 24/7 without your computer

## 📝 File Structure

```
your-repo/
├── insta_snap_youtube.py          ← Main script
├── video_processor.py             ← Video processing
├── run_instagram_snapchat.bat     ← Easy launcher
├── test_setup.py                  ← Verify setup
├── Track 1.mpeg                   ← Audio track 1
├── Track 2.mpeg                   ← Audio track 2
├── config.json                    ← Configuration
├── client_secret.json             ← YouTube OAuth (you need this)
├── token.json                     ← YouTube token (auto-generated)
├── processed.json                 ← Tracking file (auto-generated)
├── requirements.txt               ← Python packages
├── temp_downloads/                ← Temporary files (auto-created)
└── Documentation/
    ├── START_HERE.md              ← This file
    ├── README_INSTA_SNAP.md       ← Full docs
    ├── INSTAGRAM_SNAPCHAT_SETUP.md
    ├── QUICK_START_INSTAGRAM_SNAPCHAT.txt
    ├── TROUBLESHOOTING.md
    ├── IMPLEMENTATION_SUMMARY.md
    ├── GET_CLIENT_SECRET_GUIDE.md
    └── INSTALL_FFMPEG_WINDOWS.txt
```

## ✅ Pre-Flight Checklist

Before running:
- [ ] Python 3.8+ installed
- [ ] FFmpeg installed and in PATH
- [ ] All Python packages installed (`pip install -r requirements.txt`)
- [ ] `client_secret.json` present
- [ ] `Track 1.mpeg` present
- [ ] `Track 2.mpeg` present
- [ ] `config.json` or `config.defaults.json` present
- [ ] At least 1GB free disk space

## 🎉 Ready to Go?

1. **Verify setup:**
   ```bash
   python test_setup.py
   ```

2. **Run the script:**
   ```bash
   python insta_snap_youtube.py
   ```

3. **Monitor the output:**
   - Watch for successful downloads
   - Check YouTube channel for uploads
   - Review any error messages

## 🆘 Need Help?

1. Run `python test_setup.py` to diagnose issues
2. Check `TROUBLESHOOTING.md` for solutions
3. Review `README_INSTA_SNAP.md` for details
4. Verify all prerequisites are installed

## 🎯 Target Channel

**YouTube**: https://www.youtube.com/@LahoriTwins

All content uploads here automatically!

---

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Get `client_secret.json` (see `GET_CLIENT_SECRET_GUIDE.md`)
3. ✅ Run: `python insta_snap_youtube.py`
4. ✅ Monitor uploads on YouTube
5. ✅ Adjust settings in `config.json` as needed

---

**Happy Uploading! 🚀**

For detailed documentation, see `README_INSTA_SNAP.md`
