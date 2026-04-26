# Troubleshooting Guide

## Quick Diagnostics

Run this first to check your setup:
```bash
python test_setup.py
```

This will verify all dependencies and files are properly configured.

---

## Common Issues

### 1. "yt-dlp not installed" or "yt-dlp: command not found"

**Solution:**
```bash
pip install yt-dlp
```

**Verify installation:**
```bash
yt-dlp --version
```

---

### 2. "ffmpeg not installed" or "ffmpeg: command not found"

**Solution:**
1. Follow instructions in `INSTALL_FFMPEG_WINDOWS.txt`
2. Download FFmpeg from: https://ffmpeg.org/download.html
3. Add FFmpeg to your PATH environment variable

**Verify installation:**
```bash
ffmpeg -version
ffprobe -version
```

---

### 3. "YouTube API libraries not installed"

**Solution:**
```bash
pip install google-api-python-client google-auth-oauthlib
```

---

### 4. "client_secret.json not found"

**Solution:**
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download as `client_secret.json`
6. Place in the same folder as the script

**Detailed guide:** See `GET_CLIENT_SECRET_GUIDE.md`

---

### 5. "YouTube authentication failed"

**Possible causes:**
- Invalid or expired token
- Wrong client_secret.json
- Network issues

**Solutions:**

**Option 1: Refresh token**
```bash
python refresh_youtube_token.py
```

**Option 2: Delete and re-authenticate**
```bash
# Delete old token
del token.json

# Run script again (will prompt for authentication)
python insta_snap_youtube.py
```

**Option 3: Check client_secret.json**
- Make sure it's for "Desktop app" (not "Web app")
- Re-download from Google Cloud Console if needed

---

### 6. "DeepFace not installed" (Female detection)

**Solution:**
```bash
pip install deepface tf-keras
```

**Note:** This is optional. If not installed, female detection is disabled but script still works.

---

### 7. "No audio tracks found"

**Solution:**
Make sure these files exist in the same folder as the script:
- `Track 1.mpeg`
- `Track 2.mpeg`

**Check:**
```bash
dir "Track*.mpeg"
```

If missing, you need to add audio files for image-to-video conversion.

---

### 8. "Download failed" or "No new content found"

**Possible causes:**
- Instagram/Snapchat blocking automated downloads
- Account is private
- No new content available
- Network issues

**Solutions:**

**Option 1: Use VPN**
- Instagram/Snapchat may block certain IPs
- Try connecting through a VPN

**Option 2: Check account URLs**
- Verify accounts are public
- Test URLs in browser

**Option 3: Wait and retry**
- Script automatically retries every 10 minutes
- Temporary blocks usually resolve themselves

---

### 9. "Upload failed" or "Quota exceeded"

**Possible causes:**
- YouTube API quota exceeded (10,000 units/day)
- Network issues
- Invalid video format

**Solutions:**

**Check quota:**
- Go to: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
- Each upload costs ~1,600 units
- Max ~6 uploads per day

**Wait for quota reset:**
- Quota resets at midnight Pacific Time
- Script will continue trying

**Check video:**
- Make sure video is valid MP4
- Check file size (<100MB)

---

### 10. "Copyright detected" - Too many skips

**Possible causes:**
- Captions contain copyright keywords
- False positives

**Solutions:**

**Option 1: Adjust keywords**
Edit `insta_snap_youtube.py`:
```python
keywords = ['copyright', '©', '(c)', 'all rights reserved', 'copyrighted']
```

Remove keywords that cause false positives.

**Option 2: Disable copyright check**
Comment out the check in `insta_snap_youtube.py`:
```python
# if self._check_copyright(caption):
#     print(f"✗ Skipped: Copyright detected")
#     self._cleanup(file_path)
#     continue
```

---

### 11. "Female detected" - Too many skips

**Possible causes:**
- DeepFace detecting females in videos
- False positives

**Solutions:**

**Option 1: Adjust sensitivity**
Edit `video_processor.py`:
```python
# Change threshold from 0.3 to 0.5 (less sensitive)
detection_rate = female_detections / frames_checked
has_female = detection_rate > 0.5  # was 0.3
```

**Option 2: Disable female detection**
Edit `config.json`:
```json
{
  "youtube_settings": {
    "skip_female_videos": false
  }
}
```

**Option 3: Uninstall DeepFace**
```bash
pip uninstall deepface tf-keras
```
Script will continue without female detection.

---

### 12. "Memory error" or "Out of memory"

**Possible causes:**
- Large video files
- Multiple videos processing simultaneously
- Insufficient RAM

**Solutions:**

**Option 1: Reduce max file size**
Edit `insta_snap_youtube.py`:
```python
'--max-filesize', '50M',  # was 100M
```

**Option 2: Close other programs**
- Free up RAM
- Close browser tabs
- Close other applications

**Option 3: Increase virtual memory**
- Windows: System Properties → Advanced → Performance Settings → Advanced → Virtual Memory

---

### 13. "Script stops after a while"

**Possible causes:**
- Network timeout
- Unhandled exception
- System sleep

**Solutions:**

**Option 1: Check logs**
- Look for error messages before it stopped
- Address specific error

**Option 2: Prevent system sleep**
- Windows: Power Options → Never sleep
- Or use: `powercfg /change standby-timeout-ac 0`

**Option 3: Use Task Scheduler**
- Set up Windows Task Scheduler to restart script if it stops
- See README_INSTA_SNAP.md for instructions

---

### 14. "Watermark not showing" or "Watermark error"

**Possible causes:**
- FFmpeg font issue
- Invalid watermark text

**Solutions:**

**Option 1: Check FFmpeg fonts**
Edit `video_processor.py`:
```python
# Change font path
font_file = "C\\:/Windows/Fonts/arial.ttf"
```

**Option 2: Disable watermark**
Edit `config.json`:
```json
{
  "youtube_settings": {
    "add_watermark": false
  }
}
```

---

### 15. "Video splitting not working"

**Possible causes:**
- FFmpeg issue
- Invalid duration settings

**Solutions:**

**Option 1: Check FFmpeg**
```bash
ffmpeg -version
```

**Option 2: Adjust split duration**
Edit `config.json`:
```python
{
  "youtube_settings": {
    "split_duration_seconds": 30  # was 38
  }
}
```

**Option 3: Disable splitting**
Edit `config.json`:
```json
{
  "youtube_settings": {
    "split_long_videos": false
  }
}
```

---

### 16. "Image conversion failed"

**Possible causes:**
- FFmpeg issue
- Missing audio tracks
- Invalid image format

**Solutions:**

**Option 1: Check audio tracks**
```bash
dir "Track*.mpeg"
```

**Option 2: Test FFmpeg**
```bash
ffmpeg -i "Track 1.mpeg"
```

**Option 3: Check image format**
- Supported: JPG, JPEG, PNG
- Convert unsupported formats

---

### 17. "Tracking file corrupted"

**Symptoms:**
- Script crashes on startup
- "JSON decode error"

**Solution:**
```bash
# Delete tracking file (will be recreated)
del processed.json

# Run script again
python insta_snap_youtube.py
```

**Note:** This will reset tracking, so some content may be re-downloaded.

---

### 18. "Permission denied" errors

**Possible causes:**
- File in use by another program
- Insufficient permissions

**Solutions:**

**Option 1: Close other programs**
- Close video players
- Close file explorers

**Option 2: Run as administrator**
- Right-click script
- "Run as administrator"

**Option 3: Check antivirus**
- Antivirus may be blocking file operations
- Add script folder to exclusions

---

## Advanced Troubleshooting

### Enable Debug Mode

Edit `insta_snap_youtube.py`:
```python
# Add at the top
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Network Connectivity

```bash
# Test Instagram
ping instagram.com

# Test Snapchat
ping snapchat.com

# Test YouTube
ping youtube.com
```

### Check Disk Space

```bash
# Windows
dir

# Check free space
wmic logicaldisk get size,freespace,caption
```

### Monitor Resource Usage

- Open Task Manager (Ctrl+Shift+Esc)
- Check CPU, Memory, Disk usage
- Look for bottlenecks

---

## Getting Help

If you're still having issues:

1. **Run diagnostics:**
   ```bash
   python test_setup.py
   ```

2. **Check logs:**
   - Look for error messages in console output
   - Note the exact error message

3. **Verify setup:**
   - All dependencies installed?
   - All files present?
   - Configuration correct?

4. **Test components individually:**
   - Test yt-dlp: `yt-dlp --version`
   - Test FFmpeg: `ffmpeg -version`
   - Test Python packages: `python -c "import cv2; print('OK')"`

5. **Review documentation:**
   - `README_INSTA_SNAP.md`
   - `INSTAGRAM_SNAPCHAT_SETUP.md`
   - `QUICK_START_INSTAGRAM_SNAPCHAT.txt`

---

## Prevention Tips

1. **Keep dependencies updated:**
   ```bash
   pip install --upgrade yt-dlp
   pip install --upgrade google-api-python-client
   ```

2. **Monitor disk space:**
   - Keep at least 1GB free
   - Script auto-deletes files, but ensure space available

3. **Check YouTube quota:**
   - Monitor daily usage
   - Plan uploads accordingly

4. **Regular maintenance:**
   - Clear temp_downloads folder if needed
   - Check processed.json size (should be <1MB)

5. **Backup configuration:**
   - Keep backup of client_secret.json
   - Keep backup of token.json
   - Keep backup of config.json

---

## Emergency Reset

If everything is broken and you want to start fresh:

```bash
# 1. Delete all generated files
del token.json
del processed.json
rmdir /s /q temp_downloads

# 2. Reinstall dependencies
pip uninstall -y yt-dlp google-api-python-client google-auth-oauthlib opencv-python numpy pillow deepface tf-keras
pip install -r requirements.txt

# 3. Re-authenticate
python insta_snap_youtube.py
```

**Note:** This will reset everything. You'll need to re-authenticate with YouTube.

---

## Contact & Support

For additional help:
- Review all documentation files
- Check error messages carefully
- Test each component individually
- Ensure all prerequisites are met

---

**Last Updated:** January 2024
