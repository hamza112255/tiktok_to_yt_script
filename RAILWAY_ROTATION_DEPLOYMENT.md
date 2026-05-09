# Railway Deployment with YouTube Quota Rotation

## Overview

This guide shows you how to deploy your bot to Railway with automatic YouTube API quota rotation across multiple Google Cloud projects.

## Prerequisites

✅ You have created 3 Google Cloud projects  
✅ You have downloaded `client_secret_1.json`, `client_secret_2.json`, `client_secret_3.json`  
✅ You have authenticated all projects locally (generated token files)

## Step-by-Step Deployment

### Step 1: Authenticate All Projects Locally

If you haven't already, run:

```bash
python authenticate_all_projects.py
```

This generates:
- `token_1.json`
- `token_2.json`
- `token_3.json`

**Important:** You must do this locally first! Railway cannot open a browser for OAuth.

### Step 2: Encode Credentials for Railway

Run the encoding script:

```bash
python encode_for_railway_rotation.py
```

This will:
- Find all your credential files
- Encode them to base64
- Save to `railway_rotation_credentials.txt`
- Show you exactly what to copy to Railway

### Step 3: Add Environment Variables to Railway

1. **Open Railway Dashboard**
   - Go to [railway.app](https://railway.app)
   - Select your project
   - Click on your service

2. **Go to Variables Tab**
   - Click "Variables" in the left sidebar

3. **Add Each Variable**
   
   Open `railway_rotation_credentials.txt` and for each variable:
   
   - Click "New Variable"
   - Copy the **Variable Name** (e.g., `YOUTUBE_CLIENT_SECRET_1_B64`)
   - Copy the **Value** (the long base64 string)
   - Click "Add"

   You'll need to add these variables:
   ```
   YOUTUBE_CLIENT_SECRET_1_B64
   YOUTUBE_TOKEN_1_JSON
   YOUTUBE_CLIENT_SECRET_2_B64
   YOUTUBE_TOKEN_2_JSON
   YOUTUBE_CLIENT_SECRET_3_B64
   YOUTUBE_TOKEN_3_JSON
   ```

4. **Keep Existing Variables**
   
   Don't delete your other environment variables like:
   - `INSTAGRAM_USERNAME`
   - `INSTAGRAM_PASSWORD`
   - Other config variables

### Step 4: Push Code to GitHub

```bash
git add .
git commit -m "Add YouTube quota rotation support"
git push origin main
```

### Step 5: Deploy on Railway

Railway will automatically:
- Detect the code changes
- Rebuild your service
- Use the new rotation system

### Step 6: Verify Deployment

Check the Railway logs:

```
🔄 Using Project X (Day Y rotation)
✓ YouTube authenticated (0/50 uploads today)
```

This confirms rotation is working!

## How Rotation Works on Railway

### Automatic Selection

The bot checks the current day of the month and selects the appropriate project:

```
Day 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31 → Project 1
Day 2, 5, 8, 11, 14, 17, 20, 23, 26, 29     → Project 2
Day 3, 6, 9, 12, 15, 18, 21, 24, 27, 30     → Project 3
```

### Environment Variable Lookup

For each project, the bot looks for:
- `YOUTUBE_CLIENT_SECRET_{N}_B64` - The OAuth client secret
- `YOUTUBE_TOKEN_{N}_JSON` - The authentication token

Where `{N}` is the project number (1, 2, 3, etc.)

### Fallback Behavior

If rotation variables are not found, the bot falls back to:
- `YOUTUBE_CLIENT_SECRET_B64`
- `YOUTUBE_TOKEN_JSON`

This ensures backward compatibility.

## Benefits

✅ **3x More Quota**: 30,000 units/day instead of 10,000  
✅ **~150 Uploads/Day**: Instead of ~50 uploads/day  
✅ **Automatic**: No manual intervention needed  
✅ **Same Channel**: All uploads go to your YouTube channel  
✅ **Zero Downtime**: Seamless rotation

## Monitoring

### Check Active Project

Look at Railway logs to see which project is active:

```
🔄 Using Project 2 (Day 14 rotation)
```

### Check Quota Usage

The bot tracks uploads per day:

```
✓ Uploaded [45/50 today] → https://youtube.com/watch?v=...
```

### Rotation Schedule

The rotation happens automatically at midnight (based on server time).

## Troubleshooting

### "YouTube upload disabled" Error

**Cause:** Missing environment variables

**Solution:**
1. Check Railway Variables tab
2. Verify all 6 variables are present
3. Make sure values are complete (no truncation)

### "YouTube token invalid" Error

**Cause:** Token expired or corrupted

**Solution:**
1. Re-authenticate locally: `python authenticate_all_projects.py`
2. Re-encode: `python encode_for_railway_rotation.py`
3. Update the token variables in Railway
4. Redeploy

### Wrong Project Being Used

**Cause:** Environment variables not detected

**Solution:**
1. Check variable names exactly match: `YOUTUBE_CLIENT_SECRET_1_B64` (not `YOUTUBE_CLIENT_SECRET1_B64`)
2. Verify all projects have both secret and token variables
3. Check Railway logs for error messages

### Still Hitting Quota Limits

**Solution:** Add more projects!

1. Create `client_secret_4.json`, `client_secret_5.json`, etc.
2. Authenticate them locally
3. Re-run `python encode_for_railway_rotation.py`
4. Add the new variables to Railway
5. Redeploy

The rotation automatically includes all available projects!

## Adding More Projects Later

To add more projects:

1. **Create New Google Cloud Project**
   - Enable YouTube Data API v3
   - Create OAuth credentials
   - Download as `client_secret_4.json`

2. **Authenticate Locally**
   ```bash
   python authenticate_all_projects.py
   ```

3. **Encode New Credentials**
   ```bash
   python encode_for_railway_rotation.py
   ```

4. **Add to Railway**
   - Add `YOUTUBE_CLIENT_SECRET_4_B64`
   - Add `YOUTUBE_TOKEN_4_JSON`

5. **Redeploy**
   - Push code to GitHub (if needed)
   - Railway will automatically include the new project

## Environment Variables Reference

### Required for Rotation

```bash
# Project 1
YOUTUBE_CLIENT_SECRET_1_B64=<base64-encoded-client-secret>
YOUTUBE_TOKEN_1_JSON=<base64-encoded-token>

# Project 2
YOUTUBE_CLIENT_SECRET_2_B64=<base64-encoded-client-secret>
YOUTUBE_TOKEN_2_JSON=<base64-encoded-token>

# Project 3
YOUTUBE_CLIENT_SECRET_3_B64=<base64-encoded-client-secret>
YOUTUBE_TOKEN_3_JSON=<base64-encoded-token>

# Add more as needed...
```

### Optional (Fallback)

```bash
# Used if rotation variables not found
YOUTUBE_CLIENT_SECRET_B64=<base64-encoded-client-secret>
YOUTUBE_TOKEN_JSON=<base64-encoded-token>
```

## Security Notes

- ✅ Credentials are base64-encoded (not encrypted, but not plain text)
- ✅ Railway environment variables are private to your project
- ✅ Never commit `railway_rotation_credentials.txt` to GitHub
- ✅ The `.gitignore` file already excludes credential files

## Testing Locally Before Railway

Test the rotation locally:

```bash
# Check which project would be used today
python check_rotation_status.py

# Test the full rotation schedule
python test_rotation.py

# Run the bot locally with rotation
python all_platforms_youtube.py
```

## Summary

1. ✅ Authenticate all projects locally
2. ✅ Run `python encode_for_railway_rotation.py`
3. ✅ Copy variables from `railway_rotation_credentials.txt` to Railway
4. ✅ Push code to GitHub
5. ✅ Railway deploys automatically with rotation

**Result:** 3x more quota, automatic rotation, zero manual intervention!

## Need Help?

- Local setup: See `YOUTUBE_QUOTA_ROTATION_GUIDE.md`
- Quick start: See `QUICK_START_ROTATION.txt`
- Visual guide: See `ROTATION_DIAGRAM.txt`
