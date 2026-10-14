"""
管理后台：接收腾讯云 Nginx 证书 zip，存到非公开目录。
安装、解压、替换和删除由 depend_manage/install_nginx_cert.sh 完成。
"""
import os
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .views import admin_required

INBOX_DIR = Path(settings.BASE_DIR) / 'api' / 'nginx_cert' / 'inbox'
ZIP_NAME = 'lybandljy.cn_nginx.zip'
MAX_ZIP_BYTES = 2 * 1024 * 1024
INSTALL_SCRIPT = Path(settings.BASE_DIR) / 'depend_manage' / 'install_nginx_cert.sh'


def _zip_path():
    return INBOX_DIR / ZIP_NAME


def _ensure_inbox():
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(INBOX_DIR, 0o700)
    except OSError:
        pass


def _status_payload():
    path = _zip_path()
    pending = path.is_file()
    uploaded_at = None
    size = 0
    if pending:
        stat = path.stat()
        size = stat.st_size
        uploaded_at = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    return {
        'pending': pending,
        'filename': ZIP_NAME if pending else None,
        'size': size,
        'uploaded_at': uploaded_at,
    }


def _error(message, status=400):
    return JsonResponse({'success': False, 'error': message}, status=status)


def _inspect_zip(path):
    """只看文件名，确认包内有一把私钥和一份完整链证书。"""
    if not zipfile.is_zipfile(path):
        raise ValueError('不是有效的 zip 压缩包')

    keys = []
    bundle_crts = []
    bundle_pems = []
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            name = info.filename.replace('\\', '/')
            if not name or name.endswith('/'):
                continue
            parts = Path(name).parts
            if name.startswith('/') or '..' in parts:
                raise ValueError('压缩包包含非法路径')
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise ValueError('压缩包包含符号链接，已拒绝')
            base = Path(name).name.lower()
            if base.endswith('.key'):
                keys.append(base)
            elif base.endswith('_bundle.crt'):
                bundle_crts.append(base)
            elif base.endswith('_bundle.pem'):
                bundle_pems.append(base)

    if len(keys) != 1:
        raise ValueError('压缩包里需要且只能有一个 .key 私钥文件')
    if not bundle_crts and not bundle_pems:
        raise ValueError('压缩包里需要有 _bundle.crt 或 _bundle.pem 完整链证书')


@csrf_exempt
@admin_required
@require_GET
def cert_status(request):
    return JsonResponse({'success': True, 'data': _status_payload()})


@csrf_exempt
@admin_required
@require_http_methods(['POST'])
def cert_upload(request):
    upload = request.FILES.get('file')
    if not upload:
        return _error('请上传证书 zip')

    filename = (upload.name or '').lower()
    if not filename.endswith('.zip'):
        return _error('只接受 .zip 压缩包')
    if upload.size > MAX_ZIP_BYTES:
        return _error('证书包超过 2MB，已拒绝')

    _ensure_inbox()
    target = _zip_path()
    temp = INBOX_DIR / f'{ZIP_NAME}.uploading'
    try:
        with open(temp, 'wb') as out:
            for chunk in upload.chunks():
                out.write(chunk)
        os.chmod(temp, 0o600)
        _inspect_zip(temp)
        os.replace(temp, target)
    except ValueError as exc:
        return _error(str(exc))
    except OSError as exc:
        return _error(f'保存证书包失败: {exc}', 500)
    finally:
        if temp.exists():
            temp.unlink()

    return JsonResponse({
        'success': True,
        'message': '证书包已保存',
        'data': _status_payload(),
    })


@csrf_exempt
@admin_required
@require_http_methods(['POST'])
def cert_install(request):
    if not _zip_path().is_file():
        return _error('请先上传证书包')
    if not INSTALL_SCRIPT.is_file():
        return _error('未找到安装脚本', 500)
    try:
        result = subprocess.run(
            ['bash', str(INSTALL_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return _error('安装超时', 500)
    except OSError as exc:
        return _error(f'执行安装脚本失败: {exc}', 500)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or '').strip()
        return _error(detail or '安装失败', 500)
    return JsonResponse({
        'success': True,
        'message': '证书已更新',
        'data': _status_payload(),
    })


@csrf_exempt
@admin_required
@require_http_methods(['DELETE', 'POST'])
def cert_delete(request):
    path = _zip_path()
    if path.is_file():
        path.unlink()
    return JsonResponse({
        'success': True,
        'message': '待安装证书包已删除',
        'data': _status_payload(),
    })
