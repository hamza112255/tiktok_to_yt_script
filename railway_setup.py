"""
Railway-specific setup script
Handles environment variable decoding and configuration
"""
import os
import base64
import json
from pathlib import Path

# Check if we have a persistent volume mounted
DATA_DIR = Path('/app/data') if Path('/app/data').exists() else Path('.')

def setup_credentials():
    """Decode base64 credentials from environment variables"""
    
    # Decode client_secret.json
    client_secret_b64 = os.getenv('CLIENT_SECRET_B64')
    if client_secret_b64:
        try:
            client_secret = base64.b64decode(client_secret_b64).decode('utf-8')
            with open('client_secret.json', 'w') as f:
                f.write(client_secret)
            print("✓ client_secret.json created from environment variable")
        except Exception as e:
            print(f"⚠ Failed to decode CLIENT_SECRET_B64: {e}")
    
    # Decode token.json
    token_b64 = os.getenv('TOKEN_B64')
    if token_b64:
        try:
            token = base64.b64decode(token_b64).decode('utf-8')
            with open('token.json', 'w') as f:
                f.write(token)
            print("✓ token.json created from environment variable")
        except Exception as e:
            print(f"⚠ Failed to decode TOKEN_B64: {e}")
    
    # Create config.json from environment variables
    config = {
        "tiktok_username": os.getenv('TIKTOK_USERNAME', 'username'),
        "check_interval_minutes": int(os.getenv('CHECK_INTERVAL_MINUTES', '5')),
        "youtube_settings": {
            "channel_name": os.getenv('YOUTUBE_CHANNEL_NAME', 'My YouTube Channel'),
            "shorts_folder": "youtube_ready/shorts",
            "main_videos_folder": "youtube_ready/main",
            "auto_organize": True,
            "auto_upload_to_youtube": os.getenv('AUTO_UPLOAD_TO_YOUTUBE', 'false').lower() == 'true',
            "always_prompt_account": False,
            "title_suffix": os.getenv('TITLE_SUFFIX', ' | TikTok'),
            "use_tiktok_hashtags": os.getenv('USE_TIKTOK_HASHTAGS', 'false').lower() == 'true',
            "skip_copyrighted": True,
            "skip_non_original_audio": True,
            "copyright_keywords": ["copyright", "all rights reserved", "(c)"],
            "upload_as_shorts": True,
            "video_privacy": os.getenv('VIDEO_PRIVACY', 'private'),
            "default_title_prefix": "",
            "default_description": "#shorts #tiktok",
            "add_watermark": os.getenv('ADD_WATERMARK', 'false').lower() == 'true',
            "watermark_text": os.getenv('WATERMARK_TEXT', 'Lahori Twins'),
            "skip_female_videos": False,  # Disabled on Railway (requires heavy AI models)
            "split_long_videos": os.getenv('SPLIT_LONG_VIDEOS', 'false').lower() == 'true',
            "split_duration_seconds": int(os.getenv('SPLIT_DURATION_SECONDS', '30')),
            "min_segment_duration_seconds": int(os.getenv('MIN_SEGMENT_DURATION_SECONDS', '20'))
        },
        "download_settings": {
            "video_quality": "high",
            "remove_watermark": True,
            "save_video_info": True
        },
        "notifications": {
            "show_download_progress": True,
            "play_sound_on_new_video": False
        }
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print("✓ config.json created from environment variables")

if __name__ == '__main__':
    print("→ Setting up Railway environment...")
    setup_credentials()
    print("✓ Railway setup complete")
    print("→ Starting main script...")
    import sys
    sys.stdout.flush()
