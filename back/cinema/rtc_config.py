"""同频影院 RTC 配置与路径"""
from pathlib import Path

from django.conf import settings

from common.config_utils import CINEMA_VIDEO_ENCODER_DEFAULT, load_config

BASE_DIR = Path(settings.BASE_DIR)
BLOG_ROOT = BASE_DIR.parent
CINEMA_DIR = BASE_DIR / 'api' / 'static' / 'cinema'
RTC_RUNTIME_DIR = BASE_DIR / 'cinema' / 'rtc_runtime'
BLOG_CONFIG_FILE = BASE_DIR / 'config' / 'config_back.json'
LOG_DIR = BLOG_ROOT / 'log'
BLOG_LOG_FILE = LOG_DIR / 'back.log'
STREAM_PID_FILE = RTC_RUNTIME_DIR / 'stream.pid'
STREAM_STATE_FILE = RTC_RUNTIME_DIR / 'stream_state.json'

ALLOWED_CINEMA_VIDEO_EXT = ('.mp4',)
MAX_CINEMA_VIDEO_BYTES = 3 * 1024 * 1024 * 1024  # 3GB


def get_rtc_settings():
    cfg = load_config().get('rtc', {})
    return {
        'app_id': (cfg.get('app_id') or '').strip(),
        'app_key': (cfg.get('app_key') or '').strip(),
        'expire_ts': int(cfg.get('expire_ts', 168)),
        'default_room_id': (cfg.get('default_room_id') or 'cinema_room').strip(),
        'default_user_id': (cfg.get('default_user_id') or 'cinema_publisher').strip(),
        'token_server_host': (cfg.get('token_server_host') or '127.0.0.1').strip(),
        'token_server_port': int(cfg.get('token_server_port', 8000)),
        'token_server_path': (cfg.get('token_server_path') or '/api/cinema/get/token').strip(),
        'rtc_env': int(cfg.get('rtc_env', 0)),
        'enable_video': bool(cfg.get('enable_video', True)),
        'enable_audio': bool(cfg.get('enable_audio', True)),
        'video_encoder_config': cfg.get('video_encoder_config') or dict(CINEMA_VIDEO_ENCODER_DEFAULT),
    }
