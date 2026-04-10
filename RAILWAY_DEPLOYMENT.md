# Railway Deployment Guide

## Important Notes

⚠️ **This script has limitations on Railway:**
- OAuth authentication requires browser access (difficult on Railway)
- Video processing requires significant storage
- Railway's ephemeral filesystem means downloaded videos will be lost on restart

## Recommended Approach

For this type of application, consider these alternatives:
1. **Run locally** with Railway for other services
2. **Use a VPS** (DigitalOcean, Linode, AWS EC2) instead
3. **Modify the script** to use Railway's persistent volumes

## If You Still Want to Deploy on Railway

### Step 1: Prepare Your Repository

1. Ensure all changes are committed:
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Sign up or log in
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository: `hamza112255/tiktok_to_yt_script`

### Step 3: Configure Environment Variables

In Railway dashboard, add these variables:

```
TIKTOK_USERNAME=your_username
AUTO_UPLOAD_TO_YOUTUBE=false
```

### Step 4: Add Google OAuth Credentials

Since Railway doesn't support browser-based OAuth easily, you need to:

1. Run the script locally FIRST to generate `token.json`
2. Convert credentials to base64:
```bash
cat client_secret.json | base64 > client_secret_b64.txt
cat token.json | base64 > token_b64.txt
```

3. Add to Railway environment variables:
```
CLIENT_SECRET_B64=<paste base64 content>
TOKEN_B64=<paste base64 content>
```

4. Modify script to decode these on startup (see below)

### Step 5: Add Persistent Storage (Optional)

Railway offers persistent volumes:
1. In Railway dashboard, go to your service
2. Click "Variables" → "Add Volume"
3. Mount path: `/app/downloaded_videos`

### Step 6: Deploy

Railway will automatically deploy when you push to GitHub.

## Alternative: Use Railway for API Only

Consider splitting your application:
- **Local script**: Downloads and processes videos
- **Railway API**: Handles uploads and scheduling
- **Railway Database**: Tracks processed videos

This is more suitable for Railway's architecture.

## Troubleshooting

### OAuth Issues
- Railway doesn't support interactive browser authentication
- Pre-generate `token.json` locally before deploying

### Storage Issues
- Railway has ephemeral filesystem
- Use Railway volumes or external storage (S3, Cloudinary)

### FFmpeg Issues
- Included in `nixpacks.toml`
- If issues persist, check Railway build logs

## Better Alternatives

For this type of automation, consider:
1. **DigitalOcean Droplet** ($6/month) - Full control
2. **AWS EC2 t2.micro** (Free tier) - More storage
3. **Heroku** (with persistent storage add-on)
4. **Your local machine** with cron jobs

Railway is better suited for:
- Web applications
- APIs
- Stateless services
- Microservices

Your script needs:
- Persistent storage
- Browser access for OAuth
- Long-running processes
- Video processing power

These requirements make a VPS a better choice.
