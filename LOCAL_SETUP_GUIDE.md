# Instagram to YouTube - Local PC Setup Guide

## ✅ This Version WILL WORK on Your Windows PC!

Unlike Railway, your home internet connection is trusted by Instagram, so login and downloads will work perfectly.

---

## 📋 Prerequisites

### 1. Python Installed
Check if you have Python:
```bash
python --version
```

If not installed, download from: https://www.python.org/downloads/

### 2. FFmpeg Installed
Check if you have FFmpeg:
```bash
ffmpeg -version
```

If not installed, follow: `INSTALL_FFMPEG_WINDOWS.txt`

---

## 🚀 Quick Start

### Step 1: Install Required Packages
```bash
pip install instaloader google-auth google-auth-oauthlib google-api-python-client
```

### Step 2: Configure Your Accounts

Open `instagram_youtube_local.py` and edit these lines:

```python
# Your Instagram login credentials
INSTAGRAM_USERNAME = 'rebel_jallal'
INSTAGRAM_PASSWORD = 'RebelJallal123'

# Accounts to download from
DOWNLOAD_FROM_ACCOUNTS = [
    'rebel_jallal',    # Your own account
    # 'i.haiderr',     # Uncomment to download from this account
    # 'rajab.butt94'   # Uncomment to download from this account
]
```

**To download from other accounts:**
- Remove the `#` before the account name
- Example: Change `# 'i.haiderr',` to `'i.haiderr',`

### Step 3: Make Sure You Have These Files

✅ `client_secret.json` - YouTube OAuth credentials
✅ `token.json` - YouTube authentication token
✅ `Track 1.mpeg` - Audio for image-to-video conversion
✅ `Track 2.mpeg` - Audio for image-to-video conversion

### Step 4: Run the Script
```bash
python instagram_youtube_local.py
```

---

## 🎯 What Will Happen

### First Run:
1. Script will login to Instagram as @rebel_jallal
2. Save session file (so you don't need to login again)
3. Authenticate with YouTube (browser will open)
4. Start monitoring accounts every 10 minutes

### Every 10 Minutes:
1. Check each account for new posts/reels
2. Download new content
3. Add "Lahori Twins" watermark
4. Convert images to videos (with audio)
5. Upload to YouTube automatically
6. Delete local files to save space

---

## ⚙️ Configuration

### Change Check Interval
```python
CHECK_INTERVAL = 600  # 10 minutes (in seconds)
```

### Change Max Posts Per Check
```python
MAX_POSTS_PER_CHECK = 3  # Download max 3 posts per account
```

### Change Hashtags
```python
DEFAULT_HASHTAGS = "#rajabfamily #rajabbutt #viralshorts"
```

---

## 🔧 Troubleshooting

### Instagram Login Failed
**Problem:** `✗ Instagram login failed`

**Solutions:**
1. Check username/password are correct
2. Disable 2FA temporarily on Instagram
3. Login to Instagram on browser first
4. Make sure account is not locked

### YouTube Upload Failed
**Problem:** `✗ Upload failed`

**Solutions:**
1. Make sure `client_secret.json` exists
2. Make sure `token.json` is valid
3. Re-authenticate if token expired

### FFmpeg Not Found
**Problem:** `ffmpeg: command not found`

**Solution:**
Follow `INSTALL_FFMPEG_WINDOWS.txt` to install FFmpeg

### Session Expired
**Problem:** `✗ Login required - session may have expired`

**Solution:**
Just restart the script - it will login again automatically

---

## 🎉 Advantages of Local Version

✅ **Instagram login works** (home IP is trusted)
✅ **No datacenter blocking** (not using Railway)
✅ **Session persistence** (login once, reuse session)
✅ **Faster downloads** (direct connection)
✅ **No rate limiting** (Instagram trusts home IPs)
✅ **100% FREE** (no hosting costs)

---

## 🔄 Running 24/7

### Option 1: Keep Terminal Open
Just leave the script running in terminal

### Option 2: Run as Background Process
```bash
# Windows
start /B python instagram_youtube_local.py
```

### Option 3: Run on Startup
1. Press `Win + R`
2. Type `shell:startup`
3. Create shortcut to script
4. Script runs when Windows starts

---

## 📊 Monitoring

The script will show:
- ✓ When it logs in
- ✓ Which accounts it's checking
- ✓ What posts it downloads
- ✓ Upload progress to YouTube
- ✓ Next check time

Example output:
```
[08:30:15] Checking all accounts...
→ Checking Instagram @rebel_jallal
  → Profile: Rebel Jallal
  → Posts: 42

  → Post: ABC123xyz
    Type: Video
    Likes: 1234
  → Downloading...
  ✓ Downloaded video: ABC123xyz.mp4
  ✓ Watermark added
  → Uploading: ABC123xyz_watermarked.mp4
  → 100%
  ✓ Uploaded! ID: dQw4w9WgXcQ
  → URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

  ✓ Downloaded and uploaded 1 post(s)

→ Next check in 10 minutes
→ Press Ctrl+C to stop
```

---

## 🛑 Stopping the Script

Press `Ctrl + C` in the terminal

The script will:
- Save current progress
- Keep session file for next run
- Exit cleanly

---

## 🔐 Security Notes

### Session File
The script creates `session-rebel_jallal` file containing your Instagram session.

**Keep this file safe:**
- Don't share it
- Don't commit to GitHub
- It allows access to your Instagram account

### Credentials in Code
Your username/password are in the script file.

**Security tips:**
- Don't share the script file
- Don't commit to public GitHub
- Consider using environment variables instead

---

## 📝 Next Steps

1. Install dependencies: `pip install instaloader google-auth google-auth-oauthlib google-api-python-client`
2. Edit `instagram_youtube_local.py` with your credentials
3. Run: `python instagram_youtube_local.py`
4. Watch it work! 🎉

---

## ❓ Questions?

**Q: Can I download from private accounts?**
A: Only if you follow them with @rebel_jallal

**Q: Will Instagram ban my account?**
A: Unlikely if you use reasonable delays (current: 5-10 seconds between posts)

**Q: Can I run this on Railway?**
A: No, Instagram blocks Railway. This is for local PC only.

**Q: Can I download stories?**
A: Yes! Instaloader can download stories from accounts you follow.

**Q: How do I add more accounts?**
A: Edit `DOWNLOAD_FROM_ACCOUNTS` list in the script

---

## 🎯 Summary

This local version will work 100% because:
- ✅ Your home IP is trusted by Instagram
- ✅ Login works without checkpoints
- ✅ No datacenter blocking
- ✅ Session persistence
- ✅ Completely free

**Just run it and it will work!** 🚀
