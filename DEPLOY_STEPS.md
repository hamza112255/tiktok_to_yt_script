# Step-by-Step Railway Deployment

## Prerequisites

Before deploying to Railway, you need:
1. GitHub account with your code pushed
2. Railway account (sign up at https://railway.app)
3. Google OAuth credentials already set up locally
4. `token.json` file generated (run script locally once)

## Step 1: Prepare Credentials for Railway

Run these commands on your local machine:

```bash
# Convert your credentials to base64
python -c "import base64; print(base64.b64encode(open('client_secret.json', 'rb').read()).decode())" > client_secret_b64.txt

python -c "import base64; print(base64.b64encode(open('token.json', 'rb').read()).decode())" > token_b64.txt
```

Keep these files safe - you'll need them in Step 4.

## Step 2: Push Code to GitHub

```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

## Step 3: Create Railway Project

1. Go to https://railway.app
2. Click "Login" and sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Authorize Railway to access your GitHub
6. Select repository: `hamza112255/tiktok_to_yt_script`
7. Click "Deploy Now"

## Step 4: Configure Environment Variables

In the Railway dashboard:

1. Click on your deployed service
2. Go to "Variables" tab
3. Click "New Variable" and add these one by one:

### Required Variables:

```
TIKTOK_USERNAME=your_tiktok_username
```

### OAuth Credentials (from Step 1):

```
CLIENT_SECRET_B64=<paste content from client_secret_b64.txt>
TOKEN_B64=<paste content from token_b64.txt>
```

### Optional Variables:

```
CHECK_INTERVAL_MINUTES=5
YOUTUBE_CHANNEL_NAME=My YouTube Channel
AUTO_UPLOAD_TO_YOUTUBE=true
VIDEO_PRIVACY=private
TITLE_SUFFIX= | TikTok
USE_TIKTOK_HASHTAGS=true
ADD_WATERMARK=false
WATERMARK_TEXT=Lahori Twins
SKIP_FEMALE_VIDEOS=false
SPLIT_LONG_VIDEOS=false
SPLIT_DURATION_SECONDS=30
MIN_SEGMENT_DURATION_SECONDS=20
```

4. Click "Deploy" to restart with new variables

## Step 5: Add Persistent Storage (Important!)

Railway's filesystem is ephemeral - files are deleted on restart. To persist videos:

1. In Railway dashboard, click your service
2. Go to "Settings" tab
3. Scroll to "Volumes"
4. Click "Add Volume"
5. Set mount path: `/app/downloaded_videos`
6. Click "Add"

Repeat for other folders:
- `/app/youtube_ready`

## Step 6: Monitor Deployment

1. Go to "Deployments" tab
2. Click on the latest deployment
3. Watch the build logs
4. Look for:
   - ✓ Dependencies installed
   - ✓ FFmpeg available
   - ✓ Credentials loaded
   - ✓ Script started

## Step 7: Check Logs

1. Go to "Logs" tab in Railway dashboard
2. You should see:
   ```
   → Setting up Railway environment...
   ✓ client_secret.json created from environment variable
   ✓ token.json created from environment variable
   ✓ config.json created from environment variables
   ✓ Railway setup complete
   ✓ Folders created: youtube_ready
   ✓ YouTube API authenticated successfully!
   ```

## Troubleshooting

### Build Fails

Check "Deployments" → "Build Logs" for errors:
- Missing dependencies? Check `requirements.txt`
- FFmpeg issues? Check `nixpacks.toml`

### OAuth Errors

```
✗ YouTube authentication failed
```

Solutions:
1. Verify `CLIENT_SECRET_B64` and `TOKEN_B64` are set correctly
2. Regenerate token locally and re-encode
3. Check token hasn't expired

### Script Crashes

```
error: failed to start
```

Solutions:
1. Check "Logs" tab for Python errors
2. Verify all environment variables are set
3. Check if `TIKTOK_USERNAME` is valid

### Videos Not Persisting

If videos disappear after restart:
1. Verify volumes are mounted (Step 5)
2. Check volume paths match script folders
3. Railway free tier has storage limits

## Important Limitations

⚠️ **Railway Challenges:**

1. **Storage Costs**: Videos take up space, Railway charges for storage
2. **Ephemeral Filesystem**: Without volumes, files are lost on restart
3. **OAuth Refresh**: Token may expire, requiring local regeneration
4. **Processing Power**: Video processing is CPU-intensive
5. **Bandwidth**: Downloading/uploading videos uses bandwidth

## Cost Estimate

Railway pricing (as of 2024):
- **Free tier**: $5 credit/month
- **Hobby plan**: $5/month + usage
- **Storage**: ~$0.25/GB/month
- **Bandwidth**: Included in most plans

For heavy video processing, expect $10-20/month.

## Alternative: VPS Deployment

For better control and lower costs, consider:

### DigitalOcean Droplet ($6/month):
```bash
# SSH into droplet
ssh root@your-droplet-ip

# Clone repo
git clone https://github.com/hamza112255/tiktok_to_yt_script.git
cd tiktok_to_yt_script

# Install dependencies
apt update
apt install python3-pip ffmpeg -y
pip3 install -r requirements.txt

# Upload credentials
# (use scp or paste content)

# Run with screen
screen -S tiktok
python3 tiktok_to_youtube.py
# Press Ctrl+A then D to detach
```

### AWS EC2 (Free Tier):
- t2.micro instance (1 year free)
- 30GB storage
- Same setup as DigitalOcean

## Next Steps

After successful deployment:

1. **Monitor logs** regularly for errors
2. **Check storage usage** in Railway dashboard
3. **Test video downloads** by adding URLs to `video_urls.txt`
4. **Set up alerts** for failures
5. **Backup credentials** securely

## Getting Help

If you encounter issues:
1. Check Railway documentation: https://docs.railway.app
2. Railway Discord: https://discord.gg/railway
3. Check script logs for specific errors
4. Verify all environment variables are set correctly

## Security Notes

- Never commit `client_secret.json` or `token.json` to git
- Rotate OAuth credentials if exposed
- Use Railway's secret variables for sensitive data
- Enable 2FA on your Railway account
- Regularly check Google Cloud Console for unauthorized access
