#!/usr/bin/env python3
"""
Setup Verification Script
Tests if all dependencies and files are properly configured
"""
import sys
from pathlib import Path

def test_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {package_name or module_name}")
        return True
    except ImportError:
        print(f"✗ {package_name or module_name} (pip install {package_name or module_name})")
        return False

def test_command(cmd, name):
    """Test if a command is available"""
    import subprocess
    try:
        result = subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ {name}")
            return True
        else:
            print(f"✗ {name} (not working)")
            return False
    except FileNotFoundError:
        print(f"✗ {name} (not installed)")
        return False
    except Exception as e:
        print(f"✗ {name} ({e})")
        return False

def test_file(filepath, name):
    """Test if a file exists"""
    if filepath.exists():
        size = filepath.stat().st_size
        print(f"✓ {name} ({size:,} bytes)")
        return True
    else:
        print(f"✗ {name} (not found)")
        return False

def main():
    print("\n" + "="*60)
    print("Setup Verification for Instagram/Snapchat to YouTube")
    print("="*60 + "\n")
    
    base_dir = Path(__file__).resolve().parent
    
    results = []
    
    # Python version
    print("Python Version:")
    results.append(test_python_version())
    print()
    
    # Required commands
    print("Required Commands:")
    results.append(test_command('ffmpeg', 'FFmpeg'))
    results.append(test_command('ffprobe', 'FFprobe'))
    results.append(test_command('yt-dlp', 'yt-dlp'))
    print()
    
    # Required Python packages
    print("Required Python Packages:")
    results.append(test_import('google.oauth2', 'google-auth'))
    results.append(test_import('google_auth_oauthlib', 'google-auth-oauthlib'))
    results.append(test_import('googleapiclient', 'google-api-python-client'))
    results.append(test_import('cv2', 'opencv-python'))
    results.append(test_import('numpy', 'numpy'))
    results.append(test_import('PIL', 'pillow'))
    print()
    
    # Optional packages
    print("Optional Packages (for female detection):")
    test_import('deepface', 'deepface')
    test_import('tensorflow', 'tf-keras')
    print()
    
    # Required files
    print("Required Files:")
    results.append(test_file(base_dir / 'insta_snap_youtube.py', 'Main script'))
    results.append(test_file(base_dir / 'video_processor.py', 'Video processor'))
    results.append(test_file(base_dir / 'Track 1.mpeg', 'Audio Track 1'))
    results.append(test_file(base_dir / 'Track 2.mpeg', 'Audio Track 2'))
    print()
    
    # Configuration files
    print("Configuration Files:")
    has_config = test_file(base_dir / 'config.json', 'config.json')
    if not has_config:
        test_file(base_dir / 'config.defaults.json', 'config.defaults.json (fallback)')
    
    has_secret = test_file(base_dir / 'client_secret.json', 'client_secret.json (YouTube OAuth)')
    if not has_secret:
        print("  → Get from: https://console.cloud.google.com/")
    
    has_token = test_file(base_dir / 'token.json', 'token.json (YouTube token)')
    if not has_token:
        print("  → Will be created on first run")
    print()
    
    # Summary
    print("="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All checks passed ({passed}/{total})")
        print("\nYou're ready to run:")
        print("  python insta_snap_youtube.py")
    else:
        failed = total - passed
        print(f"⚠ {failed} check(s) failed ({passed}/{total} passed)")
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        print("\nAnd ensure FFmpeg is installed:")
        print("  See INSTALL_FFMPEG_WINDOWS.txt")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
