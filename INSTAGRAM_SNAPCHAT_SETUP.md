# Instagram & Snapchat to YouTube Downloader - Setup Guide

## Overview
This script automatically downloads content from Instagram and Snapchat accounts and uploads them to your YouTube channel (@LahoriTwins).

## Features
✅ Downloads from Instagram (posts, reels, stories)
✅ Downloads from Snapchat (snaps, stories, spotlights)
✅ Converts images to MP4 with audio tracks
✅ Adds "Lahori Twins" watermark (small, centered)
✅ Detects and skips videos with females
✅ Detects and skips copyrighted content
✅ Automatically uploads to YouTube
✅ Deletes videos after processing (saves storage)
✅ Runs every 10 minutes automatically

## Accounts Being Monitored

### Instagram
- **@i.haiderr** - Posts, Reels, Stories
- **@rajab.butt94** - Posts, Reels, Stories

### Snapchat
- **@i-haiderr** - Snaps, Stories, Spotlights
- **@rajab.butt7** - Snaps, Stories, Spotlights

## Prerequisites

### 1. Install Python
- Download Python 3.8+ from https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### 2. Install FFmpeg
- Follow instructions in `INSTALL_FFMPEG_WINDOWS.txt`
- FFmpeg is required for video processing and image-to-video conversion

### 3. Install Required Python Packages
```bash
pip install -r requirements.txt
```

### 4. Setup YouTube Authentication
- Follow the guide in `GET_CLIENT_SECRET_GUIDE.md`
- You need `client_secret.json` from Google Cloud Console
- Run the script once to authenticate and generate `token.json`

## Audio Tracks for Images
The script uses these audio files to convert images to videos:
- `Track 1.mpeg` - Already in your repo
- `Track 2.mpeg` - Already in your repo

The script randomly selects one of these tracks when converting images.

## Configuration

### Edit `config.json` (or use `config.defaults.json`)

```json
{
  "youtube_settings": {
    "auto_upload_to_youtube": true,
    "video_privacy": "public",
    "default_description": "#rajabfamily #rajabbutt #viralshorts #maandogar #shezi #haidershah #haiderlive #jahangir",
    "add_watermark": true,
    "watermark_text": "Lahori Twins",
    "skip_female_videos": true,
    "split_long_videos": true,
    "split_duration_seconds": 38
  }
}
```

### Key Settings:
- **auto_upload_to_youtube**: Set to `true` to enable automatic uploads
- **video_privacy**: `"public"`, `"private"`, or `"unlisted"`
- **add_watermark**: Set to `true` to add watermark
- **watermark_text**: Text to display (small, centered)
- **skip_female_videos**: Set to `true` to skip videos with females
- **split_long_videos**: Set to `true` to split videos longer than 38 seconds

## How to Run

### Option 1: Using Batch File (Recommended)
```bash
run_instagram_snapchat.bat
```

### Option 2: Using Python Directly
```bash
python instagram_snapchat_to_youtube.py
```

## How It Works

### 1. Content Discovery
Every 10 minutes, the script checks:
- Instagram posts, reels, and stories
- Snapchat snaps, stories, and spotlights

### 2. Download
- Uses `yt-dlp` to download content
- Supports both videos and images

### 3. Image to Video Conversion
If content is an image:
- Randomly selects Track 1 or Track 2
- Creates a video with the image and audio
- Duration matches the audio track (max 60 seconds)
- Formatted for YouTube Shorts (1080x1920)

### 4. Content Filtering

#### Copyright Detection
Skips content with these keywords:
- "copyright"
- "©" or "(c)"
- "all rights reserved"
- "copyrighted"
- "protected content"

#### Female Detection
- Uses DeepFace AI to detect females in videos
- Samples frames every 3 seconds
- Skips if female detected in >30% of frames

### 5. Video Processing
- Adds "Lahori Twins" watermark (small, centered, semi-transparent)
- Splits videos longer than 38 seconds into multiple parts
- Each part is uploaded separately

### 6. YouTube Upload
- Title: Uses caption from Instagram/Snapchat (or default)
- Description: Includes caption + default hashtags
- Tags: Automatically adds #Shorts
- Privacy: Public (configurable)

### 7. Cleanup
- Deletes all downloaded files after processing
- Keeps tracking file to avoid re-downloading

## Title and Description Logic

### If Caption is Available:
- **Title**: First 80 characters of caption + #Shorts
- **Description**: Full caption + default hashtags

### If No Caption:
- **Title**: "{username} {content_type} #Shorts"
- **Description**: Default hashtags only

### Default Hashtags:
```
#rajabfamily #rajabbutt #viralshorts #maandogar #shezi #haidershah #haiderlive #jahangir
```

## Tracking System
The script maintains `downloaded_content.json` to track processed content:
- Prevents re-downloading the same content
- Stores unique IDs for each piece of content
- Format: `{platform}_{username}_{type}_{timestamp}`

## Troubleshooting

### "yt-dlp not installed"
```bash
pip install yt-dlp
```

### "ffmpeg not installed"
- Follow `INSTALL_FFMPEG_WINDOWS.txt`
- Make sure FFmpeg is in your PATH

### "YouTube API libraries not installed"
```bash
pip install google-api-python-client google-auth-oauthlib
```

### "DeepFace not installed" (for female detection)
```bash
pip install deepface tf-keras
```

### "No audio tracks found"
- Make sure `Track 1.mpeg` and `Track 2.mpeg` are in the same folder as the script

### Instagram/Snapchat Download Fails
- These platforms may block automated downloads
- Try using a VPN
- The script will keep retrying every 10 minutes

### YouTube Upload Fails
- Check your `token.json` is valid
- Run `refresh_youtube_token.py` to refresh authentication
- Check your YouTube API quota (10,000 units/day)

## Storage Optimization

The script is optimized for minimal storage usage:
1. Downloads to temporary folder
2. Processes video immediately
3. Uploads to YouTube
4. Deletes all files after upload
5. Only keeps small tracking file

## Running 24/7

### Option 1: Keep Terminal Open
- Run `run_instagram_snapchat.bat`
- Keep the window open
- Script runs every 10 minutes automatically

### Option 2: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
5. Program: `python`
6. Arguments: `instagram_snapchat_to_youtube.py`
7. Start in: Your script folder path

### Option 3: Deploy to Railway (Cloud)
- Follow `RAILWAY_DEPLOYMENT.md`
- Script runs 24/7 in the cloud
- No need to keep your computer on

## Monitoring

The script prints detailed logs:
- ✓ Success messages (green checkmark)
- → Info messages (arrow)
- ⚠ Warning messages (warning symbol)
- ✗ Error messages (X symbol)

Example output:
```
[2024-01-15 10:30:00] Checking for new content...

→ Checking Instagram post for @i.haiderr...
✓ Downloaded: 20240115_103005_i.haiderr_post.mp4
→ Processing video: 20240115_103005_i.haiderr_post.mp4
✓ No female detected (checked 8 frames)
→ Adding watermark: Lahori Twins
✓ Watermark added
→ Uploading to YouTube: 20240115_103005_i.haiderr_post.mp4
  → Upload progress: 100%
✓ Uploaded to YouTube!
  → Video ID: abc123xyz
  → URL: https://www.youtube.com/watch?v=abc123xyz
  → Privacy: public
  → Deleted: 20240115_103005_i.haiderr_post.mp4

→ Next check in 600 seconds (10 minutes)...
```

## Important Notes

1. **YouTube API Quota**: You have 10,000 units/day. Each upload costs ~1,600 units. That's ~6 uploads/day.

2. **Female Detection**: Requires `deepface` and `tf-keras`. If not installed, this feature is disabled.

3. **Copyright**: The script tries to detect copyright keywords, but it's not 100% accurate. Review uploads regularly.

4. **Platform Limitations**: Instagram and Snapchat may block automated downloads. Use responsibly.

5. **Storage**: The script deletes files after processing, but make sure you have at least 1GB free space for temporary files.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the log output for error messages
3. Make sure all prerequisites are installed
4. Check your internet connection
5. Verify YouTube authentication is working

## License
This script is for personal use only. Respect Instagram, Snapchat, and YouTube's Terms of Service.
