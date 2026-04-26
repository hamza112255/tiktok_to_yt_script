#!/usr/bin/env python3
"""
Test Railway setup and configuration
Run this after deploying to Railway to verify everything is working
"""
import os
import sys
from pathlib import Path

def check_env_var(name, required=True):
    """Check if environment variable is set"""
    value = os.getenv(name)
    if value:
        # Show first 20 chars only for security
        preview = value[:20] + "..." if len(value) > 20 else value
        print(f"✓ {name} = {preview}")
        return True
    else:
        if required:
            print(f"✗ {name} (required)")
        else:
            print(f"⚠ {name} (optional, not set)")
        return False

def check_file(filename, required=True):
    """Check if file exists"""
    filepath = Path(filename)
    if filepath.exists():
        size = filepath.stat().st_size
        print(f"✓ {filename} ({size:,} bytes)")
        return True
    else:
        if required:
            print(f"✗ {filename} (required)")
        else:
            print(f"⚠ {filename} (optional, not found)")
        return False

def check_command(cmd):
    """Check if command is available"""
    import subprocess
    try:
        result = subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ {cmd}")
            return True
        else:
            print(f"✗ {cmd} (not working)")
            return False
    except FileNotFoundError:
        print(f"✗ {cmd} (not installed)")
        return False
    except Exception as e:
        print(f"✗ {cmd} ({e})")
        return False

def main():
    print("\n" + "="*60)
    print("Railway Setup Verification")
    print("="*60 + "\n")
    
    is_railway = any(os.getenv(name) for name in [
        'RAILWAY_PROJECT_ID',
        'RAILWAY_SERVICE_ID',
        'RAILWAY_ENVIRONMENT_ID'
    ])
    
    if is_railway:
        print("✓ Running on Railway\n")
    else:
        print("⚠ Not running on Railway (local environment)\n")
    
    results = []
    
    # Check environment variables
    print("Environment Variables:")
    results.append(check_env_var('YOUTUBE_CLIENT_SECRET_B64', required=True))
    results.append(check_env_var('YOUTUBE_TOKEN_JSON', required=True))
    results.append(check_env_var('AUTO_UPLOAD_TO_YOUTUBE', required=False))
    check_env_var('ADD_WATERMARK', required=False)
    check_env_var('WATERMARK_TEXT', required=False)
    check_env_var('SKIP_FEMALE_VIDEOS', required=False)
    check_env_var('VIDEO_PRIVACY', required=False)
    print()
    
    # Check files (after railway_runtime_setup.py runs)
    print("Configuration Files:")
    results.append(check_file('client_secret.json', required=True))
    results.append(check_file('token.json', required=True))
    results.append(check_file('config.json', required=True))
    check_file('Track 1.mpeg', required=True)
    check_file('Track 2.mpeg', required=True)
    print()
    
    # Check commands
    print("Required Commands:")
    results.append(check_command('python'))
    results.append(check_command('ffmpeg'))
    results.append(check_command('ffprobe'))
    results.append(check_command('yt-dlp'))
    print()
    
    # Check Python packages
    print("Python Packages:")
    packages = [
        ('google.oauth2', 'google-auth'),
        ('googleapiclient', 'google-api-python-client'),
        ('cv2', 'opencv-python'),
        ('PIL', 'pillow')
    ]
    
    for module, package in packages:
        try:
            __import__(module)
            print(f"✓ {package}")
            results.append(True)
        except ImportError:
            print(f"✗ {package}")
            results.append(False)
    print()
    
    # Check script
    print("Main Script:")
    results.append(check_file('insta_snap_youtube.py', required=True))
    results.append(check_file('video_processor.py', required=True))
    print()
    
    # Summary
    print("="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All checks passed ({passed}/{total})")
        print("\n🚀 Railway deployment is ready!")
        print("\nThe script should be running now.")
        print("Check Railway logs for output.")
    else:
        failed = total - passed
        print(f"⚠ {failed} check(s) failed ({passed}/{total} passed)")
        print("\n❌ Deployment has issues!")
        print("\nTroubleshooting:")
        print("1. Check Railway environment variables")
        print("2. Verify railway_runtime_setup.py ran successfully")
        print("3. Check Railway build logs")
        print("4. See RAILWAY_INSTA_SNAP_DEPLOYMENT.md")
    
    print("="*60 + "\n")
    
    # Railway-specific checks
    if is_railway:
        print("Railway Environment Info:")
        print(f"Project ID: {os.getenv('RAILWAY_PROJECT_ID', 'N/A')}")
        print(f"Service ID: {os.getenv('RAILWAY_SERVICE_ID', 'N/A')}")
        print(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'N/A')}")
        print()

if __name__ == "__main__":
    main()
