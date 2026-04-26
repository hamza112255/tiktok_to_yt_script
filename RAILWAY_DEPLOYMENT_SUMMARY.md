# Railway Deployment Summary

## 🎯 What You Need to Do

### 1. Prepare Credentials (5 minutes)
```bash
# Run script locally to generate token.json
python insta_snap_youtube.py

# Encode credentials for Railway
python encode_for_railway_insta.py
```

This creates:
- `client_secret_b64.txt`
- `token_b64.txt`

### 2. Push to GitHub (2 minutes)
```bash
git add .
git commit -m "Add Instagram/Snapchat downloader for Railway"
git push origin main
```

### 3. Deploy to Railway (3 minutes)
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Wait for build

### 4. Add Environment Variables (5 minutes)
In Railway dashboard → Variables, add:

**Required:**
```
YOUTUBE_CLIENT_SECRET_B64=<paste from client_secret_b64.txt>
YOUTUBE_TOKEN_JSON=<paste from token_b64.txt>
AUTO_UPLOAD_TO_YOUTUBE=true
```

**Optional:**
```
ADD_WATERMARK=true
WATERMARK_TEXT=Lahori Twins
VIDEO_PRIVACY=public
```

### 5. Update Procfile (2 minutes)
```bash
# Copy the Instagram/Snapchat Procfile
copy Procfile.insta Procfile

# Commit and push
git add Procfile
git commit -m "Update Procfile for Instagram/Snapchat"
git push origin main
```

Railway will automatically redeploy.

---

## ✅ How to Check if It's Working

### Method 1: Railway Logs
1. Go to Railway dashboard
2. Click your service
3. Click "View Logs"

**Look for:**
```
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

### Method 2: YouTube Channel
Visit https://www.youtube.com/@LahoriTwins

Check for new uploads every 10 minutes.

### Method 3: Success Messages
When content is found and uploaded:
```
✓ Downloaded: 20240115_103005_i.haiderr.mp4
→ Processing video
✓ No female detected
→ Adding watermark: Lahori Twins
✓ Watermark added
→ Uploading: 20240115_103005_i.haiderr.mp4
  → 100%
✓ Uploaded! ID: abc123xyz
```

---

## 🐛 Common Issues & Quick Fixes

### Issue: "client_secret.json not found"
**Fix:** Check `YOUTUBE_CLIENT_SECRET_B64` variable in Railway

### Issue: "YouTube authentication failed"
**Fix:** Regenerate token.json locally and re-encode

### Issue: "ffmpeg not installed"
**Fix:** Create `nixpacks.toml`:
```toml
[phases.setup]
aptPkgs = ['ffmpeg']
```

### Issue: "Memory limit exceeded"
**Fix:** Set `SKIP_FEMALE_VIDEOS=false` in Railway variables

### Issue: "No new content found"
**Fix:** This is normal. Instagram/Snapchat may block automated downloads. Script will keep retrying.

---

## 📊 What to Expect

### Normal Behavior
- Script checks every 10 minutes
- Downloads new content when available
- Converts images to videos with music
- Adds watermark
- Uploads to YouTube
- Deletes files after upload

### Expected Logs
```
[10:30:00] Checking...
→ Checking instagram @i.haiderr
  → No new post found
→ Checking instagram @rajab.butt94
  → No new reel found
→ Checking snapchat @i-haiderr
✓ Downloaded: 20240115_103005_i-haiderr.jpg
→ Converting image to video
✓ Converted to video
→ Uploading: 20240115_103005_i-haiderr.mp4
✓ Uploaded! ID: xyz789

→ Next check in 10 minutes
```

### Upload Frequency
- Depends on how often accounts post
- YouTube quota: ~6 uploads per day max
- Script runs 24/7 automatically

---

## 💰 Railway Costs

### Free Tier
- $5 free credit per month
- ~500 hours of runtime
- **Sufficient for this script!**

### Usage Estimate
- This script uses minimal resources
- Should stay within free tier
- Monitor in Railway dashboard

---

## 📚 Documentation Files

### Quick Start
- **RAILWAY_QUICK_DEPLOY.txt** - Quick reference card
- **START_HERE.md** - Getting started guide

### Detailed Guides
- **RAILWAY_INSTA_SNAP_DEPLOYMENT.md** - Full deployment guide
- **DEPLOYMENT_CHECKLIST.md** - Step-by-step checklist
- **TROUBLESHOOTING.md** - Common issues & solutions

### Scripts
- **insta_snap_youtube.py** - Main script
- **encode_for_railway_insta.py** - Encode credentials
- **test_railway_setup.py** - Test Railway deployment

---

## 🎯 Success Indicators

✅ Railway build completed
✅ Logs show "Railway setup complete"
✅ Script checks accounts every 10 minutes
✅ Downloads appear in logs (when content available)
✅ Uploads appear on YouTube
✅ No error messages

---

## 🚀 You're Ready!

Follow the 5 steps above, and your Instagram/Snapchat content will automatically upload to YouTube 24/7!

**Total Time:** ~20 minutes
**Difficulty:** Easy
**Cost:** Free (Railway free tier)

---

## 📞 Need Help?

1. **Check logs first** - Railway dashboard → View Logs
2. **Review troubleshooting** - See TROUBLESHOOTING.md
3. **Check documentation** - See RAILWAY_INSTA_SNAP_DEPLOYMENT.md
4. **Test locally** - Make sure it works on your computer first

---

## 🎉 Final Notes

- Script runs automatically every 10 minutes
- No need to keep your computer on
- Railway handles everything
- Check YouTube channel for uploads
- Monitor Railway logs for issues

**Happy Deploying! 🚀**

Your content is now uploading automatically to @LahoriTwins!
