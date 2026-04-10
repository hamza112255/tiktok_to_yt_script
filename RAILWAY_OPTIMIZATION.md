# Railway Image Size Optimization

## Problem:
Railway free tier has a 4GB image size limit. Your original build was 5.9GB due to:
- OpenCV (computer vision library) - ~1.5GB
- Ultralytics YOLO (AI model) - ~500MB
- NumPy, Pillow, and other dependencies - ~1GB

## Solution:
Removed heavy video processing dependencies to reduce image size.

## What's Disabled on Railway:

### ❌ Female Detection (skip_female_videos)
- Requires: Ultralytics YOLO AI model
- Size: ~500MB
- Status: Disabled on Railway

### ❌ Advanced Video Processing
- Requires: OpenCV
- Size: ~1.5GB
- Status: Basic processing only

### ✅ What Still Works:

- ✓ Download TikTok videos
- ✓ Upload to YouTube
- ✓ Basic video splitting (using FFmpeg)
- ✓ Watermark removal
- ✓ Auto-upload and delete
- ✓ All core functionality

## New Image Size:
~1.5GB (well under 4GB limit)

## If You Need Full Features:

### Option 1: Upgrade Railway Plan
- Pro plan: 8GB image limit
- Cost: $20/month

### Option 2: Use VPS Instead
- DigitalOcean Droplet: $6/month
- AWS EC2: Free tier available
- Full control, no image size limits

### Option 3: Split Services
- Railway: Download and upload only
- Local machine: Video processing with AI

## To Enable Features Locally:

Install full dependencies:
```bash
pip install -r requirements.txt
```

This includes:
- opencv-python
- ultralytics
- All AI models

## Environment Variables:

These features are automatically disabled on Railway:
```
SKIP_FEMALE_VIDEOS=false  # Always false on Railway
ADD_WATERMARK=false       # Can enable (uses FFmpeg only)
SPLIT_LONG_VIDEOS=true    # Can enable (uses FFmpeg only)
```

## Recommendation:

For Railway deployment, use the lightweight version. If you need AI features (female detection), run locally or use a VPS.

The core TikTok → YouTube automation works perfectly without the heavy dependencies!
