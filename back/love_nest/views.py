"""
爱情小窝相关视图
"""
import json
import logging
from datetime import date, datetime
from functools import wraps
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.db import connection, IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from common.jwt_utils import jwt_required

try:
    from PIL import Image
except ImportError:
    Image = None

BASE_DIR = Path(settings.BASE_DIR)
PHOTOS_DIR = BASE_DIR / 'api' / 'static' / 'love_nest' / 'photos'

ALLOWED_IMAGE_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
PHOTO_UPLOAD_CATEGORIES = ('person', 'scenery', 'food')
PHOTO_QUERY_CATEGORIES = PHOTO_UPLOAD_CATEGORIES
MAX_IMAGE_BYTES = 5 * 1024 * 1024

_DIARY_SELECT_SQL = """
    SELECT d.id, d.diary_date, d.photo_id, d.sentence,
           p.id, p.filename, p.title, p.caption, p.category, p.travel_city_id
    FROM love_nest_diaries d
    LEFT JOIN love_nest_photos p ON d.photo_id = p.id
"""

_PHOTO_SELECT_COLS = 'id, filename, title, caption, category, travel_city_id'

logger = logging.getLogger(__name__)


def _error_json(user_message, *, log_exc=False, status=500):
    if log_exc:
        logger.exception(user_message)
    return JsonResponse({'success': False, 'error': user_message}, status=status)


def _image_ext_from_name(name):
    file_name = (name or '').lower()
    for ext in ALLOWED_IMAGE_EXT:
        if file_name.endswith(ext):
            return ext
    return None


def _compress_image_bytes(data, ext):
    if len(data) <= MAX_IMAGE_BYTES:
        return data, ext
    if Image is None:
        raise ValueError('图片超过5MB，请换一张较小的图片')

    img = Image.open(BytesIO(data))
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        if img.mode in ('RGBA', 'LA'):
            background.paste(img, mask=img.split()[-1])
        else:
            background.paste(img)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    quality = 88
    scale = 1.0
    result = data
    for _ in range(10):
        working = img
        if scale < 1.0:
            width, height = img.size
            working = img.resize(
                (max(1, int(width * scale)), max(1, int(height * scale))),
                Image.Resampling.LANCZOS,
            )
        buf = BytesIO()
        working.save(buf, format='JPEG', quality=quality, optimize=True)
        result = buf.getvalue()
        if len(result) <= MAX_IMAGE_BYTES:
            return result, '.jpg'
        quality = max(50, quality - 8)
        scale *= 0.9

    if len(result) > MAX_IMAGE_BYTES:
        raise ValueError('图片压缩后仍超过5MB，请换一张较小的图片')
    return result, '.jpg'


def _save_uploaded_image(uploaded_file, dest_without_suffix):
    data = b''.join(uploaded_file.chunks())
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError('图片大小不能超过5MB')
    ext = _image_ext_from_name(uploaded_file.name)
    if not ext:
        raise ValueError(f'不支持的格式，仅支持: {", ".join(ALLOWED_IMAGE_EXT)}')
    data, save_ext = _compress_image_bytes(data, ext)
    dest_without_suffix.parent.mkdir(parents=True, exist_ok=True)
    dest_path = dest_without_suffix.with_suffix(save_ext)
    with open(dest_path, 'wb') as handle:
        handle.write(data)
    return dest_path.name


def _photo_public_url(filename):
    if not filename:
        return None
    return f'/api/static/love_nest/photos/{filename}'


def _get_photo_filename(photo_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT filename FROM love_nest_photos WHERE id = %s', [photo_id])
        row = cursor.fetchone()
    if not row or not row[0]:
        raise ValueError('相册照片不存在')
    return row[0]


def _create_album_photo(uploaded_file, category, title=None, caption=None, travel_city_id=None):
    if category not in PHOTO_QUERY_CATEGORIES:
        raise ValueError('无效的照片分类')

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO love_nest_photos
            (filename, title, caption, category, travel_city_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            ['', title, caption, category, travel_city_id],
        )
        photo_id = cursor.lastrowid

    category_dir = PHOTOS_DIR / category
    saved_name = _save_uploaded_image(uploaded_file, category_dir / str(int(photo_id)))
    relative_filename = f'{category}/{saved_name}'

    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE love_nest_photos SET filename = %s WHERE id = %s',
            [relative_filename, photo_id],
        )

    return photo_id, relative_filename


def _replace_album_photo_file(photo_id, uploaded_file, category=None):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT filename, category FROM love_nest_photos WHERE id = %s',
            [photo_id],
        )
        row = cursor.fetchone()
    if not row:
        raise ValueError('照片不存在')

    old_filename, current_category = row[0], row[1]
    target_category = category if category in PHOTO_UPLOAD_CATEGORIES else current_category

    category_dir = PHOTOS_DIR / target_category
    saved_name = _save_uploaded_image(uploaded_file, category_dir / str(int(photo_id)))
    new_relative = f'{target_category}/{saved_name}'

    if old_filename and old_filename != new_relative:
        _delete_photo_file(old_filename)

    return new_relative, target_category


def _relocate_album_photo_category(photo_id, new_category):
    if new_category not in PHOTO_UPLOAD_CATEGORIES:
        raise ValueError('无效的照片分类')

    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT filename, category FROM love_nest_photos WHERE id = %s',
            [photo_id],
        )
        row = cursor.fetchone()
    if not row or not row[0]:
        raise ValueError('照片不存在')

    old_filename, old_category = row[0], row[1]
    if old_category == new_category:
        return old_filename, new_category

    old_path = (PHOTOS_DIR / old_filename).resolve()
    photos_root = PHOTOS_DIR.resolve()
    if not str(old_path).startswith(str(photos_root)) or not old_path.is_file():
        return f'{new_category}/{old_path.name}', new_category

    dest_dir = PHOTOS_DIR / new_category
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / old_path.name
    if dest_path.exists():
        dest_path.unlink()
    old_path.rename(dest_path)
    return f'{new_category}/{dest_path.name}', new_category


def _resolve_diary_photo_id(photo_id, uploaded_file, category):
    if photo_id:
        try:
            photo_id = int(photo_id)
        except (TypeError, ValueError):
            raise ValueError('photo_id 无效')
        _get_photo_filename(photo_id)
        return photo_id

    if uploaded_file:
        if category not in PHOTO_UPLOAD_CATEGORIES:
            raise ValueError('上传新图时必须选择分类：人物、风景或食物')
        new_photo_id, _filename = _create_album_photo(
            uploaded_file,
            category,
        )
        return new_photo_id

    return None


def _parse_member_ids(raw):
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return [int(x) for x in raw]
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        return [int(x) for x in (data or [])]
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def _get_config_row():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, start_date, slogan, member_user_ids
            FROM love_nest_config
            WHERE id = 1
            """
        )
        return cursor.fetchone()


def _get_member_user_ids():
    row = _get_config_row()
    if not row:
        return []
    return _parse_member_ids(row[3])


def _user_is_admin(user_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT is_admin FROM users WHERE id = %s', [user_id])
        row = cursor.fetchone()
        return bool(row and row[0])


def _user_is_love_nest_editor(user_id):
    if _user_is_admin(user_id):
        return True
    return user_id in _get_member_user_ids()


def admin_required(view_func):
    @wraps(view_func)
    @jwt_required
    def _wrapped_view(request, *args, **kwargs):
        if not _user_is_admin(request.user_id):
            return JsonResponse(
                {'success': False, 'error': '需要管理员权限', 'code': 'ADMIN_REQUIRED'},
                status=403,
            )
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def love_nest_editor_required(view_func):
    @wraps(view_func)
    @jwt_required
    def _wrapped_view(request, *args, **kwargs):
        if not _user_is_love_nest_editor(request.user_id):
            return JsonResponse(
                {'success': False, 'error': '需要爱情小窝编辑权限', 'code': 'LOVE_NEST_EDITOR_REQUIRED'},
                status=403,
            )
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def _avatar_url(user_id, avatar_ext):
    if not avatar_ext:
        return None
    ext = avatar_ext if str(avatar_ext).startswith('.') else f'.{avatar_ext}'
    return f'/api/static/user_heads/{user_id}{ext}'


def _fetch_member_profiles(member_ids):
    if not member_ids:
        return []
    placeholders = ','.join(['%s'] * len(member_ids))
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT id, username, avatar
            FROM users
            WHERE id IN ({placeholders})
            ORDER BY FIELD(id, {placeholders})
            """,
            [*member_ids, *member_ids],
        )
        rows = cursor.fetchall()
    members = []
    for row in rows:
        user_id = row[0]
        members.append({
            'id': user_id,
            'username': row[1],
            'avatar': row[2],
            'avatar_url': _avatar_url(user_id, row[2]),
        })
    return members


def _calc_days_together(start_date_value):
    if not start_date_value:
        return None
    if isinstance(start_date_value, datetime):
        start = start_date_value.date()
    elif isinstance(start_date_value, date):
        start = start_date_value
    else:
        start = date.fromisoformat(str(start_date_value))
    return max((date.today() - start).days, 0)


def _row_to_photo(row):
    filename = row[1]
    return {
        'id': row[0],
        'filename': filename,
        'url': f'/api/static/love_nest/photos/{filename}',
        'title': row[2],
        'caption': row[3],
        'category': row[4],
        'travel_city_id': row[5],
    }


def _delete_photo_file(filename):
    if not filename or not isinstance(filename, str):
        return
    safe = filename.replace('\\', '/').strip('/')
    if not safe or '..' in safe:
        return
    path = (PHOTOS_DIR / safe).resolve()
    try:
        if path.is_file() and str(path).startswith(str(PHOTOS_DIR.resolve())):
            path.unlink()
    except Exception:
        pass


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return None


@csrf_exempt
@require_GET
def get_config(request):
    try:
        payload, error = _build_config_payload()
        if error:
            return JsonResponse({'success': False, 'error': error}, status=404)
        return JsonResponse({'success': True, 'data': payload})
    except Exception:
        return _error_json('获取配置失败，请稍后重试', log_exc=True)


def _build_config_payload():
    row = _get_config_row()
    if not row:
        return None, '配置不存在'

    member_ids = _parse_member_ids(row[3])
    start_date = row[1]
    return {
        'start_date': start_date.isoformat() if start_date else None,
        'slogan': row[2],
        'days_together': _calc_days_together(start_date),
        'members': _fetch_member_profiles(member_ids),
    }, None


@csrf_exempt
@require_GET
def list_decor_photos(request):
    """漂浮背景素材：数据库中的人物/风景/食物照片"""
    try:
        photos = []
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT filename, category
                FROM love_nest_photos
                WHERE category IN ('person', 'scenery', 'food')
                ORDER BY id DESC
                """
            )
            for filename, category in cursor.fetchall():
                if not filename:
                    continue
                photos.append({
                    'url': f'/api/static/love_nest/photos/{filename}',
                    'category': category,
                })

        return JsonResponse({'success': True, 'data': {'photos': photos}})
    except Exception:
        return _error_json('获取漂浮素材失败，请稍后重试', log_exc=True)


@csrf_exempt
@require_GET
def get_photos(request):
    try:
        category = request.GET.get('category', '').strip()
        page = max(int(request.GET.get('page', 1)), 1)
        page_size = min(max(int(request.GET.get('page_size', 20)), 1), 100)
        offset = (page - 1) * page_size

        where_conditions = []
        params = []
        if category in PHOTO_UPLOAD_CATEGORIES:
            where_conditions.append('category = %s')
            params.append(category)
        else:
            where_conditions.append("category IN ('person', 'scenery', 'food')")

        where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'

        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT COUNT(*) FROM love_nest_photos WHERE {where_clause}',
                params,
            )
            total = cursor.fetchone()[0]

            cursor.execute(
                f"""
                SELECT {_PHOTO_SELECT_COLS}
                FROM love_nest_photos
                WHERE {where_clause}
                ORDER BY id DESC
                LIMIT %s OFFSET %s
                """,
                [*params, page_size, offset],
            )
            rows = cursor.fetchall()

        photos = [_row_to_photo(row) for row in rows]
        total_pages = (total + page_size - 1) // page_size if total else 0
        return JsonResponse({
            'success': True,
            'data': {
                'photos': photos,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
            },
        })
    except Exception:
        return _error_json('获取照片失败，请稍后重试', log_exc=True)


@csrf_exempt
@require_GET
def check_editor(request):
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return JsonResponse({
                'success': True,
                'data': {
                    'can_edit': False,
                    'is_admin': False,
                },
            })

        is_admin = _user_is_admin(user_id)
        can_edit = _user_is_love_nest_editor(user_id)
        return JsonResponse({
            'success': True,
            'data': {
                'can_edit': can_edit,
                'is_admin': is_admin,
            },
        })
    except Exception:
        return _error_json('检查权限失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_POST
def upload_photo(request):
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': '没有上传文件'}, status=400)

        uploaded_file = request.FILES['file']
        file_ext = _image_ext_from_name(uploaded_file.name)
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

        title = (request.POST.get('title') or '').strip() or None
        caption = (request.POST.get('caption') or '').strip() or None
        category = (request.POST.get('category') or '').strip()
        if category not in PHOTO_UPLOAD_CATEGORIES:
            return JsonResponse(
                {'success': False, 'error': '请选择分类：人物、风景或食物'},
                status=400,
            )
        try:
            photo_id, _relative_filename = _create_album_photo(
                uploaded_file,
                category,
                title=title,
                caption=caption,
            )
        except ValueError as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {_PHOTO_SELECT_COLS}
                FROM love_nest_photos
                WHERE id = %s
                """,
                [photo_id],
            )
            row = cursor.fetchone()

        return JsonResponse({
            'success': True,
            'message': '上传成功',
            'data': _row_to_photo(row),
        })
    except Exception:
        return _error_json('上传失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_http_methods(['PUT', 'POST'])
def update_photo(request, photo_id):
    try:
        content_type = request.content_type or ''
        uploaded_file = request.FILES.get('file') if 'multipart/form-data' in content_type else None

        if 'multipart/form-data' in content_type:
            data = request.POST
        else:
            data = _parse_json_body(request)
            if data is None:
                return JsonResponse({'success': False, 'error': '请求体必须是 JSON 或 multipart/form-data'}, status=400)

        fields = []
        params = []
        if 'title' in data:
            fields.append('title = %s')
            params.append((data.get('title') or '').strip() or None)
        if 'caption' in data:
            fields.append('caption = %s')
            params.append((data.get('caption') or '').strip() or None)

        category = (data.get('category') or '').strip() if hasattr(data, 'get') else ''
        category_in_request = category in PHOTO_UPLOAD_CATEGORIES

        if uploaded_file:
            try:
                new_filename, resolved_category = _replace_album_photo_file(
                    photo_id,
                    uploaded_file,
                    category if category_in_request else None,
                )
            except ValueError as exc:
                return JsonResponse({'success': False, 'error': str(exc)}, status=400)
            fields.append('filename = %s')
            params.append(new_filename)
            fields.append('category = %s')
            params.append(resolved_category)
        elif category_in_request:
            try:
                new_filename, resolved_category = _relocate_album_photo_category(photo_id, category)
            except ValueError as exc:
                return JsonResponse({'success': False, 'error': str(exc)}, status=400)
            fields.append('filename = %s')
            params.append(new_filename)
            fields.append('category = %s')
            params.append(resolved_category)

        if not fields:
            return JsonResponse({'success': False, 'error': '没有可更新的字段'}, status=400)

        params.append(photo_id)
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE love_nest_photos SET {', '.join(fields)} WHERE id = %s",
                params,
            )
            if cursor.rowcount == 0:
                return JsonResponse({'success': False, 'error': '照片不存在'}, status=404)
            cursor.execute(
                f"""
                SELECT {_PHOTO_SELECT_COLS}
                FROM love_nest_photos
                WHERE id = %s
                """,
                [photo_id],
            )
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '照片不存在'}, status=404)

        return JsonResponse({
            'success': True,
            'message': '更新成功',
            'data': _row_to_photo(row),
        })
    except Exception:
        return _error_json('更新失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_http_methods(['DELETE'])
def delete_photo(request, photo_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT filename FROM love_nest_photos WHERE id = %s',
                [photo_id],
            )
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '照片不存在'}, status=404)
            filename = row[0]
            cursor.execute('DELETE FROM love_nest_photos WHERE id = %s', [photo_id])

        _delete_photo_file(filename)
        return JsonResponse({'success': True, 'message': '删除成功'})
    except Exception:
        return _error_json('删除失败，请稍后重试', log_exc=True)


@csrf_exempt
@admin_required
@require_http_methods(['PUT'])
def update_config(request):
    try:
        data = _parse_json_body(request)
        if data is None:
            return JsonResponse({'success': False, 'error': '请求体必须是 JSON'}, status=400)

        fields = []
        params = []
        if 'start_date' in data:
            start_date = data.get('start_date')
            if start_date:
                try:
                    date.fromisoformat(str(start_date))
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'start_date 格式无效'}, status=400)
            fields.append('start_date = %s')
            params.append(start_date or None)
        if 'slogan' in data:
            fields.append('slogan = %s')
            params.append((data.get('slogan') or '').strip() or None)

        if not fields:
            return JsonResponse({'success': False, 'error': '没有可更新的字段'}, status=400)

        params.append(1)
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE love_nest_config SET {', '.join(fields)} WHERE id = %s",
                params,
            )

        payload, error = _build_config_payload()
        if error:
            return JsonResponse({'success': False, 'error': error}, status=404)
        return JsonResponse({'success': True, 'message': '更新成功', 'data': payload})
    except Exception:
        return _error_json('更新配置失败，请稍后重试', log_exc=True)


@csrf_exempt
@admin_required
@require_http_methods(['PUT'])
def update_members(request):
    try:
        data = _parse_json_body(request)
        if data is None:
            return JsonResponse({'success': False, 'error': '请求体必须是 JSON'}, status=400)

        member_user_ids = data.get('member_user_ids', [])
        if not isinstance(member_user_ids, list):
            return JsonResponse({'success': False, 'error': 'member_user_ids 必须是数组'}, status=400)

        normalized_ids = []
        for item in member_user_ids:
            try:
                normalized_ids.append(int(item))
            except (TypeError, ValueError):
                return JsonResponse({'success': False, 'error': 'member_user_ids 包含无效用户ID'}, status=400)

        with connection.cursor() as cursor:
            if normalized_ids:
                placeholders = ','.join(['%s'] * len(normalized_ids))
                cursor.execute(
                    f'SELECT COUNT(*) FROM users WHERE id IN ({placeholders})',
                    normalized_ids,
                )
                if cursor.fetchone()[0] != len(normalized_ids):
                    return JsonResponse({'success': False, 'error': '存在无效的用户ID'}, status=400)

            cursor.execute(
                'UPDATE love_nest_config SET member_user_ids = %s WHERE id = 1',
                [json.dumps(normalized_ids)],
            )

        payload, error = _build_config_payload()
        if error:
            return JsonResponse({'success': False, 'error': error}, status=404)
        return JsonResponse({'success': True, 'message': '更新成功', 'data': payload})
    except Exception:
        return _error_json('更新成员失败，请稍后重试', log_exc=True)


def _row_to_diary(row):
    photo_row = row[4:10] if row[2] and row[4] else None
    photo = _row_to_photo(photo_row) if photo_row else None
    return {
        'id': row[0],
        'diary_date': row[1].isoformat() if row[1] else None,
        'photo_id': row[2],
        'photo': photo,
        'image_url': photo['url'] if photo else None,
        'sentence': row[3],
    }


def _parse_diary_input(request):
    content_type = request.content_type or ''
    if 'multipart/form-data' in content_type:
        diary_date = (request.POST.get('diary_date') or '').strip()
        sentence = (request.POST.get('sentence') or '').strip()
        photo_id = (request.POST.get('photo_id') or '').strip() or None
        category = (request.POST.get('category') or '').strip() or None
        uploaded_file = request.FILES.get('file')
        return diary_date, sentence, photo_id, category, uploaded_file, None

    data = _parse_json_body(request)
    if data is None:
        return None, None, None, None, None, '请求体必须是 JSON 或 multipart/form-data'
    diary_date = (data.get('diary_date') or '').strip()
    sentence = (data.get('sentence') or data.get('content') or '').strip()
    photo_id = data.get('photo_id')
    category = data.get('category')
    return diary_date, sentence, photo_id, category, None, None


def _validate_diary_fields(diary_date, sentence):
    if not diary_date or not sentence:
        return '日期与一句话不能为空'
    if len(sentence) > 500:
        return '一句话不能超过500字'
    try:
        date.fromisoformat(diary_date)
    except ValueError:
        return 'diary_date 格式无效'
    return None


def _row_to_milestone(row):
    return {
        'id': row[0],
        'title': row[1],
        'milestone_date': row[2].isoformat() if row[2] else None,
        'description': row[3],
        'is_yearly': bool(row[4]),
        'sort_order': row[5],
    }


@csrf_exempt
@require_GET
def get_diaries(request):
    try:
        page = max(int(request.GET.get('page', 1)), 1)
        page_size = min(max(int(request.GET.get('page_size', 20)), 1), 100)
        offset = (page - 1) * page_size

        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM love_nest_diaries')
            total = cursor.fetchone()[0]
            cursor.execute(
                f"""
                {_DIARY_SELECT_SQL}
                ORDER BY d.diary_date ASC, d.id ASC
                LIMIT %s OFFSET %s
                """,
                [page_size, offset],
            )
            rows = cursor.fetchall()

        diaries = [_row_to_diary(row) for row in rows]
        total_pages = (total + page_size - 1) // page_size if total else 0
        return JsonResponse({
            'success': True,
            'data': {
                'diaries': diaries,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
            },
        })
    except Exception:
        return _error_json('获取时光失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_POST
def create_diary(request):
    try:
        diary_date, sentence, photo_id, category, uploaded_file, parse_error = _parse_diary_input(request)
        if parse_error:
            return JsonResponse({'success': False, 'error': parse_error}, status=400)

        field_error = _validate_diary_fields(diary_date, sentence)
        if field_error:
            return JsonResponse({'success': False, 'error': field_error}, status=400)

        try:
            resolved_photo_id = _resolve_diary_photo_id(
                photo_id,
                uploaded_file,
                category,
            )
        except ValueError as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO love_nest_diaries
                (diary_date, photo_id, sentence)
                VALUES (%s, %s, %s)
                """,
                [diary_date, resolved_photo_id, sentence],
            )
            diary_id = cursor.lastrowid
            cursor.execute(
                f"""
                {_DIARY_SELECT_SQL}
                WHERE d.id = %s
                """,
                [diary_id],
            )
            row = cursor.fetchone()

        return JsonResponse({'success': True, 'message': '创建成功', 'data': _row_to_diary(row)})
    except Exception:
        return _error_json('创建时光失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_http_methods(['PUT', 'POST'])
def update_diary(request, diary_id):
    try:
        content_type = request.content_type or ''
        uploaded_file = request.FILES.get('file') if 'multipart/form-data' in content_type else None

        if 'multipart/form-data' in content_type:
            data = request.POST
        else:
            data = _parse_json_body(request)
            if data is None:
                return JsonResponse({'success': False, 'error': '请求体必须是 JSON 或 multipart/form-data'}, status=400)

        fields = []
        params = []
        if 'sentence' in data or 'content' in data:
            sentence = (data.get('sentence') or data.get('content') or '').strip()
            if not sentence:
                return JsonResponse({'success': False, 'error': '一句话不能为空'}, status=400)
            if len(sentence) > 500:
                return JsonResponse({'success': False, 'error': '一句话不能超过500字'}, status=400)
            fields.append('sentence = %s')
            params.append(sentence)
        if 'diary_date' in data:
            diary_date = (data.get('diary_date') or '').strip()
            try:
                date.fromisoformat(diary_date)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'diary_date 格式无效'}, status=400)
            fields.append('diary_date = %s')
            params.append(diary_date)

        photo_id = data.get('photo_id') if hasattr(data, 'get') and data.get('photo_id') else None
        category = (data.get('category') or '').strip() if hasattr(data, 'get') and data.get('category') else None
        if photo_id or uploaded_file:
            try:
                resolved_photo_id = _resolve_diary_photo_id(
                    photo_id,
                    uploaded_file,
                    category,
                )
            except ValueError as exc:
                return JsonResponse({'success': False, 'error': str(exc)}, status=400)
            fields.append('photo_id = %s')
            params.append(resolved_photo_id)
        elif 'clear_image' in data and data.get('clear_image'):
            fields.append('photo_id = %s')
            params.append(None)

        if not fields:
            return JsonResponse({'success': False, 'error': '没有可更新的字段'}, status=400)

        params.append(diary_id)
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE love_nest_diaries SET {', '.join(fields)} WHERE id = %s",
                params,
            )
            if cursor.rowcount == 0:
                return JsonResponse({'success': False, 'error': '日记不存在'}, status=404)
            cursor.execute(
                f"""
                {_DIARY_SELECT_SQL}
                WHERE d.id = %s
                """,
                [diary_id],
            )
            row = cursor.fetchone()

        return JsonResponse({'success': True, 'message': '更新成功', 'data': _row_to_diary(row)})
    except Exception:
        return _error_json('更新时光失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_http_methods(['DELETE'])
def delete_diary(request, diary_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id FROM love_nest_diaries WHERE id = %s', [diary_id])
            if not cursor.fetchone():
                return JsonResponse({'success': False, 'error': '日记不存在'}, status=404)
            cursor.execute('DELETE FROM love_nest_diaries WHERE id = %s', [diary_id])
        return JsonResponse({'success': True, 'message': '删除成功'})
    except Exception:
        return _error_json('删除时光失败，请稍后重试', log_exc=True)


@csrf_exempt
@require_GET
def get_milestones(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, milestone_date, description, is_yearly, sort_order
                FROM love_nest_milestones
                ORDER BY sort_order DESC, milestone_date ASC, id ASC
                """
            )
            rows = cursor.fetchall()
        return JsonResponse({
            'success': True,
            'data': {'milestones': [_row_to_milestone(row) for row in rows]},
        })
    except Exception:
        return _error_json('获取纪念日失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_POST
def create_milestone(request):
    try:
        data = _parse_json_body(request)
        if data is None:
            return JsonResponse({'success': False, 'error': '请求体必须是 JSON'}, status=400)

        title = (data.get('title') or '').strip()
        milestone_date = (data.get('milestone_date') or '').strip()
        if not title or not milestone_date:
            return JsonResponse({'success': False, 'error': '标题与日期不能为空'}, status=400)
        try:
            date.fromisoformat(milestone_date)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'milestone_date 格式无效'}, status=400)

        description = (data.get('description') or '').strip() or None
        is_yearly = 1 if data.get('is_yearly', True) else 0
        sort_order = int(data.get('sort_order') or 0)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO love_nest_milestones
                (title, milestone_date, description, is_yearly, sort_order)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [title, milestone_date, description, is_yearly, sort_order],
            )
            milestone_id = cursor.lastrowid
            cursor.execute(
                """
                SELECT id, title, milestone_date, description, is_yearly, sort_order
                FROM love_nest_milestones WHERE id = %s
                """,
                [milestone_id],
            )
            row = cursor.fetchone()

        return JsonResponse({'success': True, 'message': '创建成功', 'data': _row_to_milestone(row)})
    except Exception:
        return _error_json('创建纪念日失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_http_methods(['PUT'])
def update_milestone(request, milestone_id):
    try:
        data = _parse_json_body(request)
        if data is None:
            return JsonResponse({'success': False, 'error': '请求体必须是 JSON'}, status=400)

        fields = []
        params = []
        if 'title' in data:
            title = (data.get('title') or '').strip()
            if not title:
                return JsonResponse({'success': False, 'error': '标题不能为空'}, status=400)
            fields.append('title = %s')
            params.append(title)
        if 'milestone_date' in data:
            milestone_date = (data.get('milestone_date') or '').strip()
            try:
                date.fromisoformat(milestone_date)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'milestone_date 格式无效'}, status=400)
            fields.append('milestone_date = %s')
            params.append(milestone_date)
        if 'description' in data:
            fields.append('description = %s')
            params.append((data.get('description') or '').strip() or None)
        if 'is_yearly' in data:
            fields.append('is_yearly = %s')
            params.append(1 if data.get('is_yearly') else 0)
        if 'sort_order' in data:
            fields.append('sort_order = %s')
            params.append(int(data.get('sort_order') or 0))

        if not fields:
            return JsonResponse({'success': False, 'error': '没有可更新的字段'}, status=400)

        params.append(milestone_id)
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE love_nest_milestones SET {', '.join(fields)} WHERE id = %s",
                params,
            )
            cursor.execute(
                """
                SELECT id, title, milestone_date, description, is_yearly, sort_order
                FROM love_nest_milestones WHERE id = %s
                """,
                [milestone_id],
            )
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '纪念日不存在'}, status=404)

        return JsonResponse({'success': True, 'message': '更新成功', 'data': _row_to_milestone(row)})
    except Exception:
        return _error_json('更新纪念日失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_http_methods(['DELETE'])
def delete_milestone(request, milestone_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM love_nest_milestones WHERE id = %s', [milestone_id])
            if cursor.rowcount == 0:
                return JsonResponse({'success': False, 'error': '纪念日不存在'}, status=404)
        return JsonResponse({'success': True, 'message': '删除成功'})
    except Exception:
        return _error_json('删除纪念日失败，请稍后重试', log_exc=True)


def _province_adcode_from_city(adcode, province_adcode=None):
    city_code = str(adcode or '').strip()
    province_code = str(province_adcode or '').strip()
    if len(city_code) >= 2:
        derived = f'{city_code[:2]}0000'
    else:
        derived = ''
    if province_code and len(province_code) == 6 and province_code.endswith('0000'):
        return province_code
    return derived


def _row_to_travel_city(row, photos=None):
    return {
        'id': row[0],
        'adcode': row[1],
        'province_adcode': _province_adcode_from_city(row[1], row[2]),
        'city_name': row[3],
        'note': row[4],
        'visited_at': row[5].isoformat() if row[5] else None,
        'photos': photos or [],
    }


def _fetch_travel_photos_by_city():
    photos_by_city = {}
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT {_PHOTO_SELECT_COLS}
            FROM love_nest_photos
            WHERE travel_city_id IS NOT NULL
            ORDER BY id DESC
            """
        )
        for row in cursor.fetchall():
            city_id = row[5]
            photos_by_city.setdefault(city_id, []).append(_row_to_photo(row))
    return photos_by_city


@csrf_exempt
@require_GET
def get_travel(request):
    try:
        photos_by_city = _fetch_travel_photos_by_city()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, adcode, province_adcode, city_name, note, visited_at
                FROM love_nest_travel_cities
                ORDER BY visited_at DESC, id DESC
                """
            )
            rows = cursor.fetchall()

        cities = []
        province_stats = {}
        for row in rows:
            city = _row_to_travel_city(row, photos_by_city.get(row[0], []))
            cities.append(city)
            province_code = _province_adcode_from_city(row[1], row[2])
            if province_code:
                province_stats[province_code] = province_stats.get(province_code, 0) + 1

        return JsonResponse({
            'success': True,
            'data': {
                'cities': cities,
                'province_stats': province_stats,
                'total_visited': len(cities),
            },
        })
    except Exception:
        return _error_json('获取旅行数据失败，请稍后重试', log_exc=True)


@csrf_exempt
@require_GET
def get_travel_city(request, city_id):
    try:
        photos_by_city = _fetch_travel_photos_by_city()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, adcode, province_adcode, city_name, note, visited_at
                FROM love_nest_travel_cities
                WHERE id = %s
                """,
                [city_id],
            )
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '城市不存在'}, status=404)

        return JsonResponse({
            'success': True,
            'data': _row_to_travel_city(row, photos_by_city.get(row[0], [])),
        })
    except Exception:
        return _error_json('获取城市详情失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_POST
def create_travel_city(request):
    try:
        data = _parse_json_body(request)
        if data is None:
            return JsonResponse({'success': False, 'error': '请求体必须是 JSON'}, status=400)

        adcode = (data.get('adcode') or '').strip()
        province_adcode = (data.get('province_adcode') or '').strip()
        city_name = (data.get('city_name') or '').strip()
        if not adcode or not city_name:
            return JsonResponse({'success': False, 'error': '请选择城市'}, status=400)

        province_adcode = _province_adcode_from_city(adcode, province_adcode)
        if not province_adcode:
            return JsonResponse({'success': False, 'error': '省份信息无效'}, status=400)

        note = (data.get('note') or '').strip() or None
        visited_at = (data.get('visited_at') or '').strip() or None
        if visited_at:
            try:
                date.fromisoformat(visited_at)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'visited_at 格式无效'}, status=400)

        photo_id = data.get('photo_id')
        photo_ids = data.get('photo_ids') or ([] if photo_id is None else [photo_id])

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO love_nest_travel_cities
                (adcode, province_adcode, city_name, note, visited_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [adcode, province_adcode, city_name, note, visited_at],
            )
            city_id = cursor.lastrowid

            for item in photo_ids:
                if item:
                    cursor.execute(
                        """
                        UPDATE love_nest_photos
                        SET travel_city_id = %s
                        WHERE id = %s
                        """,
                        [city_id, int(item)],
                    )

            cursor.execute(
                """
                SELECT id, adcode, province_adcode, city_name, note, visited_at
                FROM love_nest_travel_cities WHERE id = %s
                """,
                [city_id],
            )
            row = cursor.fetchone()

        photos_by_city = _fetch_travel_photos_by_city()
        return JsonResponse({
            'success': True,
            'message': '创建成功',
            'data': _row_to_travel_city(row, photos_by_city.get(city_id, [])),
        })
    except IntegrityError:
        return JsonResponse({'success': False, 'error': '该城市已添加过旅行记录'}, status=400)
    except Exception:
        return JsonResponse({'success': False, 'error': '创建旅行记录失败，请稍后重试'}, status=500)


@csrf_exempt
@love_nest_editor_required
@require_http_methods(['PUT'])
def update_travel_city(request, city_id):
    try:
        data = _parse_json_body(request)
        if data is None:
            return JsonResponse({'success': False, 'error': '请求体必须是 JSON'}, status=400)

        fields = []
        params = []
        for key, column in (
            ('city_name', 'city_name'),
            ('note', 'note'),
            ('visited_at', 'visited_at'),
        ):
            if key in data:
                value = (data.get(key) or '').strip() or None
                if key == 'visited_at' and value:
                    try:
                        date.fromisoformat(value)
                    except ValueError:
                        return JsonResponse({'success': False, 'error': 'visited_at 格式无效'}, status=400)
                fields.append(f'{column} = %s')
                params.append(value)

        if not fields and 'photo_ids' not in data:
            return JsonResponse({'success': False, 'error': '没有可更新的字段'}, status=400)

        with connection.cursor() as cursor:
            if fields:
                params.append(city_id)
                cursor.execute(
                    f"UPDATE love_nest_travel_cities SET {', '.join(fields)} WHERE id = %s",
                    params,
                )
                if cursor.rowcount == 0:
                    return JsonResponse({'success': False, 'error': '城市不存在'}, status=404)

            if 'photo_ids' in data:
                photo_ids = data.get('photo_ids') or []
                cursor.execute(
                    'UPDATE love_nest_photos SET travel_city_id = NULL WHERE travel_city_id = %s',
                    [city_id],
                )
                for item in photo_ids:
                    if item:
                        cursor.execute(
                            """
                            UPDATE love_nest_photos
                            SET travel_city_id = %s
                            WHERE id = %s
                            """,
                            [city_id, int(item)],
                        )

            cursor.execute(
                """
                SELECT id, adcode, province_adcode, city_name, note, visited_at
                FROM love_nest_travel_cities WHERE id = %s
                """,
                [city_id],
            )
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '城市不存在'}, status=404)

        photos_by_city = _fetch_travel_photos_by_city()
        return JsonResponse({
            'success': True,
            'message': '更新成功',
            'data': _row_to_travel_city(row, photos_by_city.get(city_id, [])),
        })
    except Exception:
        return _error_json('更新旅行记录失败，请稍后重试', log_exc=True)


@csrf_exempt
@love_nest_editor_required
@require_http_methods(['DELETE'])
def delete_travel_city(request, city_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id FROM love_nest_travel_cities WHERE id = %s', [city_id])
            if not cursor.fetchone():
                return JsonResponse({'success': False, 'error': '城市不存在'}, status=404)
            cursor.execute(
                'UPDATE love_nest_photos SET travel_city_id = NULL WHERE travel_city_id = %s',
                [city_id],
            )
            cursor.execute('DELETE FROM love_nest_travel_cities WHERE id = %s', [city_id])
        return JsonResponse({'success': True, 'message': '删除成功'})
    except Exception:
        return _error_json('删除旅行记录失败，请稍后重试', log_exc=True)
