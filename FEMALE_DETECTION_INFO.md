# Female Detection Feature

## Overview

This feature uses **DeepFace**, a powerful facial recognition and analysis library, to detect female presence in videos. Unlike basic person detection, DeepFace can actually determine gender by analyzing facial features.

## How It Works

1. **Face Detection**: DeepFace detects faces in video frames
2. **Gender Analysis**: For each detected face, it predicts gender (Man/Woman)
3. **Confidence Scoring**: Analyzes multiple frames (every 3 seconds) to get accurate results
4. **Decision**: If females are detected in >30% of sampled frames, the video is skipped

## Technology Used

- **DeepFace**: State-of-the-art facial analysis library
- **Backend Models**: Uses pre-trained deep learning models for gender classification
- **Accuracy**: Much more accurate than basic person detection

## Configuration

In `config.json`:

```json
{
  "youtube_settings": {
    "skip_female_videos": false  // Set to true to enable female detection
  }
}
```

## Installation

The feature requires additional dependencies:

```bash
pip install deepface tf-keras
```

These are now included in:
- `requirements.txt` (for local use)
- `requirements-railway.txt` (for Railway deployment)

## Performance

- **Sampling**: Checks 8 frames per video (every 3 seconds)
- **Speed**: Slower than basic person detection but much more accurate
- **Resource Usage**: Requires more CPU/memory due to deep learning models

## Detection Process

```
Video → Sample Frames → Face Detection → Gender Analysis → Decision
         (every 3s)      (DeepFace)      (Man/Woman)      (Skip/Keep)
```

## Example Output

When enabled, you'll see:

```
→ Analyzing video for female presence (8 frames)...
✓ No female detected (checked 8 frames)
```

Or if female detected:

```
→ Analyzing video for female presence (8 frames)...
⚠ Female detected in 62.5% of frames
→ Skipping segment: female detected
```

## Advantages Over Previous Implementation

| Feature | Old (Person Detection) | New (DeepFace) |
|---------|----------------------|----------------|
| Gender Detection | ❌ No | ✓ Yes |
| Accuracy | Low (detects any person) | High (analyzes facial features) |
| False Positives | Very High | Low |
| Technology | OpenCV HOG / YOLO | Deep Learning (DeepFace) |

## Notes

- Currently **DISABLED** by default (`skip_female_videos: false`)
- First run will download pre-trained models (~100MB)
- Models are cached for future use
- Works on both local and Railway deployments

## Troubleshooting

If you see:
```
Warning: DeepFace not installed
```

Run:
```bash
pip install deepface tf-keras
```

Then redeploy to Railway.
