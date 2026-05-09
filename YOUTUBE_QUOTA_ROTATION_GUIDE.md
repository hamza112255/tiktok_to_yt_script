# YouTube API Quota Rotation Guide

## Overview
This system automatically rotates between multiple Google Cloud projects to avoid hitting the daily YouTube API quota limit (10,000 units per project per day).

## How It Works

### Automatic Daily Rotation
- The script automatically selects which project to use based on the **day of the month**
- Example with 3 projects:
  - Day 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31 → Project 1
  - Day 2, 5, 8, 11, 14, 17, 20, 23, 26, 29 → Project 2
  - Day 3, 6, 9, 12, 15, 18, 21, 24, 27, 30 → Project 3

### File Naming Convention
```
client_secret_1.json  →  token_1.json  (Project 1)
client_secret_2.json  →  token_2.json  (Project 2)
client_secret_3.json  →  token_3.json  (Project 3)
...and so on
```

## Setup Steps

### 1. Create Multiple Google Cloud Projects

For each project you want to create:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click project dropdown → "New Project"
3. Name it: `youtube-uploader-1`, `youtube-uploader-2`, etc.
4. Click "Create"

### 2. Enable YouTube Data API v3

For each project:

1. Select the project
2. Go to "APIs & Services" → "Library"
3. Search for "YouTube Data API v3"
4. Click "Enable"

### 3. Create OAuth 2.0 Credentials

For each project:

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure OAuth consent screen if needed (use same settings for all)
4. Choose "Desktop app" as application type
5. Name it: `Desktop client 1`, `Desktop client 2`, etc.
6. Click "Create"

### 4. Download Client Secrets

For each project:

1. Click the download icon (⬇️) next to your OAuth client
2. Save with numbered names:
   - First project: `client_secret_1.json`
   - Second project: `client_secret_2.json`
   - Third project: `client_secret_3.json`
   - And so on...
3. Place all files in your project root directory

### 5. Authenticate All Projects

Run the authentication script:

```bash
python authenticate_all_projects.py
```

This will:
- Find all your `client_secret_X.json` files
- Open a browser for each one
- Ask you to login with your YouTube channel (use the SAME account for all)
- Generate corresponding `token_X.json` files

**Important:** Authenticate with the SAME YouTube channel account for all projects!

### 6. Run Your Main Script

```bash
python all_platforms_youtube.py
```

The script will automatically:
- Detect all available projects
- Select the appropriate project based on the current day
- Use that project's credentials
- Display which project is being used

## Verification

When the script starts, you should see:
```
🔄 Using Project 2 (Day 9 rotation)
✓ YouTube authenticated (0/50 uploads today)
```

This confirms:
- Which project number is active
- What day triggered this selection
- Authentication was successful

## Benefits

- **3x More Quota**: With 3 projects, you get 30,000 units/day instead of 10,000
- **Automatic Rotation**: No manual switching needed
- **Same Channel**: All uploads go to your same YouTube channel
- **Seamless**: Works exactly like before, just with more capacity

## Troubleshooting

### "client_secret_X.json not found"
- Make sure you downloaded and renamed the files correctly
- Files must be in the project root directory
- Use exact naming: `client_secret_1.json`, `client_secret_2.json`, etc.

### "token_X.json not found"
- Run `python authenticate_all_projects.py` to generate token files
- You must authenticate each project at least once

### "YouTube auth failed"
- Check that your OAuth credentials are for "Desktop app" (not Web app)
- Verify the token files aren't corrupted
- Try re-authenticating: delete `token_X.json` and run authentication script again

### Still hitting quota limits
- Create more projects (4, 5, 6, or more)
- Each additional project adds 10,000 more units per day
- The rotation will automatically include all available projects

## Adding More Projects

To add more projects later:

1. Create new Google Cloud project
2. Enable YouTube Data API v3
3. Create OAuth credentials
4. Download as `client_secret_4.json` (next number)
5. Run `python authenticate_all_projects.py`
6. The script will automatically detect and use the new project

No code changes needed - the rotation system automatically detects all available projects!

## How Many Projects Do You Need?

Calculate based on your upload volume:

- **1 project** = ~50 uploads/day (200 units per upload)
- **3 projects** = ~150 uploads/day
- **7 projects** = ~350 uploads/day
- **10 projects** = ~500 uploads/day

Choose based on your needs!
