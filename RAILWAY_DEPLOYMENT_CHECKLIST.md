# Railway Deployment Checklist - YouTube Quota Rotation

## Pre-Deployment (Do This First)

### Local Setup
- [ ] Created 3 Google Cloud projects
- [ ] Downloaded `client_secret_1.json`, `client_secret_2.json`, `client_secret_3.json`
- [ ] Placed files in project root directory
- [ ] Run `python authenticate_all_projects.py`
- [ ] Verified `token_1.json`, `token_2.json`, `token_3.json` were created
- [ ] Run `python check_rotation_status.py` to verify all projects are ready

### Encode for Railway
- [ ] Run `python encode_for_railway_rotation.py`
- [ ] Verify `railway_rotation_credentials.txt` was created
- [ ] Open the file and review the environment variables

## Railway Configuration

### Add Environment Variables
- [ ] Go to Railway dashboard → Your project → Your service
- [ ] Click "Variables" tab
- [ ] Add `YOUTUBE_CLIENT_SECRET_1_B64` (copy from railway_rotation_credentials.txt)
- [ ] Add `YOUTUBE_TOKEN_1_JSON` (copy from railway_rotation_credentials.txt)
- [ ] Add `YOUTUBE_CLIENT_SECRET_2_B64` (copy from railway_rotation_credentials.txt)
- [ ] Add `YOUTUBE_TOKEN_2_JSON` (copy from railway_rotation_credentials.txt)
- [ ] Add `YOUTUBE_CLIENT_SECRET_3_B64` (copy from railway_rotation_credentials.txt)
- [ ] Add `YOUTUBE_TOKEN_3_JSON` (copy from railway_rotation_credentials.txt)
- [ ] Verify all 6 variables are added correctly
- [ ] Keep existing variables (Instagram credentials, etc.)

## Git & Deployment

### Push to GitHub
- [ ] Run `git status` to see changed files
- [ ] Run `git add .`
- [ ] Run `git commit -m "Add YouTube quota rotation support"`
- [ ] Run `git push origin main` (or your branch name)

### Railway Deployment
- [ ] Railway automatically detects the push
- [ ] Wait for build to complete
- [ ] Check deployment logs

## Verification

### Check Logs
- [ ] Open Railway dashboard → Your service → Deployments
- [ ] Click on the latest deployment
- [ ] Look for: `🔄 Using Project X (Day Y rotation)`
- [ ] Look for: `✓ YouTube authenticated (0/50 uploads today)`
- [ ] Verify no error messages

### Monitor First Upload
- [ ] Wait for the bot to detect a new video
- [ ] Check logs for upload progress
- [ ] Verify upload succeeds
- [ ] Check your YouTube channel for the video

## Post-Deployment

### Document Your Setup
- [ ] Note which day uses which project (check logs)
- [ ] Save `railway_rotation_credentials.txt` in a secure location (NOT in GitHub)
- [ ] Document any custom configuration

### Optional: Test Rotation
- [ ] Wait for the next day
- [ ] Check logs to see if it switches to a different project
- [ ] Verify uploads continue working

## Troubleshooting Checklist

If something goes wrong:

- [ ] Check Railway logs for error messages
- [ ] Verify all 6 environment variables are present
- [ ] Check variable names match exactly (case-sensitive)
- [ ] Verify base64 values are complete (not truncated)
- [ ] Try re-encoding credentials: `python encode_for_railway_rotation.py`
- [ ] Check GitHub repository has the latest code
- [ ] Verify Railway is connected to the correct GitHub repository

## Success Indicators

✅ Railway logs show: `🔄 Using Project X (Day Y rotation)`  
✅ Railway logs show: `✓ YouTube authenticated`  
✅ Videos upload successfully  
✅ No quota exceeded errors  
✅ Different project used on different days  

## Quick Reference Commands

```bash
# Local testing
python check_rotation_status.py
python test_rotation.py
python all_platforms_youtube.py

# Re-encode credentials
python encode_for_railway_rotation.py

# Git commands
git status
git add .
git commit -m "Your message"
git push origin main
```

## Important Notes

⚠️ **Never commit these files to GitHub:**
- `client_secret_*.json`
- `token_*.json`
- `railway_rotation_credentials.txt`

✅ **These are already in .gitignore**

⚠️ **Use the SAME YouTube account** for all project authentications

✅ **All projects upload to the SAME YouTube channel**

## Need Help?

- Full guide: `RAILWAY_ROTATION_DEPLOYMENT.md`
- Local setup: `YOUTUBE_QUOTA_ROTATION_GUIDE.md`
- Quick start: `QUICK_START_ROTATION.txt`

---

**Ready to deploy?** Start with the "Pre-Deployment" section above!
