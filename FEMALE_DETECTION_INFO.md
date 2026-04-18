# Female Detection Feature

## ⚠️ Important: Railway Limitation

**Female detection is DISABLED on Railway** due to resource constraints. DeepFace requires significant CPU/memory and causes crashes on Railway's free tier.

### Where It Works:
- ✅ **Local machine** - Full DeepFace AI detection
- ❌ **Railway deployment** - Automatically disabled

### Railway Message:
```
⚠ Female detection disabled on Railway (resource constraints)
  To enable: run locally or upgrade Railway plan
```

---

## Overview

This feature uses **DeepFace**, a powerful facial recognition and analysis library, to detect female presence in videos. It only works when running locally on your computer.

## How It Works (Local Only)

1. **Face Detection**: DeepFace detects faces in video frames
2. **Gender Analysis**: For each detected face, it predicts gender (Man/Woman)
3. **Confidence Scoring**: Analyzes multiple frames (every 3 seconds) to get accurate results
4. **Decision**: If females are detected in >30% of sampled frames, the video is skipped

## Technology Used

- **DeepFace**: State-of-the-art facial analysis library
- **Backend Models**: Uses pre-trained deep learning models for gender classification
- **Accuracy**: Much more accurate than basic person detection
- **CPU Mode**: Runs on CPU (no GPU required)

## Configuration

In `config.json`:

```json
{
  "youtube_settings": {
    "skip_female_videos": false  // Set to true to enable (local only)
  }
}
```

## Installation (Local Use Only)

The feature requires additional dependencies:

```bash
pip install deepface tf-keras
```

These are included in `requirements.txt` for local use.

## Performance

- **Sampling**: Checks 5 frames per video (every 3 seconds)
- **Speed**: Slower than basic detection but much more accurate
- **Resource Usage**: Requires significant CPU/memory (not suitable for Railway)

## Detection Process

```
Video → Sample Frames → Face Detection → Gender Analysis → Decision
         (every 3s)      (DeepFace)      (Man/Woman)      (Skip/Keep)
```

## Example Output (Local)

When enabled locally, you'll see:

```
→ Analyzing video for female presence (5 frames)...
✓ No female detected (checked 5 frames)
```

Or if female detected:

```
→ Analyzing video for female presence (5 frames)...
⚠ Female detected in 60.0% of frames
→ Skipping segment: female detected
```

## Example Output (Railway)

On Railway, you'll see:

```
⚠ Female detection disabled on Railway (resource constraints)
  To enable: run locally or upgrade Railway plan
```

## Advantages Over Basic Person Detection

| Feature | Basic Person Detection | DeepFace (Local) |
|---------|----------------------|----------------|
| Gender Detection | ❌ No | ✓ Yes |
| Accuracy | Low (detects any person) | High (analyzes facial features) |
| False Positives | Very High | Low |
| Technology | OpenCV HOG / YOLO | Deep Learning (DeepFace) |
| Railway Compatible | ✓ Yes | ❌ No (too heavy) |

## Notes

- Currently **DISABLED** by default (`skip_female_videos: false`)
- **Automatically disabled on Railway** to prevent crashes
- First run will download pre-trained models (~100MB)
- Models are cached for future use
- Only works when running locally

## Troubleshooting

### On Railway:
Female detection is automatically disabled. This is normal and expected.

### On Local Machine:

If you see:
```
Warning: DeepFace not installed
```

Run:
```bash
pip install deepface tf-keras
```

### CUDA Errors:
The code automatically uses CPU mode to avoid GPU/CUDA issues.

---

## Summary

- 🏠 **Local**: Full AI-powered female detection with DeepFace
- ☁️ **Railway**: Feature automatically disabled (too resource-intensive)
- 🎯 **Recommendation**: Keep `skip_female_videos: false` for Railway deployments
- 💡 **Alternative**: Run the bot locally if you need female detection
