# Railway Deployment Guide - Instagram/Snapchat to YouTube

## 🚀 Quick Deploy to Railway

### Prerequisites
1. GitHub account with your code pushed
2. Railway account (https://railway.app)
3. YouTube OAuth credentials (`client_secret.json` and `token.json`)

---

## Step-by-Step Deployment

### Step 1: Prepare Credentials Locally

Before deploying, you need to generate `token.json` locally:

```bash
# Run the script once locally to authenticate
python insta_snap_youtube.py
```

This will open a browser for YouTube authentication and create `token.json`.

### Step 2: Encode Credentials to Base64

Railway doesn't support file uploads, so we encode credentials as environment variables:

**Windows (PowerShell):**
```powershell
# Encode client_secret.json
$content = Get-Content client_secret.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$encoded = [Convert]::ToBase64String($bytes)
$encoded | Out-File -FilePath client_secret_b64.txt -NoNewline

# Encode token.json
$content = Get-Content token.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$encoded = [Convert]::ToBase64String($bytes)
$encoded | Out-File -FilePath token_b64.txt -NoNewline

Write-Host "✓ Encoded files created"
```

**Windows (Command Prompt):**
```bash
# Use the encode_for_railway.py script
python encode_for_railway.py
```

**Linux/Mac:**
```bash
# Encode client_secret.json
cat client_secret.json | base64 > client_secret_b64.txt

# Encode token.json
cat token.json | base64 > token_b64.txt
```

### Step 3: Push Code to GitHub

```bash
git add .
git commit -m "Add Instagram/Snapchat downloader"
git push origin main
```

### Step 4: Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will start building automatically

### Step 5: Configure Environment Variables

In Railway dashboard, go to your service → Variables tab and add:

#### Required Variables:
```
YOUTUBE_CLIENT_SECRET_B64=<paste content from client_secret_b64.txt>
YOUTUBE_TOKEN_JSON=<paste content from token_b64.txt>
AUTO_UPLOAD_TO_YOUTUBE=true
```

#### Optional Variables:
```
# Watermark settings
ADD_WATERMARK=true
WATERMARK_TEXT=Lahori Twins

# Female detection (requires heavy AI models - may cause memory issues)
SKIP_FEMALE_VIDEOS=false

# Video splitting
SPLIT_LONG_VIDEOS=true
SPLIT_DURATION_SECONDS=38

# YouTube settings
VIDEO_PRIVACY=public
DEFAULT_DESCRIPTION=#rajabfamily #rajabbutt #viralshorts #maandogar #shezi #haidershah #haiderlive #jahangir
```

### Step 6: Update Procfile

Railway needs to know which script to run. Update your `Procfile`:

```
web: python -u railway_runtime_setup.py && python -u insta_snap_youtube.py
```

Or rename `Procfile.insta` to `Procfile`:
```bash
# Windows
copy Procfile.insta Procfile

# Linux/Mac
cp Procfile.insta Procfile
```

Then commit and push:
```bash
git add Procfile
git commit -m "Update Procfile for Instagram/Snapchat script"
git push origin main
```

Railway will automatically redeploy.

### Step 7: Monitor Deployment

1. In Railway dashboard, click on your service
2. Go to "Deployments" tab
3. Click on the latest deployment
4. View logs to see if it's working

---

## 🔍 Checking if It's Working

### View Logs in Railway

1. Go to your Railway project
2. Click on your service
3. Click "View Logs"

You should see output like:
```
→ Setting up Railway environment...
✓ client_secret.json created from environment variable
✓ token.json created from environment variable
✓ config.json created from base config and environment variables
✓ Railway setup complete
→ Starting main script...

============================================================
Instagram & Snapchat to YouTube
============================================================
Check interval: 10 minutes
YouTube: @LahoriTwins
============================================================

[10:30:00] Checking...

→ Checking instagram @i.haiderr
→ Checking instagram @rajab.butt94
→ Checking snapchat @i-haiderr
→ Checking snapchat @rajab.butt7

→ Next check in 10 minutes
```

### Check YouTube Channel

Visit https://www.youtube.com/@LahoriTwins and check for new uploads.

### Common Log Messages

**Success:**
```
✓ Downloaded: 20240115_103005_i.haiderr.mp4
✓ No female detected
✓ Watermark added
→ Uploading: 20240115_103005_i.haiderr.mp4
✓ Uploaded! ID: abc123xyz
```

**No new content:**
```
→ Checking instagram @i.haiderr
  → No new post found
```

**Skipped content:**
```
✗ Skipped: Copyright detected
✗ Skipped: Female detected
```

---

## ⚠️ Important Railway Limitations

### 1. Memory Limitations
Railway free tier has limited memory. If using female detection (DeepFace), you may hit memory limits.

**Solution:** Disable female detection on Railway:
```
SKIP_FEMALE_VIDEOS=false
```

### 2. Ephemeral Filesystem
Railway's filesystem is temporary. Files are deleted on restart.

**Solution:** The script is already optimized to delete files immediately after upload.

### 3. Build Time
First deployment may take 5-10 minutes to install FFmpeg and dependencies.

### 4. YouTube API Quota
Limited to ~6 uploads per day (10,000 API units).

---

## 🐛 Troubleshooting

### "client_secret.json not found"

**Problem:** Base64 encoding failed or environment variable not set.

**Solution:**
1. Verify `YOUTUBE_CLIENT_SECRET_B64` is set in Railway
2. Check the base64 content is complete (no line breaks)
3. Re-encode and update the variable

### "YouTube authentication failed"

**Problem:** Token expired or invalid.

**Solution:**
1. Generate fresh `token.json` locally
2. Re-encode to base64
3. Update `YOUTUBE_TOKEN_JSON` in Railway
4. Redeploy

### "yt-dlp not installed"

**Problem:** Build failed or dependencies not installed.

**Solution:**
1. Check Railway build logs
2. Verify `requirements.txt` includes `yt-dlp`
3. Trigger rebuild

### "ffmpeg not installed"

**Problem:** FFmpeg not available in Railway environment.

**Solution:**
Create `nixpacks.toml` in your repo:
```toml
[phases.setup]
aptPkgs = ['ffmpeg']
```

Then commit and push:
```bash
git add nixpacks.toml
git commit -m "Add FFmpeg to Railway build"
git push origin main
```

### "Memory limit exceeded"

**Problem:** DeepFace AI models use too much memory.

**Solution:**
Disable female detection:
```
SKIP_FEMALE_VIDEOS=false
```

### "No new content found"

**Problem:** Instagram/Snapchat blocking Railway's IP.

**Solution:**
1. This is normal - platforms block automated downloads
2. Script will keep retrying every 10 minutes
3. Consider using a proxy service (advanced)

### Script stops after a while

**Problem:** Railway may restart services periodically.

**Solution:**
The script has auto-restart built-in. Check logs for errors.

---

## 📊 Monitoring Your Deployment

### Railway Dashboard
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time script output
- **Deployments**: History of deployments

### YouTube Studio
- Check uploads at: https://studio.youtube.com
- Monitor quota usage
- Review uploaded videos

### Set Up Alerts (Optional)

Railway doesn't have built-in alerts, but you can:
1. Use Railway's webhook feature
2. Set up external monitoring (UptimeRobot, etc.)
3. Check logs daily

---

## 🔄 Updating Your Deployment

### Update Code
```bash
# Make changes to insta_snap_youtube.py
git add .
git commit -m "Update script"
git push origin main
```

Railway will automatically redeploy.

### Update Environment Variables
1. Go to Railway dashboard
2. Click your service → Variables
3. Update values
4. Click "Redeploy" if needed

### Update Credentials
If YouTube token expires:
1. Generate new `token.json` locally
2. Encode to base64
3. Update `YOUTUBE_TOKEN_JSON` in Railway
4. Redeploy

---

## 💰 Railway Pricing

### Free Tier (Hobby Plan)
- $5 free credit per month
- ~500 hours of runtime
- Shared CPU
- 512MB RAM
- 1GB disk

**Sufficient for this script!**

### Pro Plan ($20/month)
- More resources
- Priority support
- Better for heavy usage

---

## 🎯 Testing Checklist

After deployment, verify:

- [ ] Railway build completed successfully
- [ ] Logs show "Railway setup complete"
- [ ] Script starts without errors
- [ ] YouTube authentication works
- [ ] Script checks accounts every 10 minutes
- [ ] Downloads work (check logs)
- [ ] Uploads to YouTube work
- [ ] Files are deleted after upload

---

## 🚨 Emergency: Stop the Script

If something goes wrong:

1. **Pause deployment:**
   - Railway dashboard → Service → Settings → "Pause"

2. **Check logs:**
   - Identify the error
   - Fix locally
   - Push update

3. **Resume:**
   - Railway dashboard → Service → Settings → "Resume"

---

## 📝 Environment Variables Reference

### Required
| Variable | Description | Example |
|----------|-------------|---------|
| `YOUTUBE_CLIENT_SECRET_B64` | Base64 encoded client_secret.json | `eyJpbnN0YWxsZWQi...` |
| `YOUTUBE_TOKEN_JSON` | Base64 encoded token.json | `eyJhY2Nlc3NfdG9r...` |
| `AUTO_UPLOAD_TO_YOUTUBE` | Enable YouTube uploads | `true` |

### Optional
| Variable | Description | Default |
|----------|-------------|---------|
| `ADD_WATERMARK` | Add watermark to videos | `true` |
| `WATERMARK_TEXT` | Watermark text | `Lahori Twins` |
| `SKIP_FEMALE_VIDEOS` | Enable female detection | `false` (recommended) |
| `SPLIT_LONG_VIDEOS` | Split videos >38s | `true` |
| `SPLIT_DURATION_SECONDS` | Split duration | `38` |
| `VIDEO_PRIVACY` | YouTube privacy | `public` |
| `DEFAULT_DESCRIPTION` | Default hashtags | `#rajabfamily...` |

---

## 🎉 Success!

If you see this in logs:
```
✓ Uploaded! ID: abc123xyz
```

Your script is working! Check your YouTube channel for the uploaded video.

---

## 🆘 Need Help?

1. **Check logs first** - Most issues are visible in Railway logs
2. **Review troubleshooting section** above
3. **Test locally** - Make sure script works on your computer first
4. **Check Railway status** - https://railway.app/status

---

## 📚 Additional Resources

- Railway Docs: https://docs.railway.app
- YouTube API Docs: https://developers.google.com/youtube/v3
- yt-dlp Docs: https://github.com/yt-dlp/yt-dlp

---

**Happy Deploying! 🚀**

Your Instagram/Snapchat content will now automatically upload to YouTube 24/7!
