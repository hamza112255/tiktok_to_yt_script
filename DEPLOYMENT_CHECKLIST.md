# Railway Deployment Checklist

## ✅ Pre-Deployment Checklist

### Local Setup
- [ ] Python 3.8+ installed
- [ ] FFmpeg installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `Track 1.mpeg` and `Track 2.mpeg` present
- [ ] `client_secret.json` obtained from Google Cloud Console
- [ ] Script tested locally (`python insta_snap_youtube.py`)
- [ ] `token.json` generated (after local authentication)
- [ ] Script successfully downloads and uploads at least one video locally

### GitHub Setup
- [ ] Code pushed to GitHub
- [ ] Repository is accessible
- [ ] All files committed (including audio tracks)
- [ ] `.gitignore` excludes sensitive files (token.json, client_secret.json)

### Credentials Preparation
- [ ] `client_secret.json` encoded to base64
- [ ] `token.json` encoded to base64
- [ ] Base64 files saved (`client_secret_b64.txt`, `token_b64.txt`)
- [ ] Base64 content copied and ready to paste

---

## 🚀 Deployment Steps

### Step 1: Create Railway Project
- [ ] Logged into Railway (https://railway.app)
- [ ] Clicked "New Project"
- [ ] Selected "Deploy from GitHub repo"
- [ ] Chose correct repository
- [ ] Build started automatically

### Step 2: Configure Environment Variables
- [ ] Opened Railway dashboard
- [ ] Clicked on service
- [ ] Went to "Variables" tab
- [ ] Added `YOUTUBE_CLIENT_SECRET_B64` (paste from client_secret_b64.txt)
- [ ] Added `YOUTUBE_TOKEN_JSON` (paste from token_b64.txt)
- [ ] Added `AUTO_UPLOAD_TO_YOUTUBE=true`
- [ ] Added optional variables (watermark, privacy, etc.)
- [ ] Saved all variables

### Step 3: Update Procfile
- [ ] Renamed `Procfile.insta` to `Procfile` OR
- [ ] Updated existing `Procfile` to run `insta_snap_youtube.py`
- [ ] Committed changes
- [ ] Pushed to GitHub
- [ ] Railway redeployed automatically

### Step 4: Add FFmpeg Support (if needed)
- [ ] Created `nixpacks.toml` with FFmpeg
- [ ] Committed and pushed
- [ ] Railway rebuilt with FFmpeg

---

## 🔍 Verification Steps

### Check Build
- [ ] Railway build completed successfully (green checkmark)
- [ ] No build errors in logs
- [ ] All dependencies installed
- [ ] FFmpeg available

### Check Logs
- [ ] Opened Railway logs
- [ ] Saw "Railway setup complete"
- [ ] Saw "Starting main script..."
- [ ] Saw "Instagram & Snapchat to YouTube" header
- [ ] Saw "Checking..." messages every 10 minutes
- [ ] No error messages

### Check Functionality
- [ ] Script checks Instagram accounts
- [ ] Script checks Snapchat accounts
- [ ] Downloads appear in logs (if content available)
- [ ] Uploads appear in logs (if content downloaded)
- [ ] YouTube channel shows new uploads
- [ ] Files deleted after upload (check logs)

---

## 📊 Monitoring Checklist

### Daily Checks
- [ ] Check Railway logs for errors
- [ ] Verify script is still running
- [ ] Check YouTube channel for new uploads
- [ ] Monitor Railway resource usage (CPU, Memory)
- [ ] Check Railway credit usage

### Weekly Checks
- [ ] Review uploaded videos on YouTube
- [ ] Check YouTube API quota usage
- [ ] Verify no copyright strikes
- [ ] Check for any blocked accounts
- [ ] Review Railway metrics

### Monthly Checks
- [ ] Verify YouTube token is still valid
- [ ] Check Railway billing
- [ ] Review script performance
- [ ] Update dependencies if needed
- [ ] Check for yt-dlp updates

---

## 🐛 Troubleshooting Checklist

### If Build Fails
- [ ] Check Railway build logs
- [ ] Verify `requirements.txt` is correct
- [ ] Check for syntax errors in code
- [ ] Verify `Procfile` is correct
- [ ] Check if FFmpeg is needed (add `nixpacks.toml`)

### If Script Doesn't Start
- [ ] Check Railway logs for errors
- [ ] Verify environment variables are set
- [ ] Check `YOUTUBE_CLIENT_SECRET_B64` is complete
- [ ] Check `YOUTUBE_TOKEN_JSON` is complete
- [ ] Verify `Procfile` points to correct script

### If Authentication Fails
- [ ] Regenerate `token.json` locally
- [ ] Re-encode to base64
- [ ] Update `YOUTUBE_TOKEN_JSON` in Railway
- [ ] Redeploy
- [ ] Check client_secret.json is valid

### If Downloads Fail
- [ ] Check if Instagram/Snapchat is blocking
- [ ] Verify yt-dlp is installed
- [ ] Check account URLs are correct
- [ ] Wait and retry (platforms may temporarily block)
- [ ] Check Railway logs for specific errors

### If Uploads Fail
- [ ] Check YouTube API quota
- [ ] Verify token is valid
- [ ] Check video format is correct
- [ ] Verify YouTube channel exists
- [ ] Check Railway logs for error details

### If Memory Issues
- [ ] Disable female detection (`SKIP_FEMALE_VIDEOS=false`)
- [ ] Reduce max file size
- [ ] Upgrade Railway plan
- [ ] Check for memory leaks in logs

---

## 🔧 Maintenance Checklist

### Regular Maintenance
- [ ] Update yt-dlp regularly
- [ ] Check for Python package updates
- [ ] Monitor Railway credit usage
- [ ] Review YouTube API quota
- [ ] Check for Railway service updates

### Token Refresh (Every 6 months)
- [ ] Run script locally
- [ ] Re-authenticate with YouTube
- [ ] Generate new `token.json`
- [ ] Encode to base64
- [ ] Update Railway variable
- [ ] Redeploy

### Dependency Updates
- [ ] Update `requirements.txt`
- [ ] Test locally
- [ ] Commit and push
- [ ] Verify Railway rebuild succeeds
- [ ] Monitor for issues

---

## 📈 Performance Checklist

### Optimize for Railway
- [ ] Female detection disabled (saves memory)
- [ ] Max file size limited (100MB)
- [ ] Files deleted immediately after upload
- [ ] Check interval appropriate (10 minutes)
- [ ] Tracking file size reasonable (<1MB)

### Optimize for YouTube
- [ ] Video format correct (MP4)
- [ ] Resolution appropriate (1080x1920)
- [ ] File size reasonable (<100MB)
- [ ] Metadata complete (title, description)
- [ ] Privacy settings correct

### Optimize for Bandwidth
- [ ] Download only 1 item per check
- [ ] Skip large files (>100MB)
- [ ] Delete files after upload
- [ ] Use efficient video encoding

---

## 🎯 Success Criteria

### Deployment Success
- ✅ Railway build completes without errors
- ✅ Script starts and runs continuously
- ✅ Logs show regular checks every 10 minutes
- ✅ No authentication errors
- ✅ No memory errors

### Functional Success
- ✅ Downloads content from Instagram
- ✅ Downloads content from Snapchat
- ✅ Converts images to videos
- ✅ Adds watermark correctly
- ✅ Uploads to YouTube successfully
- ✅ Deletes files after upload

### Operational Success
- ✅ Runs 24/7 without intervention
- ✅ Handles errors gracefully
- ✅ Stays within Railway free tier
- ✅ Stays within YouTube API quota
- ✅ No copyright strikes

---

## 📝 Documentation Checklist

### Files to Review
- [ ] `RAILWAY_INSTA_SNAP_DEPLOYMENT.md` - Full deployment guide
- [ ] `RAILWAY_QUICK_DEPLOY.txt` - Quick reference
- [ ] `TROUBLESHOOTING.md` - Common issues
- [ ] `README_INSTA_SNAP.md` - Script documentation
- [ ] `START_HERE.md` - Getting started

### Scripts to Know
- [ ] `insta_snap_youtube.py` - Main script
- [ ] `encode_for_railway_insta.py` - Encode credentials
- [ ] `test_setup.py` - Test local setup
- [ ] `test_railway_setup.py` - Test Railway setup
- [ ] `railway_runtime_setup.py` - Railway initialization

---

## 🚨 Emergency Procedures

### If Script Crashes
1. [ ] Check Railway logs for error
2. [ ] Identify the issue
3. [ ] Fix locally
4. [ ] Test locally
5. [ ] Push to GitHub
6. [ ] Verify Railway redeploys
7. [ ] Monitor logs

### If YouTube Token Expires
1. [ ] Run script locally
2. [ ] Re-authenticate
3. [ ] Generate new token.json
4. [ ] Encode to base64
5. [ ] Update Railway variable
6. [ ] Redeploy

### If Railway Runs Out of Credit
1. [ ] Add payment method
2. [ ] Add more credit
3. [ ] Or optimize to stay in free tier
4. [ ] Or pause deployment temporarily

### If Account Gets Blocked
1. [ ] Check which platform blocked
2. [ ] Wait 24 hours
3. [ ] Try with VPN (advanced)
4. [ ] Or remove that account from script

---

## 📞 Support Resources

### Documentation
- Railway Docs: https://docs.railway.app
- YouTube API: https://developers.google.com/youtube/v3
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- FFmpeg: https://ffmpeg.org/documentation.html

### Community
- Railway Discord: https://discord.gg/railway
- Railway Status: https://railway.app/status

### Your Documentation
- Full guide: `RAILWAY_INSTA_SNAP_DEPLOYMENT.md`
- Quick guide: `RAILWAY_QUICK_DEPLOY.txt`
- Troubleshooting: `TROUBLESHOOTING.md`

---

## ✅ Final Verification

Before considering deployment complete:

- [ ] Railway build successful
- [ ] Script running continuously
- [ ] Logs show regular activity
- [ ] At least one successful download
- [ ] At least one successful upload
- [ ] YouTube channel shows new video
- [ ] No errors in logs
- [ ] Resource usage acceptable
- [ ] Within Railway free tier
- [ ] Within YouTube API quota

---

## 🎉 Deployment Complete!

If all checkboxes are checked, your deployment is successful!

Your Instagram/Snapchat content is now automatically uploading to YouTube 24/7.

**Next Steps:**
1. Monitor daily for first week
2. Check YouTube channel regularly
3. Review Railway logs for issues
4. Adjust settings as needed
5. Enjoy automated uploads!

---

**Deployed**: [Date]
**Railway Project**: [Project Name]
**YouTube Channel**: https://www.youtube.com/@LahoriTwins
**Status**: ✅ Active
