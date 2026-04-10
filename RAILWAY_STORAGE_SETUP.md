# Railway Storage Setup Guide

## Problem: Ephemeral Filesystem

Railway's filesystem is ephemeral, meaning:
- ✓ Folders are created automatically by your script
- ✓ Videos download successfully
- ✗ Files are DELETED when Railway restarts
- ✗ You lose all videos on every deployment

## Solution 1: Railway Volumes (Persistent Storage)

### Step 1: Add Volumes in Railway Dashboard

1. Go to your Railway project
2. Click on your service
3. Go to "Settings" tab
4. Scroll to "Volumes" section
5. Click "Add Volume"

### Add These Volumes:

**Volume 1: Downloaded Videos**
- Mount Path: `/app/downloaded_videos`
- Click "Add"

**Volume 2: YouTube Ready Folder**
- Mount Path: `/app/youtube_ready`
- Click "Add"

**Volume 3: Tracking File (Optional)**
- Mount Path: `/app/data`
- Then modify script to save `downloaded_videos.json` to `/app/data/`

### Step 2: Verify Volumes

After adding volumes:
1. Go to "Deployments" tab
2. Trigger a new deployment (or it auto-deploys)
3. Check logs - you should see:
   ```
   ✓ Folders created: youtube_ready
   ```

### Step 3: Test Persistence

1. Download a video
2. Restart your service (Settings → Restart)
3. Check if video still exists in logs

## Solution 2: External Storage (Better for Large Videos)

Instead of Railway volumes, use cloud storage:

### Option A: AWS S3

Install boto3:
```bash
pip install boto3
```

Modify script to upload videos to S3 after download.

### Option B: Cloudinary (Free Tier)

Install cloudinary:
```bash
pip install cloudinary
```

Upload videos to Cloudinary after processing.

### Option C: Google Drive API

Since you already use Google APIs, upload to Google Drive:
```bash
pip install google-api-python-client
```

## Solution 3: Process and Delete (No Storage Needed)

Modify your workflow:
1. Download video → Process → Upload to YouTube → Delete immediately
2. No persistent storage needed
3. Only keep tracking file (`downloaded_videos.json`)

This is the most cost-effective for Railway!

## Recommended Approach for Your Script

### Best Option: Process and Delete Immediately

Your script already does this! Just ensure:

1. **Enable auto-upload in Railway environment variables:**
   ```
   AUTO_UPLOAD_TO_YOUTUBE=true
   ```

2. **Script flow:**
   - Download TikTok video → `downloaded_videos/`
   - Process video → `youtube_ready/`
   - Upload to YouTube
   - Delete video files (script already does this)
   - Only keep `downloaded_videos.json` (small file)

3. **Add volume only for tracking file:**
   - Mount Path: `/app/data`
   - Modify script to save tracking to `/app/data/downloaded_videos.json`

## Cost Comparison

### Railway Volumes:
- **Free tier**: 1GB included
- **Cost**: ~$0.25/GB/month
- **Example**: 10GB videos = $2.50/month

### External Storage:
- **AWS S3**: $0.023/GB/month
- **Cloudinary**: 25GB free
- **Google Drive**: 15GB free

### Process & Delete:
- **Cost**: $0 (no storage needed)
- **Best for**: Automated workflows

## Current Script Behavior

Your script ALREADY deletes videos after upload:
```python
def _cleanup_uploaded_video(self, uploaded_path):
    """Delete uploaded video from local folders"""
```

So you DON'T need persistent storage if:
- ✓ `AUTO_UPLOAD_TO_YOUTUBE=true`
- ✓ Videos upload successfully
- ✓ Script deletes after upload

## What You Need to Do

### Minimal Setup (Recommended):

1. **Set environment variable:**
   ```
   AUTO_UPLOAD_TO_YOUTUBE=true
   ```

2. **Add ONE small volume for tracking:**
   - Mount Path: `/app/data`
   - Size: 100MB (more than enough)

3. **Modify tracking file path** (optional):
   Update `railway_setup.py` to save tracking to volume.

### Full Storage Setup:

Only if you want to keep videos:
1. Add volumes for `downloaded_videos` and `youtube_ready`
2. Monitor storage usage in Railway dashboard
3. Pay for storage as needed

## Testing Storage

### Test if files persist:

1. SSH into Railway (if available) or check logs
2. Download a test video
3. Check file exists:
   ```bash
   ls -lh downloaded_videos/
   ```
4. Restart service
5. Check again - file should still exist if volume is mounted

### Without volumes:
- Files disappear after restart

### With volumes:
- Files persist across restarts

## Recommendation

For your use case (TikTok → YouTube automation):

**Use Process & Delete approach:**
- No volumes needed (or just 100MB for tracking)
- Set `AUTO_UPLOAD_TO_YOUTUBE=true`
- Videos are temporary (download → process → upload → delete)
- Saves money on Railway
- Keeps your deployment simple

Only add large volumes if you need to:
- Keep videos for manual review
- Retry failed uploads
- Archive downloaded content

## Questions?

- **Q: Will videos download without volumes?**
  - A: Yes! Folders are created automatically. Videos download fine.

- **Q: When do I lose videos?**
  - A: On Railway restart/redeploy (unless you have volumes)

- **Q: Do I need volumes?**
  - A: No, if you enable auto-upload and let script delete after upload

- **Q: How much storage do I need?**
  - A: Depends on video size. TikTok videos are ~5-50MB each.
    - 1 video at a time: No volume needed (process & delete)
    - 10 videos queued: ~500MB volume
    - 100 videos archived: ~5GB volume

## Next Steps

1. Decide: Do you want to keep videos or process & delete?
2. If keep: Add volumes in Railway dashboard
3. If delete: Just set `AUTO_UPLOAD_TO_YOUTUBE=true`
4. Test with one video to verify workflow
