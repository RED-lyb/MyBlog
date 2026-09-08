"""
同频影院：片库目录、MediaMTX 推流进程管理
"""
import json
import os
import re
import signal
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from history.views import admin_required

from .cinema_log import cinema_log
from .mediamtx_config import (
    ALLOWED_CINEMA_VIDEO_EXT,
    BLOG_LOG_FILE,
    CINEMA_DIR,
    LOG_DIR,
    MAX_CINEMA_VIDEO_BYTES,
    MEDIAMTX_BINARY,
    MEDIAMTX_CONFIG_FILE,
    MEDIAMTX_PID_FILE,
    MEDIAMTX_RUNTIME_DIR,
    STREAM_PID_FILE,
    STREAM_STATE_FILE,
    STREAM_RUNTIME_DIR,
    build_admin_config_payload,
    build_playback_payload,
    get_mediamtx_settings,
    save_admin_config,
)


def _success(data=None, message='ok'):
    return JsonResponse({'success': True, 'data': data, 'message': message})


def _error(message, code=400, extra=None):
    body = {'success': False, 'error': message}
    if extra:
        body.update(extra)
    return JsonResponse(body, status=code)


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


_MEDIAMTX_PROXY_OPENER = urllib.request.build_opener(_NoRedirectHandler)


def _rewrite_mediamtx_location(location, upstream_origin, proxy_prefix):
    if not location:
        return location
    if location.startswith(upstream_origin):
        return f'{proxy_prefix}{location[len(upstream_origin):]}'
    if location.startswith('/'):
        return f'{proxy_prefix}{location}'
    return location


def _header_values(headers, name):
    if hasattr(headers, 'get_all'):
        values = headers.get_all(name)
        if values:
            return values
    value = headers.get(name)
    return [value] if value else []


def _copy_mediamtx_proxy_headers(upstream, response, mtx):
    upstream_origin = f'http://127.0.0.1:{mtx["webrtc_port"]}'
    proxy_prefix = '/api/cinema/mtx/webrtc'

    content_type = upstream.headers.get('Content-Type')
    if content_type:
        response['Content-Type'] = content_type

    for header in ('Cache-Control', 'ETag', 'ID', 'Accept-Patch'):
        value = upstream.headers.get(header)
        if value:
            response[header] = value

    link_values = _header_values(upstream.headers, 'Link')
    if link_values:
        response['Link'] = ', '.join(link_values)

    location = upstream.headers.get('Location')
    if location:
        response['Location'] = _rewrite_mediamtx_location(
            location, upstream_origin, proxy_prefix,
        )

    response['Access-Control-Expose-Headers'] = (
        'Location, Link, ETag, ID, Accept-Patch'
    )


def _proxy_request_headers(request):
    headers = {}
    content_type = request.META.get('CONTENT_TYPE') or request.META.get('HTTP_CONTENT_TYPE')
    if content_type:
        headers['Content-Type'] = content_type

    for name in ('Authorization', 'If-Match', 'Accept', 'Cookie'):
        value = request.META.get(f'HTTP_{name.upper().replace("-", "_")}')
        if value:
            headers[name] = value
    return headers


def _mediamtx_proxy(request, subpath):
    mtx = get_mediamtx_settings()
    target = f'http://127.0.0.1:{mtx["webrtc_port"]}/{subpath}'
    query = request.META.get('QUERY_STRING')
    if query:
        target += f'?{query}'

    headers = _proxy_request_headers(request)
    body = None
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        body = request.body or None

    upstream_req = urllib.request.Request(
        target,
        data=body,
        headers=headers,
        method=request.method,
    )

    try:
        with _MEDIAMTX_PROXY_OPENER.open(upstream_req, timeout=60) as upstream_resp:
            payload = upstream_resp.read()
            response = HttpResponse(payload, status=upstream_resp.status)
            _copy_mediamtx_proxy_headers(upstream_resp, response, mtx)
            return response
    except urllib.error.HTTPError as exc:
        payload = exc.read() if exc.fp is not None else b''
        response = HttpResponse(payload, status=exc.code)
        _copy_mediamtx_proxy_headers(exc, response, mtx)
        return response
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        cinema_log(f'mediamtx proxy error: {exc}')
        return HttpResponse(str(exc), status=502, content_type='text/plain')


@csrf_exempt
@require_http_methods(['GET', 'HEAD', 'OPTIONS', 'POST', 'PATCH', 'DELETE'])
def mediamtx_webrtc_proxy(request, subpath):
    return _mediamtx_proxy(request, subpath)


def _safe_cinema_filename(name):
    if not name or not isinstance(name, str):
        return None
    base = os.path.basename(name.strip())
    if not base or base in ('.', '..') or '..' in name:
        return None
    lower = base.lower()
    if not any(lower.endswith(ext) for ext in ALLOWED_CINEMA_VIDEO_EXT):
        return None
    return base


def _cinema_file_path(filename):
    safe = _safe_cinema_filename(filename)
    if not safe:
        return None
    path = (CINEMA_DIR / safe).resolve()
    if path.parent != CINEMA_DIR.resolve():
        return None
    return path


def _scan_cinema_files():
    CINEMA_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for path in sorted(CINEMA_DIR.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWED_CINEMA_VIDEO_EXT:
            continue
        stat = path.stat()
        items.append({
            'filename': path.name,
            'title': path.stem,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(timespec='seconds'),
            'static_url': f'{settings.STATIC_URL}cinema/{path.name}',
        })
    return items


def _read_stream_state():
    if not STREAM_STATE_FILE.is_file():
        return {}
    try:
        with open(STREAM_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _write_stream_state(state):
    STREAM_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with open(STREAM_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _read_pid(pid_file):
    if not pid_file.is_file():
        return None
    try:
        raw = pid_file.read_text(encoding='utf-8').strip()
        return int(raw) if raw else None
    except Exception:
        return None


def _proc_state(pid):
    try:
        with open(f'/proc/{pid}/status', encoding='utf-8') as f:
            for line in f:
                if line.startswith('State:'):
                    return line.split()[1]
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return None
    return None


def _reap_process(pid):
    if not pid or pid <= 0:
        return
    try:
        while True:
            wpid, _ = os.waitpid(pid, os.WNOHANG)
            if wpid in (0, pid):
                break
    except ChildProcessError:
        pass
    except OSError:
        pass


def _is_process_running(pid):
    if not pid or pid <= 0:
        return False
    state = _proc_state(pid)
    if state is None:
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True
    if state == 'Z':
        _reap_process(pid)
        return False
    return True


def _clear_pid_file(pid_file):
    if pid_file.is_file():
        try:
            pid_file.unlink()
        except OSError:
            pass


def _mark_stream_stopped(state=None):
    state = dict(state or _read_stream_state())
    if state.get('running'):
        state['running'] = False
        state['stopped_at'] = datetime.now().isoformat(timespec='seconds')
        _write_stream_state(state)
    else:
        state['running'] = False
        _write_stream_state(state)


def _reconcile_ffmpeg_state():
    pid = _read_pid(STREAM_PID_FILE)
    if pid and _is_process_running(pid):
        return pid, True

    had_pid = pid is not None
    if pid:
        cinema_log(f'ffmpeg pid={pid} exited, stream ended')
        _reap_process(pid)
    _clear_pid_file(STREAM_PID_FILE)
    if had_pid:
        _mark_stream_stopped()
    return None, False


def _kill_ffmpeg_publish():
    pid = _read_pid(STREAM_PID_FILE)
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
        _reap_process(pid)

    mtx = get_mediamtx_settings()
    pattern = f'ffmpeg.*{re.escape(mtx["rtsp_publish_url"])}'
    subprocess.run(
        ['pkill', '-f', pattern],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        check=False,
    )
    time.sleep(0.05)


def _stop_ffmpeg_publish():
    cinema_log('stop ffmpeg publish')
    _kill_ffmpeg_publish()
    _clear_pid_file(STREAM_PID_FILE)
    state = _read_stream_state()
    if state.get('running'):
        state['running'] = False
        state['stopped_at'] = datetime.now().isoformat(timespec='seconds')
        _write_stream_state(state)
    else:
        _mark_stream_stopped()


def _mediamtx_path_online(mtx, timeout=6.0):
    """等待 mediamtx 路径上有推流源（ffmpeg 已连上）"""
    url = f'{mtx["api_url"]}/v3/paths/get/{mtx["path_name"]}'
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get('online') or data.get('ready'):
                    tracks = []
                    source = data.get('source') or {}
                    for track in source.get('tracks') or []:
                        tracks.append(track.get('type') or track.get('codec') or str(track))
                    cinema_log(
                        f'mediamtx path online: tracks={tracks or "unknown"} '
                        f'bytesReceived={source.get("bytesReceived")}'
                    )
                    return True, data
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            cinema_log(f'mediamtx path poll: {exc}')
        time.sleep(0.15)
    cinema_log(f'mediamtx path online timeout after {timeout}s')
    return False, None


def _ffprobe_bin(ffmpeg_bin):
    if ffmpeg_bin.endswith('ffmpeg'):
        candidate = f'{ffmpeg_bin[:-6]}ffprobe'
        if os.path.isfile(candidate):
            return candidate
    return 'ffprobe'


def _probe_video_codec(cinema_path, ffmpeg_bin):
    try:
        result = subprocess.run(
            [
                _ffprobe_bin(ffmpeg_bin),
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name',
                '-of', 'csv=p=0',
                str(cinema_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        return result.stdout.strip().lower()
    except Exception:
        return ''


def _video_encode_args(ffmpeg_bin, cinema_path):
    if _probe_video_codec(cinema_path, ffmpeg_bin) == 'h264':
        return ['-c:v', 'copy']
    return [
        '-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'zerolatency',
        '-g', '30', '-keyint_min', '30', '-sc_threshold', '0', '-bf', '0',
        '-force_key_frames', 'expr:gte(t,n_forced*1)',
    ]


def _build_ffmpeg_cmd(mtx, cinema_path):
    """立即以 1x 推原始片源；H.264 直拷，音频转 Opus。"""
    return [
        mtx['ffmpeg_bin'],
        '-nostdin',
        '-hide_banner',
        '-loglevel', 'info',
        '-re',
        '-i', str(cinema_path.resolve()),
        *_video_encode_args(mtx['ffmpeg_bin'], cinema_path),
        '-c:a', 'libopus', '-ar', '48000', '-ac', '2',
        '-application', 'lowdelay', '-b:a', '96k',
        '-f', 'rtsp', '-rtsp_transport', 'tcp',
        mtx['rtsp_publish_url'],
    ]


def _launch_ffmpeg_push(mtx, cinema_path):
    ffmpeg_cmd = _build_ffmpeg_cmd(mtx, cinema_path)
    cinema_log('ffmpeg cmd: ' + ' '.join(ffmpeg_cmd))

    STREAM_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_file = open(BLOG_LOG_FILE, 'a', encoding='utf-8')
    log_file.write(f'\n[{datetime.now().isoformat(timespec="seconds")}] [ffmpeg] process start\n')
    try:
        proc = subprocess.Popen(
            ffmpeg_cmd,
            cwd=str(STREAM_RUNTIME_DIR),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    finally:
        log_file.close()

    if proc.poll() is not None:
        cinema_log('ffmpeg exited immediately after start', tag='ffmpeg')
        return None, False

    t0 = time.time()
    path_ready, _path_data = _mediamtx_path_online(mtx)
    cinema_log(
        f'ffmpeg pid={proc.pid} path_ready={path_ready} '
        f'wait_ms={int((time.time() - t0) * 1000)}'
    )

    STREAM_PID_FILE.write_text(str(proc.pid), encoding='utf-8')
    return proc.pid, path_ready


def _mediamtx_binary_path():
    return MEDIAMTX_BINARY if MEDIAMTX_BINARY.is_file() else None


def _is_mediamtx_running():
    pid = _read_pid(MEDIAMTX_PID_FILE)
    if pid and _is_process_running(pid):
        return True, pid

    mtx = get_mediamtx_settings()
    try:
        req = urllib.request.Request(
            f'{mtx["api_url"]}/v3/config/global/get',
            method='GET',
        )
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                return True, pid
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        pass

    if pid:
        _reap_process(pid)
    _clear_pid_file(MEDIAMTX_PID_FILE)
    return False, None


def _start_mediamtx():
    running, pid = _is_mediamtx_running()
    if running:
        return True, pid, ''

    exe = _mediamtx_binary_path()
    if not exe:
        return False, None, '未找到 mediamtx 可执行文件，请运行 deploy_mediamtx.sh'

    if not MEDIAMTX_CONFIG_FILE.is_file():
        return False, None, f'未找到配置文件: {MEDIAMTX_CONFIG_FILE}'

    MEDIAMTX_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    cinema_log('mediamtx starting')
    log_file = open(BLOG_LOG_FILE, 'a', encoding='utf-8')
    log_file.write(f'\n[{datetime.now().isoformat(timespec="seconds")}] [mediamtx] process start\n')
    try:
        proc = subprocess.Popen(
            [str(exe), str(MEDIAMTX_CONFIG_FILE.resolve())],
            cwd=str(MEDIAMTX_RUNTIME_DIR),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    finally:
        log_file.close()

    if proc.poll() is not None:
        return False, None, 'mediamtx 启动失败，请查看 log/back.log'

    MEDIAMTX_PID_FILE.write_text(str(proc.pid), encoding='utf-8')
    for _ in range(30):
        time.sleep(0.1)
        if _is_mediamtx_running()[0]:
            return True, proc.pid, ''
        if proc.poll() is not None:
            return False, None, 'mediamtx 启动后退出，请查看 log/back.log'

    return False, None, 'mediamtx 启动超时，请查看 log/back.log'


def _runtime_ready():
    if not _mediamtx_binary_path():
        return False, '未找到 mediamtx，请运行 back/cinema/scripts/deploy_mediamtx.sh'
    return True, ''


def _stream_payload(state, pid, session_running, pushing, mtx):
    return {
        'running': session_running,
        'pushing': pushing,
        'pid': pid if pushing else None,
        'path_name': mtx['path_name'],
        'cinema_filename': state.get('cinema_filename'),
        'started_at': state.get('started_at'),
        'playback': build_playback_payload(mtx),
    }


def _get_stream_status():
    state = _read_stream_state()
    pid, pushing = _reconcile_ffmpeg_state()
    session_running = bool(state.get('running'))
    mtx = get_mediamtx_settings()
    if pushing:
        pid = pid or _read_pid(STREAM_PID_FILE)
    return state, pid, session_running, pushing, mtx


@require_GET
def cinema_list(request):
    cinema_files = _scan_cinema_files()
    state, pid, session_running, pushing, mtx = _get_stream_status()
    mediamtx_running, _ = _is_mediamtx_running()
    return _success({
        'cinema': cinema_files,
        'stream': _stream_payload(state, pid, session_running, pushing, mtx),
        'mediamtx_running': mediamtx_running,
    })


@require_GET
def stream_status(request):
    state, pid, session_running, pushing, mtx = _get_stream_status()
    mediamtx_running, mediamtx_pid = _is_mediamtx_running()
    payload = _stream_payload(state, pid, session_running, pushing, mtx)
    payload['mediamtx_running'] = mediamtx_running
    payload['mediamtx_pid'] = mediamtx_pid
    payload['mediamtx_ready'] = _mediamtx_binary_path() is not None
    return _success(payload)


@require_GET
@admin_required
def admin_cinema_list(request):
    return cinema_list(request)


@csrf_exempt
@require_POST
@admin_required
def admin_upload_cinema(request):
    CINEMA_DIR.mkdir(parents=True, exist_ok=True)
    upload = request.FILES.get('file')
    if not upload:
        return _error('请上传视频文件')

    safe = _safe_cinema_filename(upload.name)
    if not safe:
        return _error('仅支持 .mp4 文件')

    if upload.size > MAX_CINEMA_VIDEO_BYTES:
        return _error('文件过大')

    dest = CINEMA_DIR / safe
    with open(dest, 'wb') as out:
        for chunk in upload.chunks():
            out.write(chunk)

    return _success({'filename': safe, 'cinema': _scan_cinema_files()}, '上传成功')


@csrf_exempt
@require_http_methods(['DELETE', 'POST'])
@admin_required
def admin_delete_cinema(request, filename):
    path = _cinema_file_path(filename)
    if not path or not path.is_file():
        return _error('影片不存在', 404)

    state, _, running, _, _ = _get_stream_status()
    if state.get('cinema_filename') == path.name and running:
        return _error('该影片正在放映中，请先停止推流')

    path.unlink()
    return _success({'cinema': _scan_cinema_files()}, '已删除')


@csrf_exempt
@require_POST
@admin_required
def admin_start_stream(request):
    ok, msg = _runtime_ready()
    if not ok:
        return _error(msg, 400)

    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        body = {}

    cinema_filename = body.get('cinema_filename') or body.get('filename')
    if not cinema_filename:
        return _error('请指定 cinema_filename')

    cinema_path = _cinema_file_path(cinema_filename)
    if not cinema_path or not cinema_path.is_file():
        return _error('影片文件不存在', 404)

    mtx = get_mediamtx_settings()
    started, mediamtx_pid, start_err = _start_mediamtx()
    if not started:
        return _error(start_err or 'mediamtx 启动失败', 500)

    _stop_ffmpeg_publish()
    cinema_log(f'--- start stream: {cinema_path.name} ---')

    pid, path_ready = _launch_ffmpeg_push(mtx, cinema_path)
    if not pid:
        _mark_stream_stopped()
        return _error('ffmpeg 推流启动失败，请查看 log/back.log', 500)

    state = {
        'running': True,
        'pid': pid,
        'path_name': mtx['path_name'],
        'cinema_filename': cinema_path.name,
        'started_at': datetime.now().isoformat(timespec='seconds'),
        'push_started_at': datetime.now().isoformat(timespec='seconds'),
    }
    _write_stream_state(state)
    cinema_log(f'session started, ffmpeg pid={pid} path_ready={path_ready}')

    return _success({
        'running': True,
        'pushing': True,
        'pid': pid,
        'mediamtx_pid': mediamtx_pid,
        'path_name': mtx['path_name'],
        'cinema_filename': cinema_path.name,
        'playback': build_playback_payload(mtx),
        'started_at': state['started_at'],
        'log_file': str(BLOG_LOG_FILE),
    }, '推流已开始')


@csrf_exempt
@require_POST
@admin_required
def admin_stop_stream(request):
    _stop_ffmpeg_publish()
    return _success({'running': False}, '推流已停止')


@require_GET
@admin_required
def admin_runtime_info(request):
    exe = _mediamtx_binary_path()
    mtx = get_mediamtx_settings()
    _, pid, running, pushing, mtx = _get_stream_status()
    mediamtx_running, mediamtx_pid = _is_mediamtx_running()
    return _success({
        'mediamtx_runtime_dir': str(MEDIAMTX_RUNTIME_DIR),
        'mediamtx_binary_exists': exe is not None,
        'mediamtx_binary_path': str(exe) if exe else None,
        'mediamtx_config': str(MEDIAMTX_CONFIG_FILE),
        'mediamtx_running': mediamtx_running,
        'mediamtx_pid': mediamtx_pid,
        'cinema_dir': str(CINEMA_DIR),
        'stream_running': running,
        'stream_pushing': pushing,
        'ffmpeg_pid': pid if pushing else None,
        'rtsp_publish_url': mtx['rtsp_publish_url'],
        'playback': build_playback_payload(mtx),
        'log_file': str(BLOG_LOG_FILE),
    })


@csrf_exempt
@require_http_methods(['GET', 'PUT'])
@admin_required
def admin_cinema_config(request):
    if request.method == 'GET':
        try:
            return _success(build_admin_config_payload())
        except (OSError, ValueError, yaml.YAMLError) as exc:
            return _error(f'读取配置失败: {exc}', 500)

    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _error('请求体不是有效 JSON')

    try:
        payload = save_admin_config(body)
    except ValueError as exc:
        return _error(str(exc))
    except (OSError, yaml.YAMLError) as exc:
        return _error(f'保存配置失败: {exc}', 500)

    cinema_log('cinema config updated from admin')
    return _success(payload, '配置已保存')
