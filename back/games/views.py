"""
游戏相关视图

Web：上传 .zip，解压至 api/static/games/game_files/{id}/web/；web_entry 为该目录下相对路径（当前策略：按游戏标题推导 {标题}.html，
或仅含一个 html 时自动采用）。
其它平台单文件：game_files/{id}/{platform}{扩展名}。
"""
import json
import mimetypes
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from history.views import admin_required

BASE_DIR = Path(settings.BASE_DIR)
GAME_IMAGES_DIR = BASE_DIR / 'api' / 'static' / 'games' / 'game_images'
GAME_FILES_DIR = BASE_DIR / 'api' / 'static' / 'games' / 'game_files'

ALLOWED_ARCHIVE_EXT = ('.zip',)
ALLOWED_IMAGE_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_WEB_ZIP_BYTES = 280 * 1024 * 1024  # ~280MB
MAX_PLATFORM_FILE_BYTES = 600 * 1024 * 1024

PLATFORM_NAMES = ('windows', 'linux', 'android')


def _safe_basename(name):
    if not name or not isinstance(name, str):
        return None
    base = os.path.basename(name.strip())
    if not base or base in ('.', '..') or '..' in name:
        return None
    return base


def _delete_image_file_if_exists(filename):
    safe = _safe_basename(filename)
    if not safe:
        return
    path = GAME_IMAGES_DIR / safe
    try:
        if path.is_file() and path.resolve().parent == GAME_IMAGES_DIR.resolve():
            path.unlink()
    except Exception:
        pass


def _delete_stored_images_for_game_id(game_id):
    gid = int(game_id)
    for ext in ALLOWED_IMAGE_EXT:
        p = GAME_IMAGES_DIR / f'{gid}{ext}'
        try:
            if p.is_file() and p.resolve().parent == GAME_IMAGES_DIR.resolve():
                p.unlink()
        except Exception:
            pass


def _game_files_root(game_id):
    return (GAME_FILES_DIR / str(int(game_id))).resolve()


def _web_bundle_root(game_id):
    return (_game_files_root(game_id) / 'web').resolve()


def _rmtree_game_assets(game_id):
    base = GAME_FILES_DIR / str(int(game_id))
    try:
        if base.is_dir():
            shutil.rmtree(base, ignore_errors=True)
    except Exception:
        pass


def _row_to_game(row):
    return {
        'id': row[0],
        'title': row[1],
        'content': row[2] if row[2] is not None else '',
        'introduction': row[3],
        'detail': row[4],
        'web_entry': row[5] if row[5] is not None else '',
        'windows': row[6] if row[6] is not None else '',
        'linux': row[7] if row[7] is not None else '',
        'android': row[8] if row[8] is not None else '',
    }


def _row_to_game_public(row):
    d = _row_to_game(row)
    gid = d['id']
    d['has_web'] = bool((d.get('web_entry') or '').strip())
    d['has_windows'] = bool((d.get('windows') or '').strip())
    d['has_linux'] = bool((d.get('linux') or '').strip())
    d['has_android'] = bool((d.get('android') or '').strip())
    d['play_route'] = f'/games/play/{gid}'
    return d


def _normalize_optional_str(value):
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _safe_extract_zip(zf: zipfile.ZipFile, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    dest_r = dest.resolve()
    for m in zf.infolist():
        out = (dest / m.filename).resolve()
        if dest_r not in out.parents and out != dest_r:
            raise ValueError('ZIP 内包含非法路径')
    zf.extractall(dest)


def _expected_web_html_basename(title: str) -> str:
    t = (title or '').strip() or 'game'
    invalid = '<>:"/\\|?*'
    s = ''.join('_' if c in invalid else c for c in t)
    s = s.rstrip('. ') or 'game'
    return f'{s}.html'


def _resolve_web_entry(web_root: Path, title: str) -> str | None:
    """
    当前约定：入口为「与游戏标题同名的单个 .html」（经非法字符替换），否则若 web/
    目录下仅此一个 html 则采用。
    """
    exp = _expected_web_html_basename(title)
    p = web_root / exp
    if p.is_file():
        return exp

    shallow = sorted(
        [x for x in web_root.iterdir() if x.is_file() and x.suffix.lower() == '.html']
    )
    if len(shallow) == 1:
        return shallow[0].name

    all_html = sorted([x for x in web_root.rglob('*.html') if x.is_file()])
    if len(all_html) == 1:
        return str(all_html[0].relative_to(web_root)).replace('\\', '/')

    return None


def _extract_archive_disk(tmp_path: Path, dest_root: Path, ext: str):
    if ext.lower() != '.zip':
        raise ValueError('仅支持 .zip 压缩包')
    dest_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(tmp_path), 'r') as zf:
        _safe_extract_zip(zf, dest_root)


def _delete_old_platform_file(game_id, platform: str):
    root = _game_files_root(game_id)
    if not root.is_dir():
        return
    pre = platform.lower() + '.'
    try:
        for p in root.iterdir():
            if p.is_file() and p.name.lower().startswith(pre):
                p.unlink()
    except Exception:
        pass


@csrf_exempt
@require_GET
def get_games_list(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, content, introduction, detail, web_entry,
                       windows, linux, android
                FROM games
                ORDER BY id DESC
                """
            )
            rows = cursor.fetchall()
        games_list = [_row_to_game_public(r) for r in rows]
        return JsonResponse({'success': True, 'data': {'games': games_list}})
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': f'获取游戏列表失败: {str(e)}'},
            status=500,
        )


@csrf_exempt
@require_GET
def get_game_public(request, game_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, content, introduction, detail, web_entry,
                       windows, linux, android
                FROM games WHERE id = %s
                """,
                [game_id],
            )
            row = cursor.fetchone()
        if not row:
            return JsonResponse({'success': False, 'error': '游戏不存在'}, status=404)
        return JsonResponse({'success': True, 'data': _row_to_game_public(row)})
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': f'获取游戏失败: {str(e)}'},
            status=500,
        )


@csrf_exempt
@require_GET
@admin_required
def admin_get_games_list(request):
    return get_games_list(request)


@csrf_exempt
@admin_required
@require_GET
def admin_get_game(request, game_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, content, introduction, detail, web_entry,
                       windows, linux, android
                FROM games WHERE id = %s
                """,
                [game_id],
            )
            row = cursor.fetchone()
        if not row:
            return JsonResponse({'success': False, 'error': '游戏不存在'}, status=404)
        return JsonResponse({'success': True, 'data': _row_to_game(row)})
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': f'获取游戏失败: {str(e)}'},
            status=500,
        )


@csrf_exempt
@admin_required
@require_POST
def admin_upload_game_image(request, game_id):
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': '没有上传文件'}, status=400)

        uploaded_file = request.FILES['file']
        file_name = (uploaded_file.name or '').lower()
        file_ext = None
        for ext in ALLOWED_IMAGE_EXT:
            if file_name.endswith(ext):
                file_ext = ext
                break
        if not file_ext:
            return JsonResponse(
                {
                    'success': False,
                    'error': f'不支持的格式，仅支持: {", ".join(ALLOWED_IMAGE_EXT)}',
                },
                status=400,
            )

        if uploaded_file.size > MAX_IMAGE_BYTES:
            return JsonResponse({'success': False, 'error': '图片大小不能超过5MB'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute('SELECT id, content FROM games WHERE id = %s', [game_id])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '游戏不存在'}, status=404)
            old_content = row[1]

        if old_content:
            _delete_image_file_if_exists(old_content)
        _delete_stored_images_for_game_id(game_id)

        GAME_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        new_name = f'{int(game_id)}{file_ext}'
        dest = GAME_IMAGES_DIR / new_name

        with open(dest, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE games SET content = %s WHERE id = %s',
                [new_name, game_id],
            )

        return JsonResponse(
            {
                'success': True,
                'message': '上传成功',
                'data': {
                    'filename': new_name,
                    'url': f'/api/static/games/game_images/{new_name}',
                },
            }
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': f'上传失败: {str(e)}'},
            status=500,
        )


@csrf_exempt
@admin_required
@require_POST
def admin_upload_web_zip(request, game_id):
    """
    上传 Web 端 .zip，解压到 game_files/{id}/web/。
    入口 HTML：当前默认为「游戏标题」（非法字符替换后）+.html；若解压结果中仅此一个 html 则自动采纳。
    """
    tmp_written = None
    tmp_path = None
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': '没有上传文件'}, status=400)

        uploaded = request.FILES['file']
        lower = (uploaded.name or '').lower()
        ext = None
        for ae in ALLOWED_ARCHIVE_EXT:
            if lower.endswith(ae):
                ext = ae
                break
        if not ext:
            return JsonResponse(
                {'success': False, 'error': '请上传 .zip 压缩包'},
                status=400,
            )
        if uploaded.size > MAX_WEB_ZIP_BYTES:
            return JsonResponse({'success': False, 'error': '压缩包过大'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute('SELECT id, title FROM games WHERE id = %s', [game_id])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '游戏不存在'}, status=404)
            game_title = row[1]

        dest_root = _web_bundle_root(game_id)
        if dest_root.is_dir():
            shutil.rmtree(dest_root, ignore_errors=True)
        dest_root.parent.mkdir(parents=True, exist_ok=True)

        fd, tmp_written = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        tmp_path = Path(tmp_written)
        try:
            with open(tmp_path, 'wb') as out:
                for chunk in uploaded.chunks():
                    out.write(chunk)
            _extract_archive_disk(tmp_path, dest_root, ext)
        except zipfile.BadZipFile:
            shutil.rmtree(dest_root, ignore_errors=True)
            return JsonResponse({'success': False, 'error': '无效的 zip 文件'}, status=400)
        except ValueError as ve:
            shutil.rmtree(dest_root, ignore_errors=True)
            return JsonResponse({'success': False, 'error': str(ve)}, status=400)
        finally:
            tmp_path.unlink(missing_ok=True)
            tmp_written = None
            tmp_path = None

        entry = _resolve_web_entry(dest_root, game_title)
        if not entry:
            shutil.rmtree(dest_root, ignore_errors=True)
            exp = _expected_web_html_basename(game_title)
            return JsonResponse(
                {
                    'success': False,
                    'error': (
                        f'未解析到可用 HTML（请保证解压后仅此一个 .html，'
                        f'或存在入口文件「{exp}」与当前游戏标题一致）'
                    ),
                },
                status=400,
            )

        entry = entry.replace('\\', '/')
        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE games SET web_entry = %s WHERE id = %s',
                [entry, game_id],
            )
            cursor.execute(
                """
                SELECT id, title, content, introduction, detail, web_entry,
                       windows, linux, android
                FROM games WHERE id = %s
                """,
                [game_id],
            )
            row = cursor.fetchone()

        return JsonResponse(
            {
                'success': True,
                'message': 'Web 资源已部署',
                'data': _row_to_game(row),
            }
        )
    except Exception as e:
        if tmp_written:
            try:
                Path(tmp_written).unlink(missing_ok=True)
            except Exception:
                pass
        return JsonResponse(
            {'success': False, 'error': f'部署失败: {str(e)}'},
            status=500,
        )


@csrf_exempt
@admin_required
@require_POST
def admin_upload_platform_file(request, game_id):
    """
    上传单平台压缩包/安装包。表单字段：platform=windows|linux|android，file=文件；
    保存为 game_files/{id}/{platform}{原扩展名}
    """
    try:
        platform = (request.POST.get('platform') or '').strip().lower()
        if platform not in PLATFORM_NAMES:
            return JsonResponse({'success': False, 'error': 'platform 无效'}, status=400)
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': '没有上传文件'}, status=400)

        uploaded = request.FILES['file']
        if uploaded.size > MAX_PLATFORM_FILE_BYTES:
            return JsonResponse({'success': False, 'error': '文件过大'}, status=400)

        orig = (uploaded.name or 'file').lower()
        m = re.search(r'(\.[a-z0-9]{1,8})$', orig)
        ext = m.group(1) if m else ''

        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT id, {platform} FROM games WHERE id = %s',
                [game_id],
            )
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '游戏不存在'}, status=404)
            old_name = row[1]

        root = _game_files_root(game_id)
        root.mkdir(parents=True, exist_ok=True)

        if old_name:
            old_path = root / _safe_basename(old_name)
            if old_path and old_path.is_file():
                try:
                    old_path.unlink()
                except Exception:
                    pass
        _delete_old_platform_file(game_id, platform)

        save_name = f'{platform}{ext}'
        dest = root / save_name
        if dest.resolve().parent != root:
            return JsonResponse({'success': False, 'error': '非法文件名'}, status=400)

        with open(dest, 'wb') as f:
            for chunk in uploaded.chunks():
                f.write(chunk)

        with connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE games SET {platform} = %s WHERE id = %s',
                [save_name, game_id],
            )
            cursor.execute(
                """
                SELECT id, title, content, introduction, detail, web_entry,
                       windows, linux, android
                FROM games WHERE id = %s
                """,
                [game_id],
            )
            row = cursor.fetchone()

        return JsonResponse(
            {'success': True, 'message': '上传成功', 'data': _row_to_game(row)}
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': f'上传失败: {str(e)}'},
            status=500,
        )


@csrf_exempt
@require_GET
def download_platform_file(request, game_id, platform):
    """公开下载（管理员上传的安装包）"""
    if platform not in PLATFORM_NAMES:
        raise Http404()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT {platform} FROM games WHERE id = %s',
                [game_id],
            )
            row = cursor.fetchone()
        if not row or not row[0]:
            raise Http404()
        fname = _safe_basename(row[0])
        if not fname:
            raise Http404()
        path = _game_files_root(game_id) / fname
        if not path.is_file() or path.resolve().parent != _game_files_root(game_id):
            raise Http404()
        ctype, _ = mimetypes.guess_type(path.name)
        try:
            f = open(path, 'rb')
        except OSError:
            raise Http404()
        resp = FileResponse(
            f,
            content_type=ctype or 'application/octet-stream',
        )
        resp['Content-Disposition'] = f'attachment; filename="{path.name}"'
        return resp
    except Http404:
        raise
    except Exception:
        raise Http404()


@csrf_exempt
@admin_required
@require_POST
def admin_create_game(request):
    try:
        data = json.loads(request.body.decode())
        title = (data.get('title') or '').strip()
        introduction = (data.get('introduction') or '').strip()
        detail = (data.get('detail') or '').strip()
        content_raw = data.get('content')
        content = _normalize_optional_str(content_raw) if content_raw is not None else None
        if content is not None:
            content = _safe_basename(content)

        web_entry = _normalize_optional_str(data.get('web_entry'))
        windows = _normalize_optional_str(data.get('windows'))
        linux = _normalize_optional_str(data.get('linux'))
        android = _normalize_optional_str(data.get('android'))

        if not title or not introduction or not detail:
            return JsonResponse(
                {'success': False, 'error': '标题、简介（卡片底部）与详情为必填项'},
                status=400,
            )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO games (title, content, introduction, detail, web_entry,
                    windows, linux, android)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    title,
                    content,
                    introduction,
                    detail,
                    web_entry,
                    windows,
                    linux,
                    android,
                ],
            )
            new_id = cursor.lastrowid
            cursor.execute(
                """
                SELECT id, title, content, introduction, detail, web_entry,
                       windows, linux, android
                FROM games WHERE id = %s
                """,
                [new_id],
            )
            row = cursor.fetchone()

        return JsonResponse(
            {
                'success': True,
                'data': _row_to_game(row),
                'message': '游戏创建成功',
            }
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': f'创建游戏失败: {str(e)}'},
            status=500,
        )


@csrf_exempt
@admin_required
@require_http_methods(['PUT'])
def admin_update_game(request, game_id):
    try:
        data = json.loads(request.body.decode())
        title = (data.get('title') or '').strip()
        introduction = (data.get('introduction') or '').strip()
        detail = (data.get('detail') or '').strip()
        content_raw = data.get('content')
        content = _normalize_optional_str(content_raw) if content_raw is not None else None
        if content is not None:
            content = _safe_basename(content)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT content, web_entry, windows, linux, android
                FROM games WHERE id = %s
                """,
                [game_id],
            )
            old = cursor.fetchone()
            if not old:
                return JsonResponse({'success': False, 'error': '游戏不存在'}, status=404)

        old_content, old_web_entry, ow, ol, oa = old[0], old[1], old[2], old[3], old[4]

        if 'web_entry' in data:
            web_entry_raw = data.get('web_entry')
            web_entry = (
                _normalize_optional_str(web_entry_raw)
                if web_entry_raw is not None
                else None
            )
            if web_entry:
                web_entry = web_entry.replace('\\', '/')
        else:
            web_entry = old_web_entry

        if 'windows' in data:
            windows = _normalize_optional_str(data.get('windows'))
        else:
            windows = ow
        if 'linux' in data:
            linux = _normalize_optional_str(data.get('linux'))
        else:
            linux = ol
        if 'android' in data:
            android = _normalize_optional_str(data.get('android'))
        else:
            android = oa

        if not title or not introduction or not detail:
            return JsonResponse(
                {'success': False, 'error': '标题、简介（卡片底部）与详情为必填项'},
                status=400,
            )

        with connection.cursor() as cursor:

            old_fn = _safe_basename(old_content) if old_content else None
            new_fn = content
            if old_fn and old_fn != new_fn:
                _delete_image_file_if_exists(old_content)

            # 清空 Web：删解压目录
            if not (web_entry or '').strip() and (old_web_entry or '').strip():
                shutil.rmtree(_web_bundle_root(game_id), ignore_errors=True)

            # 清空各平台文件
            def _sync_plat(old_name, new_name, plat):
                o = _safe_basename(old_name) if old_name else None
                n = _safe_basename(new_name) if new_name else None
                if o and (not n or n != o):
                    pth = _game_files_root(game_id) / o
                    try:
                        if pth.is_file():
                            pth.unlink()
                    except Exception:
                        pass

            _sync_plat(ow, windows, 'windows')
            _sync_plat(ol, linux, 'linux')
            _sync_plat(oa, android, 'android')

            cursor.execute(
                """
                UPDATE games SET
                    title = %s,
                    content = %s,
                    introduction = %s,
                    detail = %s,
                    web_entry = %s,
                    windows = %s,
                    linux = %s,
                    android = %s
                WHERE id = %s
                """,
                [
                    title,
                    content,
                    introduction,
                    detail,
                    web_entry,
                    windows,
                    linux,
                    android,
                    game_id,
                ],
            )
            cursor.execute(
                """
                SELECT id, title, content, introduction, detail, web_entry,
                       windows, linux, android
                FROM games WHERE id = %s
                """,
                [game_id],
            )
            row = cursor.fetchone()

        return JsonResponse(
            {'success': True, 'data': _row_to_game(row), 'message': '游戏更新成功'}
        )
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '请求体无效'}, status=400)
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': f'更新游戏失败: {str(e)}'},
            status=500,
        )


@csrf_exempt
@admin_required
@require_http_methods(['DELETE'])
def admin_delete_game(request, game_id):
    try:
        gid = int(game_id)
        with connection.cursor() as cursor:
            cursor.execute('SELECT content FROM games WHERE id = %s', [gid])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '游戏不存在'}, status=404)
            img = row[0]
            if img:
                _delete_image_file_if_exists(img)
            cursor.execute('DELETE FROM games WHERE id = %s', [gid])

        _rmtree_game_assets(gid)

        return JsonResponse({'success': True, 'message': '游戏删除成功'})
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': f'删除游戏失败: {str(e)}'},
            status=500,
        )