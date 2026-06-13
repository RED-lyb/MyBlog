"""
同频影院：片库目录、RTC Token、推流进程管理
"""
import json
import os
import re
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from history.views import admin_required

from . import access_token
from .rtc_config import (
    ALLOWED_CINEMA_VIDEO_EXT,
    BLOG_CONFIG_FILE,
    CINEMA_DIR,
    BLOG_LOG_FILE,
    LOG_DIR,
    MAX_CINEMA_VIDEO_BYTES,
    RTC_RUNTIME_DIR,
    STREAM_PID_FILE,
    STREAM_STATE_FILE,
    get_rtc_settings,
)


def _success(data=None, message='ok'):
    return JsonResponse({'success': True, 'data': data, 'message': message})


def _error(message, code=400, extra=None):
    body = {'success': False, 'error': message}
    if extra:
        body.update(extra)
    return JsonResponse(body, status=code)


def _token_response(code=200, message='请求成功', user_id=None, room_id=None, data=None):
    """与 bytedance_server Flask 响应格式一致，供 rtccli 解析"""
    return JsonResponse(
        {
            'user_id': user_id,
            'room_id': room_id,
            'data': data,
            'message': message,
        },
        status=code,
    )


_RTC_USER_ID_RE = re.compile(r'^[0-9a-zA-Z_\-@.]{1,128}$')


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
    RTC_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with open(STREAM_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _read_pid():
    if not STREAM_PID_FILE.is_file():
        return None
    try:
        raw = STREAM_PID_FILE.read_text(encoding='utf-8').strip()
        return int(raw) if raw else None
    except Exception:
        return None


def _proc_state(pid):
    """读取 /proc 进程状态，不存在返回 None。"""
    try:
        with open(f'/proc/{pid}/status', encoding='utf-8') as f:
            for line in f:
                if line.startswith('State:'):
                    return line.split()[1]
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return None
    return None


def _reap_process(pid):
    """回收子进程，避免僵尸进程被误判为仍在推流。"""
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
    """进程存在且非僵尸才算推流中。"""
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


def _kill_all_rtccli():
    """快速结束全部 rtccli，防止残留进程在中途续播。"""
    pid = _read_pid()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    subprocess.run(
        ['pkill', '-9', '-x', 'rtccli'],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        check=False,
    )
    if pid:
        _reap_process(pid)
    time.sleep(0.05)


def _clear_stream_files():
    if STREAM_PID_FILE.is_file():
        try:
            STREAM_PID_FILE.unlink()
        except OSError:
            pass
    lock_file = RTC_RUNTIME_DIR / 'stream.lock'
    if lock_file.is_file():
        try:
            lock_file.unlink()
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


def _reconcile_stream_state():
    """进程已退出但 pid/状态未更新时同步为已停止。"""
    pid = _read_pid()
    if pid and _is_process_running(pid):
        return pid, True

    if pid:
        _reap_process(pid)
    _clear_stream_files()
    _mark_stream_stopped()
    return None, False


def _get_stream_status():
    pid, running = _reconcile_stream_state()
    state = _read_stream_state()
    if running:
        pid = pid or _read_pid()
    return state, pid, running


def _stop_stream_process():
    _kill_all_rtccli()
    _clear_stream_files()
    _mark_stream_stopped()


def _rtccli_path():
    exe = RTC_RUNTIME_DIR / 'rtccli'
    return exe if exe.is_file() else None


def _runtime_ready():
    exe = _rtccli_path()
    if not exe:
        return False, '未找到 rtccli，请编译'
    rtc = get_rtc_settings()
    if not rtc['app_id'] or not rtc['app_key']:
        return False, '请配置 app_id 与 app_key'
    return True, ''


def _stream_payload(state, pid, running, rtc):
    return {
        'running': running,
        'pid': pid if running else None,
        'room_id': state.get('room_id') or rtc['default_room_id'],
        'user_id': state.get('user_id') or rtc['default_user_id'],
        'cinema_filename': state.get('cinema_filename'),
        'app_id': rtc['app_id'],
        'started_at': state.get('started_at'),
    }


@csrf_exempt
@require_POST
def get_token(request):
    """POST /api/cinema/get/token — 与 Flask token 服务兼容"""
    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _token_response(400, '未携带json数据或格式错误')

    user_id = (body.get('user_id') or '').strip()
    room_id = body.get('room_id')
    if not user_id or not room_id:
        return _token_response(400, '未携带json数据或格式错误')
    if not _RTC_USER_ID_RE.fullmatch(user_id):
        return _token_response(400, 'user_id 格式无效')

    rtc = get_rtc_settings()
    if not rtc['app_id'] or not rtc['app_key']:
        return _token_response(500, 'RTC 未配置 app_id / app_key')

    token_str = access_token.create_rtc_token(
        rtc['app_id'],
        rtc['app_key'],
        str(room_id),
        str(user_id),
        rtc['expire_ts'],
    )
    return _token_response(200, '请求成功', user_id, room_id, token_str)


@require_GET
def cinema_list(request):
    cinema_files = _scan_cinema_files()
    state, pid, running = _get_stream_status()
    rtc = get_rtc_settings()
    return _success({
        'cinema': cinema_files,
        'stream': _stream_payload(state, pid, running, rtc),
    })


@require_GET
def stream_status(request):
    state, pid, running = _get_stream_status()
    rtc = get_rtc_settings()
    payload = _stream_payload(state, pid, running, rtc)
    payload['rtc_runtime_ready'] = _rtccli_path() is not None
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

    state, _, running = _get_stream_status()
    if state.get('cinema_filename') == path.name and running:
        return _error('该影片正在推流中，请先停止推流')

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

    rtc = get_rtc_settings()
    room_id = (body.get('room_id') or rtc['default_room_id']).strip()
    user_id = (body.get('user_id') or rtc['default_user_id']).strip()

    name_re = re.compile(r'^[a-zA-Z0-9@._-]{1,128}$')
    if not name_re.match(room_id) or not name_re.match(user_id):
        return _error('room_id / user_id 格式无效（1-128 位字母数字及 @._-）')

    _stop_stream_process()

    RTC_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    exe = _rtccli_path()
    if not BLOG_CONFIG_FILE.is_file():
        return _error(f'未找到博客配置: {BLOG_CONFIG_FILE}', 500)

    log_file = open(BLOG_LOG_FILE, 'a', encoding='utf-8')
    try:
        proc = subprocess.Popen(
            [
                str(exe),
                str(cinema_path.resolve()),
                room_id,
                user_id,
                str(BLOG_CONFIG_FILE.resolve()),
            ],
            cwd=str(RTC_RUNTIME_DIR),
            stdout=log_file,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    finally:
        log_file.close()

    if proc.poll() is not None:
        return _error('rtccli 启动失败，请查看 log/back.log', 500)

    STREAM_PID_FILE.write_text(str(proc.pid), encoding='utf-8')
    state = {
        'running': True,
        'pid': proc.pid,
        'room_id': room_id,
        'user_id': user_id,
        'cinema_filename': cinema_path.name,
        'started_at': datetime.now().isoformat(timespec='seconds'),
    }
    _write_stream_state(state)

    return _success({
        'pid': proc.pid,
        'room_id': room_id,
        'user_id': user_id,
        'cinema_filename': cinema_path.name,
        'config_file': str(BLOG_CONFIG_FILE),
        'log_file': str(BLOG_LOG_FILE),
    }, '推流已启动')


@csrf_exempt
@require_POST
@admin_required
def admin_stop_stream(request):
    _stop_stream_process()
    return _success({'running': False}, '推流已停止')


@require_GET
@admin_required
def admin_runtime_info(request):
    exe = _rtccli_path()
    rtc = get_rtc_settings()
    _, pid, running = _get_stream_status()
    return _success({
        'rtc_runtime_dir': str(RTC_RUNTIME_DIR),
        'rtccli_exists': exe is not None,
        'rtccli_path': str(exe) if exe else None,
        'cinema_dir': str(CINEMA_DIR),
        'app_id_configured': bool(rtc['app_id']),
        'stream_running': running,
        'token_endpoint': f"http://{rtc['token_server_host']}:{rtc['token_server_port']}{rtc['token_server_path']}",
    })
