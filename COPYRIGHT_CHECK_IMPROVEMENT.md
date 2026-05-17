# Copyright Check Improvement

## Problem
Previously, the bot would:
1. Upload video as Private
2. Wait 2 minutes
3. Check copyright status every 10 minutes
4. If video was still processing, wait another 10 minutes

This meant a copyrighted video could be on YouTube for 10+ minutes before being deleted.

## Solution
Modified `check_and_remove_restricted()` method to:
1. Upload video as Private
2. Wait 2 minutes (initial buffer)
3. **Poll continuously every 45 seconds** until video processing completes
4. Once `uploadStatus` becomes "processed", immediately check for copyright
5. Delete if copyright detected OR make Public if clean
6. Maximum wait time: 20 minutes (then check next cycle)

## Technical Details

### Polling Logic
- **Poll interval**: 45 seconds
- **Max wait time**: 20 minutes
- **Status checked**: `uploadStatus` field from YouTube API
- **Processing states**: "uploaded" or "" (empty) = still processing
- **Completed state**: "processed" = ready to check

### Processing Time
YouTube typically takes 2-8 minutes to process a short video:
- **Short videos (<1 min)**: 2-5 minutes
- **Medium videos (1-3 min)**: 5-10 minutes
- **Longer videos**: 10-20 minutes

With the new polling system:
- Video is checked **immediately** after processing completes
- Copyrighted videos are deleted within **seconds** of detection
- Clean videos are published **immediately**

## Benefits
✅ Copyrighted videos deleted within seconds (not 10+ minutes)
✅ Clean videos published immediately after processing
✅ No waiting for next 10-minute cycle
✅ User sees real-time progress with elapsed time updates
✅ Timeout prevents infinite loops (20 min max)

## Example Output
```
⏳ Waiting for video ABC123 to finish processing…
⏳ Video ABC123 still processing (2.3 min elapsed)…
⏳ Video ABC123 still processing (3.1 min elapsed)…
⏳ Video ABC123 still processing (3.9 min elapsed)…
⚠ Video ABC123 restricted (Content ID claim — blocked in 5 region(s)) — deleting from YouTube
✓ Deleted restricted video: ABC123
```

Or for clean videos:
```
⏳ Waiting for video XYZ789 to finish processing…
⏳ Video XYZ789 still processing (2.5 min elapsed)…
⏳ Video XYZ789 still processing (3.3 min elapsed)…
✓ Video XYZ789 — clean, published public
```
