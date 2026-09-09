"""片源预处理：1920x1080@30，片头 10 秒黑屏。"""
import json
import re
from datetime import datetime
from pathlib import Path

from .mediamtx_config import (
    CINEMA_READY_DIR,
    STREAM_RUNTIME_DIR,
    TRANSCODE_FPS,
    TRANSCODE_HEIGHT,
    TRANSCODE_LEAD_SECONDS,
    TRANSCODE_PROGRESS_FILE,
    TRANSCODE_STATE_FILE,
    TRANSCODE_WIDTH,
)


def ready_dir():
    CINEMA_READY_DIR.mkdir(parents=True, exist_ok=True)
    return CINEMA_READY_DIR


def ready_path(filename):
    return ready_dir() / filename


def tmp_path(filename):
    # 必须以 .mp4 结尾，否则 ffmpeg 无法从扩展名判断容器
    return ready_dir() / f'{Path(filename).stem}.transcoding.mp4'


def is_ready(filename):
    path = ready_path(filename)
    return path.is_file() and path.stat().st_size > 0


def unlink_outputs(filename):
    leftovers = [
        ready_path(filename),
        tmp_path(filename),
        ready_dir() / f'{filename}.tmp',
    ]
    for path in leftovers:
        if path.is_file():
            try:
                path.unlink()
            except OSError:
                pass


def read_state():
    if not TRANSCODE_STATE_FILE.is_file():
        return {}
    try:
        with open(TRANSCODE_STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def write_state(state):
    STREAM_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRANSCODE_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def progress_ended():
    if not TRANSCODE_PROGRESS_FILE.is_file():
        return False
    try:
        text = TRANSCODE_PROGRESS_FILE.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False
    return bool(re.search(r'^progress=end\s*$', text, re.M))


def progress_out_time_sec():
    if not TRANSCODE_PROGRESS_FILE.is_file():
        return 0.0
    try:
        text = TRANSCODE_PROGRESS_FILE.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return 0.0
    matches = re.findall(r'out_time_us=(\d+)', text)
    if matches:
        return int(matches[-1]) / 1_000_000
    matches = re.findall(r'out_time_ms=(\d+)', text)
    if matches:
        return int(matches[-1]) / 1000
    return 0.0


def percent_for(state):
    duration = float(state.get('duration_sec') or 0)
    out_time = progress_out_time_sec()
    if duration <= 0:
        return 0
    return max(0, min(99, int(out_time / duration * 100)))


def public_state(state=None):
    state = dict(state or read_state())
    status = state.get('status') or 'idle'
    if status == 'running':
        state['percent'] = percent_for(state)
        state['out_time_sec'] = round(progress_out_time_sec(), 1)
    elif status == 'done':
        state['percent'] = 100
    else:
        state.setdefault('percent', 0)
    return {
        'status': status,
        'filename': state.get('filename'),
        'percent': int(state.get('percent') or 0),
        'out_time_sec': state.get('out_time_sec'),
        'duration_sec': state.get('duration_sec'),
        'started_at': state.get('started_at'),
        'finished_at': state.get('finished_at'),
        'error': state.get('error') or '',
    }


def mark_running(filename, duration_sec, pid):
    write_state({
        'status': 'running',
        'filename': filename,
        'pid': pid,
        'duration_sec': round(float(duration_sec or 0), 1),
        'percent': 0,
        'started_at': datetime.now().isoformat(timespec='seconds'),
        'finished_at': None,
        'error': '',
    })


def mark_done(filename):
    state = read_state()
    if state.get('filename') and state.get('filename') != filename:
        state = {}
    state.update({
        'status': 'done',
        'filename': filename,
        'percent': 100,
        'finished_at': datetime.now().isoformat(timespec='seconds'),
        'error': '',
    })
    write_state(state)


def mark_failed(filename, error):
    state = read_state()
    if state.get('filename') and state.get('filename') != filename:
        state = {'filename': filename}
    state.update({
        'status': 'failed',
        'filename': filename,
        'finished_at': datetime.now().isoformat(timespec='seconds'),
        'error': (error or '转码失败')[:500],
    })
    write_state(state)


def build_cmd(ffmpeg_bin, src_path, dst_tmp, has_audio):
    """离线转成 WebRTC 可直拷的 H.264 1080p30，片头加黑屏。单线程编码。"""
    w, h, fps = TRANSCODE_WIDTH, TRANSCODE_HEIGHT, TRANSCODE_FPS
    lead = TRANSCODE_LEAD_SECONDS
    vf_main = (
        f'fps={fps},'
        f'scale={w}:{h}:force_original_aspect_ratio=decrease,'
        f'pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,'
        'setsar=1,format=yuv420p,setpts=PTS-STARTPTS'
    )
    vf_black = f'fps={fps},format=yuv420p,setsar=1,setpts=PTS-STARTPTS'
    encode = [
        '-c:v', 'libx264',
        '-threads', '1',
        '-x264-params', 'threads=1:sliced_threads=0',
        '-preset', 'veryfast',
        '-profile:v', 'baseline',
        '-level', '4.0',
        '-pix_fmt', 'yuv420p',
        '-g', str(fps),
        '-keyint_min', str(fps),
        '-sc_threshold', '0',
        '-bf', '0',
        '-b:v', '3000k',
        '-maxrate', '3000k',
        '-bufsize', '6000k',
        '-c:a', 'aac',
        '-ar', '48000',
        '-ac', '2',
        '-b:a', '128k',
        '-movflags', '+faststart',
    ]
    cmd = [
        ffmpeg_bin,
        '-y',
        '-nostdin',
        '-hide_banner',
        '-loglevel', 'info',
        '-progress', str(TRANSCODE_PROGRESS_FILE),
        '-threads', '1',
        '-filter_threads', '1',
        '-filter_complex_threads', '1',
        '-f', 'lavfi',
        '-t', str(lead),
        '-i', f'color=c=black:s={w}x{h}:r={fps}',
    ]
    if has_audio:
        cmd.extend([
            '-f', 'lavfi',
            '-t', str(lead),
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000',
            '-i', str(src_path),
            '-filter_complex',
            (
                f'[0:v]{vf_black}[vblack];'
                f'[2:v]{vf_main}[vmain];'
                '[vblack][vmain]concat=n=2:v=1:a=0[vout];'
                '[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,'
                'asetpts=PTS-STARTPTS[ablack];'
                '[2:a]aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:'
                'channel_layouts=stereo,asetpts=PTS-STARTPTS[amain];'
                '[ablack][amain]concat=n=2:v=0:a=1[aout]'
            ),
            '-map', '[vout]',
            '-map', '[aout]',
            '-shortest',
        ])
    else:
        cmd.extend([
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000',
            '-i', str(src_path),
            '-filter_complex',
            (
                f'[0:v]{vf_black}[vblack];'
                f'[2:v]{vf_main}[vmain];'
                '[vblack][vmain]concat=n=2:v=1:a=0[vout]'
            ),
            '-map', '[vout]',
            '-map', '1:a',
            '-shortest',
        ])
    cmd.extend(encode)
    cmd.extend(['-f', 'mp4', str(dst_tmp)])
    return cmd


def scan_extra(filename):
    ready = ready_path(filename)
    transcoded = ready.is_file() and ready.stat().st_size > 0
    extra = {
        'transcoded': transcoded,
        'transcoded_size_mb': 0,
    }
    if transcoded:
        extra['transcoded_size_mb'] = round(ready.stat().st_size / (1024 * 1024), 2)
    return extra
