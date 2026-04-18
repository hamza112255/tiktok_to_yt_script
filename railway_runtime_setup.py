"""
Railway-specific setup script.
Decodes credentials and merges environment overrides into config.json.
"""

import base64
import json
import os
import sys
from pathlib import Path


def _env_text(name):
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def _env_bool(name):
    value = _env_text(name)
    if value is None:
        return None
    return value.lower() in {'1', 'true', 'yes', 'on'}


def _env_int(name):
    value = _env_text(name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        print(f"Warning: Invalid integer for {name}: {value}")
        return None


def _decode_file_from_env(env_name, output_path):
    payload = os.getenv(env_name)
    if not payload:
        return

    try:
        decoded = base64.b64decode(payload).decode('utf-8')
        Path(output_path).write_text(decoded, encoding='utf-8')
        print(f"✓ {output_path} created from environment variable")
    except Exception as e:
        print(f"Warning: Failed to decode {env_name}: {e}")


def _load_base_config():
    for config_name in ('config.json', 'config.defaults.json'):
        config_path = Path(config_name)
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding='utf-8'))
                print(f"✓ Loaded base {config_name} from repository")
                return config
            except Exception as e:
                print(f"Warning: Could not read {config_name}: {e}")

    return {
        "tiktok_username": "username",
        "check_interval_minutes": 5,
        "youtube_settings": {
            "channel_name": "My YouTube Channel",
            "shorts_folder": "youtube_ready/shorts",
            "main_videos_folder": "youtube_ready/main",
            "auto_organize": True,
            "organize_by_date": False,
            "auto_upload_to_youtube": False,
            "always_prompt_account": False,
            "title_suffix": " | TikTok",
            "use_tiktok_hashtags": False,
            "skip_copyrighted": True,
            "skip_non_original_audio": True,
            "copyright_keywords": ["copyright", "all rights reserved", "(c)"],
            "copyright_risk_action": "private",
            "copyright_risk_privacy": "private",
            "upload_as_shorts": True,
            "video_privacy": "public",
            "default_title_prefix": "",
            "default_description": "#shorts #tiktok",
            "add_watermark": False,
            "watermark_text": "Lahori Twins",
            "skip_female_videos": False,
            "split_long_videos": False,
            "split_duration_seconds": 30,
            "min_segment_duration_seconds": 20
        },
        "download_settings": {
            "video_quality": "high",
            "remove_watermark": True,
            "save_video_info": True,
            "download_latest_only": True,
            "max_videos_per_check": 1
        },
        "notifications": {
            "show_download_progress": True,
            "play_sound_on_new_video": False
        },
        "auto_restart": {
            "enabled": True,
            "restart_on_error": True,
            "max_retries": 999999
        }
    }


def _ensure_section(config, name):
    section = config.get(name)
    if not isinstance(section, dict):
        section = {}
        config[name] = section
    return section


def _set_if_provided(mapping, key, value):
    if value is not None:
        mapping[key] = value


def setup_runtime_config():
    """Decode credentials and build effective config.json."""
    # Support both old and new variable names
    _decode_file_from_env('YOUTUBE_CLIENT_SECRET_B64', 'client_secret.json')
    if not Path('client_secret.json').exists():
        _decode_file_from_env('CLIENT_SECRET_B64', 'client_secret.json')
    
    _decode_file_from_env('YOUTUBE_TOKEN_JSON', 'token.json')
    if not Path('token.json').exists():
        _decode_file_from_env('TOKEN_B64', 'token.json')

    config = _load_base_config()
    youtube_settings = _ensure_section(config, 'youtube_settings')
    download_settings = _ensure_section(config, 'download_settings')
    notifications = _ensure_section(config, 'notifications')
    auto_restart = _ensure_section(config, 'auto_restart')

    _set_if_provided(config, 'tiktok_username', _env_text('TIKTOK_USERNAME'))
    _set_if_provided(config, 'check_interval_minutes', _env_int('CHECK_INTERVAL_MINUTES'))

    _set_if_provided(youtube_settings, 'channel_name', _env_text('YOUTUBE_CHANNEL_NAME'))
    _set_if_provided(youtube_settings, 'shorts_folder', _env_text('SHORTS_FOLDER'))
    _set_if_provided(youtube_settings, 'main_videos_folder', _env_text('MAIN_VIDEOS_FOLDER'))
    _set_if_provided(youtube_settings, 'auto_upload_to_youtube', _env_bool('AUTO_UPLOAD_TO_YOUTUBE'))
    _set_if_provided(youtube_settings, 'title_suffix', _env_text('TITLE_SUFFIX'))
    _set_if_provided(youtube_settings, 'use_tiktok_hashtags', _env_bool('USE_TIKTOK_HASHTAGS'))
    _set_if_provided(youtube_settings, 'skip_copyrighted', _env_bool('SKIP_COPYRIGHTED'))
    _set_if_provided(youtube_settings, 'skip_non_original_audio', _env_bool('SKIP_NON_ORIGINAL_AUDIO'))
    _set_if_provided(youtube_settings, 'copyright_risk_action', _env_text('COPYRIGHT_RISK_ACTION'))
    _set_if_provided(youtube_settings, 'copyright_risk_privacy', _env_text('COPYRIGHT_RISK_PRIVACY'))
    _set_if_provided(youtube_settings, 'video_privacy', _env_text('VIDEO_PRIVACY'))
    _set_if_provided(youtube_settings, 'default_title_prefix', _env_text('DEFAULT_TITLE_PREFIX'))
    _set_if_provided(youtube_settings, 'default_description', _env_text('DEFAULT_DESCRIPTION'))
    _set_if_provided(youtube_settings, 'add_watermark', _env_bool('ADD_WATERMARK'))
    _set_if_provided(youtube_settings, 'watermark_text', _env_text('WATERMARK_TEXT'))
    _set_if_provided(youtube_settings, 'skip_female_videos', _env_bool('SKIP_FEMALE_VIDEOS'))
    _set_if_provided(youtube_settings, 'split_long_videos', _env_bool('SPLIT_LONG_VIDEOS'))
    _set_if_provided(youtube_settings, 'split_duration_seconds', _env_int('SPLIT_DURATION_SECONDS'))
    _set_if_provided(youtube_settings, 'min_segment_duration_seconds', _env_int('MIN_SEGMENT_DURATION_SECONDS'))
    _set_if_provided(youtube_settings, 'organize_by_date', _env_bool('ORGANIZE_BY_DATE'))

    _set_if_provided(download_settings, 'download_latest_only', _env_bool('DOWNLOAD_LATEST_ONLY'))
    _set_if_provided(download_settings, 'max_videos_per_check', _env_int('MAX_VIDEOS_PER_CHECK'))
    _set_if_provided(download_settings, 'remove_watermark', _env_bool('REMOVE_WATERMARK'))
    _set_if_provided(download_settings, 'save_video_info', _env_bool('SAVE_VIDEO_INFO'))

    _set_if_provided(notifications, 'show_download_progress', _env_bool('SHOW_DOWNLOAD_PROGRESS'))
    _set_if_provided(notifications, 'play_sound_on_new_video', _env_bool('PLAY_SOUND_ON_NEW_VIDEO'))

    _set_if_provided(auto_restart, 'enabled', _env_bool('AUTO_RESTART_ENABLED'))
    _set_if_provided(auto_restart, 'restart_on_error', _env_bool('RESTART_ON_ERROR'))
    _set_if_provided(auto_restart, 'max_retries', _env_int('MAX_RETRIES'))

    Path('config.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
    print("✓ config.json created from base config and environment variables")


if __name__ == '__main__':
    print("-> Setting up Railway environment...")
    setup_runtime_config()
    print("✓ Railway setup complete")
    print("-> Starting main script...")
    sys.stdout.flush()
