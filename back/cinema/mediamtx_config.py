"""同频影院 MediaMTX 配置与路径"""
import json
import re
from pathlib import Path

import yaml
from django.conf import settings

from common.config_utils import get_config_path, load_config

BASE_DIR = Path(settings.BASE_DIR)
BLOG_ROOT = BASE_DIR.parent
CINEMA_DIR = BASE_DIR / 'api' / 'static' / 'cinema'
MEDIAMTX_DIR = BASE_DIR / 'cinema' / 'mediamtx'
MEDIAMTX_CONFIG_FILE = MEDIAMTX_DIR / 'cinema.yml'
MEDIAMTX_RUNTIME_DIR = BASE_DIR / 'cinema' / 'mediamtx_runtime'
MEDIAMTX_BINARY = MEDIAMTX_RUNTIME_DIR / 'mediamtx'
MEDIAMTX_PID_FILE = MEDIAMTX_RUNTIME_DIR / 'mediamtx.pid'
STREAM_RUNTIME_DIR = BASE_DIR / 'cinema' / 'stream_runtime'
STREAM_PID_FILE = STREAM_RUNTIME_DIR / 'ffmpeg.pid'
STREAM_STATE_FILE = STREAM_RUNTIME_DIR / 'stream_state.json'
LOG_DIR = BLOG_ROOT / 'log'
BLOG_LOG_FILE = LOG_DIR / 'back.log'

ALLOWED_CINEMA_VIDEO_EXT = ('.mp4',)
MAX_CINEMA_VIDEO_BYTES = 3 * 1024 * 1024 * 1024  # 3GB

PATH_NAME = 'cinema'
DEFAULT_RTSP_ADDRESS = '127.0.0.1:8554'
DEFAULT_API_ADDRESS = '127.0.0.1:9997'
DEFAULT_WEBRTC_HTTP_ADDRESS = '127.0.0.1:8889'
WEBRTC_UDP_ADDRESS = ':8189'
ADDRESS_RE = re.compile(
    r'^(?:(?:\[[0-9a-fA-F:]+\]|[0-9A-Za-z._-]+)?):(\d{1,5})$'
)


def _as_str_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        parts = [item.strip() for item in value.replace(';', ',').split(',')]
        return [item for item in parts if item]
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _split_hostport(address, default_host='127.0.0.1', default_port=0):
    text = (address or '').strip()
    if not text:
        return default_host, default_port
    if text.startswith('['):
        end = text.find(']')
        host = text[1:end] if end > 0 else default_host
        rest = text[end + 1:] if end > 0 else ''
        port = int(rest[1:]) if rest.startswith(':') and rest[1:].isdigit() else default_port
        return host or default_host, port
    if text.startswith(':'):
        return default_host, int(text[1:]) if text[1:].isdigit() else default_port
    if ':' in text:
        host, _, port_text = text.rpartition(':')
        port = int(port_text) if port_text.isdigit() else default_port
        return (host or default_host), port
    return text, default_port


def _connect_host(bind_host):
    if bind_host in ('', '0.0.0.0', '::', '[::]'):
        return '127.0.0.1'
    return bind_host


def validate_address(value, label):
    text = (value or '').strip()
    matched = ADDRESS_RE.match(text)
    if not matched:
        raise ValueError(f'{label} 格式应为 host:port 或 :port')
    port = int(matched.group(1))
    if port < 1 or port > 65535:
        raise ValueError(f'{label} 端口无效')
    return text


def load_cinema_yml():
    if not MEDIAMTX_CONFIG_FILE.is_file():
        return {}
    with MEDIAMTX_CONFIG_FILE.open('r', encoding='utf-8') as fh:
        data = yaml.safe_load(fh) or {}
    return data if isinstance(data, dict) else {}


def parse_server_settings(yml=None):
    data = yml if yml is not None else load_cinema_yml()
    return {
        'log_level': str(data.get('logLevel') or 'info').strip() or 'info',
        'rtsp_address': str(data.get('rtspAddress') or DEFAULT_RTSP_ADDRESS).strip()
        or DEFAULT_RTSP_ADDRESS,
        'api_address': str(data.get('apiAddress') or DEFAULT_API_ADDRESS).strip()
        or DEFAULT_API_ADDRESS,
        'webrtc_address': str(data.get('webrtcAddress') or DEFAULT_WEBRTC_HTTP_ADDRESS).strip()
        or DEFAULT_WEBRTC_HTTP_ADDRESS,
        'webrtc_additional_hosts': _as_str_list(data.get('webrtcAdditionalHosts')),
    }


def dump_cinema_yml(server):
    data = {
        'logLevel': server.get('log_level') or 'info',
        'logDestinations': ['stdout'],
        'api': True,
        'apiAddress': server.get('api_address') or DEFAULT_API_ADDRESS,
        'rtsp': True,
        'rtspAddress': server.get('rtsp_address') or DEFAULT_RTSP_ADDRESS,
        'hls': False,
        'webrtc': True,
        'webrtcAddress': server.get('webrtc_address') or DEFAULT_WEBRTC_HTTP_ADDRESS,
        'webrtcLocalUDPAddress': WEBRTC_UDP_ADDRESS,
        'webrtcAllowOrigins': ['*'],
        'paths': {
            PATH_NAME: {
                'source': 'publisher',
            },
        },
    }
    hosts = server.get('webrtc_additional_hosts') or []
    if hosts:
        data['webrtcAdditionalHosts'] = hosts

    dumped = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    header = (
        '# 同频影院专用 MediaMTX 配置（由 Django 启动 mediamtx 时加载）\n'
        '# RTSP / API / WebRTC 信令仅监听 127.0.0.1；公网观众通过 Django 代理信令，\n'
        '# 音视频 UDP 走 webrtcLocalUDPAddress（默认 8189），需在 webrtcAdditionalHosts 填公网 IP 或域名。\n'
    )
    return header + dumped


def save_cinema_yml(server):
    MEDIAMTX_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEDIAMTX_CONFIG_FILE.write_text(dump_cinema_yml(server), encoding='utf-8')


def load_app_mediamtx():
    cfg = load_config().get('mediamtx') or {}
    return {
        'prelude_seconds': max(0, int(cfg.get('prelude_seconds', 10))),
        'ffmpeg_bin': (cfg.get('ffmpeg_bin') or 'ffmpeg').strip() or 'ffmpeg',
    }


def save_app_mediamtx(app):
    path = get_config_path()
    if path.is_file():
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            data = {}
    else:
        data = {}
    data['mediamtx'] = {
        'prelude_seconds': max(0, int(app['prelude_seconds'])),
        'ffmpeg_bin': (app.get('ffmpeg_bin') or 'ffmpeg').strip() or 'ffmpeg',
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=4) + '\n',
        encoding='utf-8',
    )


def get_mediamtx_settings():
    app = load_app_mediamtx()
    server = parse_server_settings()
    rtsp_host, rtsp_port = _split_hostport(server['rtsp_address'], '127.0.0.1', 8554)
    api_host, api_port = _split_hostport(server['api_address'], '127.0.0.1', 9997)
    _, webrtc_port = _split_hostport(server['webrtc_address'], '127.0.0.1', 8889)
    return {
        'path_name': PATH_NAME,
        'rtsp_publish_url': f'rtsp://{_connect_host(rtsp_host)}:{rtsp_port}/{PATH_NAME}',
        'prelude_seconds': app['prelude_seconds'],
        'ffmpeg_bin': app['ffmpeg_bin'],
        'api_url': f'http://{_connect_host(api_host)}:{api_port}',
        'webrtc_port': webrtc_port,
    }


def build_playback_payload(mtx):
    """播放地址走 Django 同源代理，避免浏览器无法访问 127.0.0.1:8889。"""
    webrtc_whep_url = f'/api/cinema/mtx/webrtc/{mtx["path_name"]}/whep'
    return {
        'mode': 'webrtc',
        'webrtc_whep_url': webrtc_whep_url,
        'play_url': webrtc_whep_url,
    }


def build_admin_config_payload():
    app = load_app_mediamtx()
    server = parse_server_settings()
    return {
        'app': {
            **app,
            'file': 'back/config/config_back.json',
        },
        'server': {
            **server,
            'file': 'back/cinema/mediamtx/cinema.yml',
        },
    }


def save_admin_config(payload):
    app_in = payload.get('app') or {}
    server_in = payload.get('server') or {}
    current_server = parse_server_settings()
    current_app = load_app_mediamtx()

    prelude_seconds = app_in.get('prelude_seconds', current_app['prelude_seconds'])
    try:
        prelude_seconds = max(0, min(int(prelude_seconds), 120))
    except (TypeError, ValueError) as exc:
        raise ValueError('黑场秒数必须是 0–120 的整数') from exc

    ffmpeg_bin = (app_in.get('ffmpeg_bin') or current_app['ffmpeg_bin']).strip() or 'ffmpeg'
    log_level = str(server_in.get('log_level') or current_server['log_level']).strip() or 'info'
    if log_level not in ('error', 'warn', 'info', 'debug'):
        raise ValueError('日志级别仅支持 error / warn / info / debug')

    additional_hosts = _as_str_list(server_in.get('webrtc_additional_hosts'))
    rtsp_address = validate_address(
        server_in.get('rtsp_address') or current_server['rtsp_address'],
        'RTSP 监听',
    )
    api_address = validate_address(
        server_in.get('api_address') or current_server['api_address'],
        '控制 API',
    )
    webrtc_address = validate_address(
        server_in.get('webrtc_address') or current_server['webrtc_address'],
        'WebRTC 信令',
    )

    app = {
        'prelude_seconds': prelude_seconds,
        'ffmpeg_bin': ffmpeg_bin,
    }
    server = {
        'log_level': log_level,
        'rtsp_address': rtsp_address,
        'api_address': api_address,
        'webrtc_address': webrtc_address,
        'webrtc_additional_hosts': additional_hosts,
    }
    save_app_mediamtx(app)
    save_cinema_yml(server)
    return build_admin_config_payload()
