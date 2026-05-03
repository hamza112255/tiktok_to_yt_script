# Manual Installation Guide

## Issue: pip not recognized

Your Python is installed but `pip` is not in your system PATH.

---

## Solution 1: Use python -m pip (EASIEST)

Instead of `pip`, use `python -m pip`:

```bash
python -m pip install instaloader google-auth google-auth-oauthlib google-api-python-client
```

This should work immediately!

---

## Solution 2: Add pip to PATH

### Find pip location:
```bash
python -m site --user-site
```

This will show something like:
```
C:\Users\YourName\AppData\Roaming\Python\Python315\site-packages
```

### Add to PATH:
1. Press `Win + R`
2. Type `sysdm.cpl` and press Enter
3. Click "Advanced" tab
4. Click "Environment Variables"
5. Under "User variables", find "Path"
6. Click "Edit"
7. Click "New"
8. Add: `C:\Users\YourName\AppData\Roaming\Python\Python315\Scripts`
9. Click OK on all windows
10. **Close and reopen terminal**

Now `pip` should work!

---

## Install FFmpeg

### Option 1: Using Chocolatey (EASIEST)

1. Install Chocolatey (if not installed):
   - Open PowerShell as Administrator
   - Run:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. Install FFmpeg:
   ```bash
   choco install ffmpeg
   ```

### Option 2: Manual Download

1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
2. Download: `ffmpeg-release-essentials.zip`
3. Extract to: `C:\ffmpeg`
4. Add to PATH:
   - Press `Win + R`
   - Type `sysdm.cpl` and press Enter
   - Click "Advanced" tab
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit"
   - Click "New"
   - Add: `C:\ffmpeg\bin`
   - Click OK on all windows
5. **Close and reopen terminal**

### Option 3: Using winget (Windows 11)

```bash
winget install ffmpeg
```

---

## Quick Install Commands

Run these commands one by one:

```bash
# Install Python packages
python -m pip install instaloader google-auth google-auth-oauthlib google-api-python-client

# Verify installation
python -m pip list | findstr instaloader

# Check FFmpeg (after installing)
ffmpeg -version
```

---

## After Installation

Once packages are installed, run:

```bash
python instagram_youtube_local.py
```

Or double-click: `run_local.bat`

---

## Troubleshooting

### "python is not recognized"
- Reinstall Python from https://www.python.org/downloads/
- **Check "Add Python to PATH" during installation**

### "ModuleNotFoundError: No module named 'instaloader'"
- Run: `python -m pip install instaloader`

### "ffmpeg: command not found"
- Follow FFmpeg installation steps above
- Make sure to close and reopen terminal after adding to PATH

### "Permission denied"
- Run terminal as Administrator
- Or use: `python -m pip install --user instaloader ...`

---

## Verify Everything Works

```bash
# Check Python
python --version

# Check pip
python -m pip --version

# Check packages
python -m pip list

# Check FFmpeg
ffmpeg -version
```

If all commands work, you're ready to run the script!

---

## Run the Script

```bash
python instagram_youtube_local.py
```

That's it! 🎉
