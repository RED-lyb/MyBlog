"""
爱情小窝相关视图
"""
import json
import os
from datetime import date, datetime
from functools import wraps
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.db import connection
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
DIARY_DIR = PHOTOS_DIR / 'diary'

ALLOWED_IMAGE_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
PHOTO_UPLOAD_CATEGORIES = ('person', 'scenery', 'food')
PHOTO_QUERY_CATEGORIES = PHOTO_UPLOAD_CATEGORIES + ('travel',)
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_STORED_BYTES = 5 * 1024 * 1024


def _safe_basename(name):
    if not name or not isinstance(name, str):
        return None
    base = os.path.basename(name.strip())
    if not base or base in ('.', '..') or '..' in name:
        return None
    return base


def _image_ext_from_name(name):
    file_name = (name or '').lower()
    for ext in ALLOWED_IMAGE_EXT:
        if file_name.endswith(ext):
            return ext
    return None


def _compress_image_bytes(data, ext):
    if len(data) <= MAX_STORED_BYTES:
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
        if len(result) <= MAX_STORED_BYTES:
            return result, '.jpg'
        quality = max(50, quality - 8)
        scale *= 0.9

    if len(result) > MAX_UPLOAD_BYTES:
        raise ValueError('图片压缩后仍过大，请换一张较小的图片')
    return result, '.jpg'


def _save_uploaded_image(uploaded_file, dest_without_suffix):
    data = b''.join(uploaded_file.chunks())
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError('图片大小不能超过8MB')
    ext = _image_ext_from_name(uploaded_file.name)
    if not ext:
        raise ValueError(f'不支持的格式，仅支持: {", ".join(ALLOWED_IMAGE_EXT)}')
    data, save_ext = _compress_image_bytes(data, ext)
    dest_without_suffix.parent.mkdir(parents=True, exist_ok=True)
    dest_path = dest_without_suffix.with_suffix(save_ext)
    with open(dest_path, 'wb') as handle:
        handle.write(data)
    return dest_path.name


def _delete_diary_image(filename):
    safe_name = _safe_basename(filename)
    if not safe_name:
        return
    path = DIARY_DIR / safe_name
    if path.is_file():
        path.unlink()


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
            SELECT id, start_date, slogan, member_user_ids, updated_at
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
        'sort_order': row[6],
        'created_by': row[7],
        'created_at': row[8].isoformat() if row[8] else None,
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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'获取配置失败: {str(e)}'}, status=500)


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
        'updated_at': row[4].isoformat() if row[4] else None,
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
                ORDER BY sort_order DESC, id DESC
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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'获取漂浮素材失败: {str(e)}'}, status=500)


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
        if category in PHOTO_QUERY_CATEGORIES:
            where_conditions.append('category = %s')
            params.append(category)

        where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'

        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT COUNT(*) FROM love_nest_photos WHERE {where_clause}',
                params,
            )
            total = cursor.fetchone()[0]

            cursor.execute(
                f"""
                SELECT id, filename, title, caption, category, travel_city_id,
                       sort_order, created_by, created_at
                FROM love_nest_photos
                WHERE {where_clause}
                ORDER BY sort_order DESC, created_at DESC
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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'获取照片失败: {str(e)}'}, status=500)


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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'检查权限失败: {str(e)}'}, status=500)


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

        if uploaded_file.size > MAX_UPLOAD_BYTES:
            return JsonResponse({'success': False, 'error': '图片大小不能超过8MB'}, status=400)

        title = (request.POST.get('title') or '').strip() or None
        caption = (request.POST.get('caption') or '').strip() or None
        category = (request.POST.get('category') or '').strip()
        if category not in PHOTO_UPLOAD_CATEGORIES:
            return JsonResponse(
                {'success': False, 'error': '请选择分类：人物、风景或食物'},
                status=400,
            )
        sort_order = int(request.POST.get('sort_order', 0) or 0)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO love_nest_photos
                (filename, title, caption, category, sort_order, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                ['', title, caption, category, sort_order, request.user_id],
            )
            photo_id = cursor.lastrowid

        category_dir = PHOTOS_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)
        try:
            saved_name = _save_uploaded_image(uploaded_file, category_dir / str(int(photo_id)))
        except ValueError as exc:
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM love_nest_photos WHERE id = %s', [photo_id])
            return JsonResponse({'success': False, 'error': str(exc)}, status=400)

        relative_filename = f'{category}/{saved_name}'

        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE love_nest_photos SET filename = %s WHERE id = %s',
                [relative_filename, photo_id],
            )
            cursor.execute(
                """
                SELECT id, filename, title, caption, category, travel_city_id,
                       sort_order, created_by, created_at
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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'上传失败: {str(e)}'}, status=500)


@csrf_exempt
@love_nest_editor_required
@require_http_methods(['PUT'])
def update_photo(request, photo_id):
    try:
        data = _parse_json_body(request)
        if data is None:
            return JsonResponse({'success': False, 'error': '请求体必须是 JSON'}, status=400)

        fields = []
        params = []
        if 'title' in data:
            fields.append('title = %s')
            params.append((data.get('title') or '').strip() or None)
        if 'caption' in data:
            fields.append('caption = %s')
            params.append((data.get('caption') or '').strip() or None)
        if 'category' in data and data.get('category') in PHOTO_QUERY_CATEGORIES:
            fields.append('category = %s')
            params.append(data['category'])
        if 'sort_order' in data:
            fields.append('sort_order = %s')
            params.append(int(data.get('sort_order') or 0))

        if not fields:
            return JsonResponse({'success': False, 'error': '没有可更新的字段'}, status=400)

        params.append(photo_id)
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE love_nest_photos SET {', '.join(fields)} WHERE id = %s",
                params,
            )
            cursor.execute(
                """
                SELECT id, filename, title, caption, category, travel_city_id,
                       sort_order, created_by, created_at
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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'更新失败: {str(e)}'}, status=500)


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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'删除失败: {str(e)}'}, status=500)


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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'更新配置失败: {str(e)}'}, status=500)


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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'更新成员失败: {str(e)}'}, status=500)


def _row_to_diary(row):
    image_filename = row[2]
    return {
        'id': row[0],
        'diary_date': row[1].isoformat() if row[1] else None,
        'image_filename': image_filename,
        'image_url': f'/api/static/love_nest/photos/diary/{image_filename}' if image_filename else None,
        'sentence': row[3],
        'created_by': row[4],
        'created_at': row[5].isoformat() if row[5] else None,
        'updated_at': row[6].isoformat() if row[6] else None,
    }


def _parse_diary_input(request):
    content_type = request.content_type or ''
    if 'multipart/form-data' in content_type:
        diary_date = (request.POST.get('diary_date') or '').strip()
        sentence = (request.POST.get('sentence') or '').strip()
        uploaded_file = request.FILES.get('file')
        return diary_date, sentence, uploaded_file, None

    data = _parse_json_body(request)
    if data is None:
        return None, None, None, '请求体必须是 JSON 或 multipart/form-data'
    diary_date = (data.get('diary_date') or '').strip()
    sentence = (data.get('sentence') or data.get('content') or '').strip()
    return diary_date, sentence, None, None


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
        'created_at': row[6].isoformat() if row[6] else None,
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
                """
                SELECT id, diary_date, image_filename, sentence,
                       created_by, created_at, updated_at
                FROM love_nest_diaries
                ORDER BY diary_date ASC, id ASC
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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'获取日记失败: {str(e)}'}, status=500)


@csrf_exempt
@love_nest_editor_required
@require_POST
def create_diary(request):
    try:
        diary_date, sentence, uploaded_file, parse_error = _parse_diary_input(request)
        if parse_error:
            return JsonResponse({'success': False, 'error': parse_error}, status=400)

        field_error = _validate_diary_fields(diary_date, sentence)
        if field_error:
            return JsonResponse({'success': False, 'error': field_error}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO love_nest_diaries
                (diary_date, image_filename, sentence, created_by)
                VALUES (%s, %s, %s, %s)
                """,
                [diary_date, None, sentence, request.user_id],
            )
            diary_id = cursor.lastrowid

        image_filename = None
        if uploaded_file:
            try:
                image_filename = _save_uploaded_image(uploaded_file, DIARY_DIR / str(int(diary_id)))
            except ValueError as exc:
                with connection.cursor() as cursor:
                    cursor.execute('DELETE FROM love_nest_diaries WHERE id = %s', [diary_id])
                return JsonResponse({'success': False, 'error': str(exc)}, status=400)
            with connection.cursor() as cursor:
                cursor.execute(
                    'UPDATE love_nest_diaries SET image_filename = %s WHERE id = %s',
                    [image_filename, diary_id],
                )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, diary_date, image_filename, sentence,
                       created_by, created_at, updated_at
                FROM love_nest_diaries WHERE id = %s
                """,
                [diary_id],
            )
            row = cursor.fetchone()

        return JsonResponse({'success': True, 'message': '创建成功', 'data': _row_to_diary(row)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'创建日记失败: {str(e)}'}, status=500)


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

        old_image_filename = None
        new_image_filename = None
        if uploaded_file:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT image_filename FROM love_nest_diaries WHERE id = %s',
                    [diary_id],
                )
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({'success': False, 'error': '日记不存在'}, status=404)
                old_image_filename = row[0]
            try:
                new_image_filename = _save_uploaded_image(uploaded_file, DIARY_DIR / str(int(diary_id)))
            except ValueError as exc:
                return JsonResponse({'success': False, 'error': str(exc)}, status=400)
            fields.append('image_filename = %s')
            params.append(new_image_filename)

        if not fields:
            return JsonResponse({'success': False, 'error': '没有可更新的字段'}, status=400)

        params.append(diary_id)
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE love_nest_diaries SET {', '.join(fields)} WHERE id = %s",
                params,
            )
            if cursor.rowcount == 0:
                if new_image_filename:
                    _delete_diary_image(new_image_filename)
                return JsonResponse({'success': False, 'error': '日记不存在'}, status=404)
            cursor.execute(
                """
                SELECT id, diary_date, image_filename, sentence,
                       created_by, created_at, updated_at
                FROM love_nest_diaries WHERE id = %s
                """,
                [diary_id],
            )
            row = cursor.fetchone()

        if old_image_filename and new_image_filename and old_image_filename != new_image_filename:
            _delete_diary_image(old_image_filename)

        return JsonResponse({'success': True, 'message': '更新成功', 'data': _row_to_diary(row)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'更新日记失败: {str(e)}'}, status=500)


@csrf_exempt
@love_nest_editor_required
@require_http_methods(['DELETE'])
def delete_diary(request, diary_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT image_filename FROM love_nest_diaries WHERE id = %s',
                [diary_id],
            )
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '日记不存在'}, status=404)
            image_filename = row[0]
            cursor.execute('DELETE FROM love_nest_diaries WHERE id = %s', [diary_id])

        _delete_diary_image(image_filename)
        return JsonResponse({'success': True, 'message': '删除成功'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'删除日记失败: {str(e)}'}, status=500)


@csrf_exempt
@require_GET
def get_milestones(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, milestone_date, description, is_yearly,
                       sort_order, created_at
                FROM love_nest_milestones
                ORDER BY sort_order DESC, milestone_date ASC, id ASC
                """
            )
            rows = cursor.fetchall()
        return JsonResponse({
            'success': True,
            'data': {'milestones': [_row_to_milestone(row) for row in rows]},
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'获取纪念日失败: {str(e)}'}, status=500)


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
                SELECT id, title, milestone_date, description, is_yearly,
                       sort_order, created_at
                FROM love_nest_milestones WHERE id = %s
                """,
                [milestone_id],
            )
            row = cursor.fetchone()

        return JsonResponse({'success': True, 'message': '创建成功', 'data': _row_to_milestone(row)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'创建纪念日失败: {str(e)}'}, status=500)


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
                SELECT id, title, milestone_date, description, is_yearly,
                       sort_order, created_at
                FROM love_nest_milestones WHERE id = %s
                """,
                [milestone_id],
            )
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': '纪念日不存在'}, status=404)

        return JsonResponse({'success': True, 'message': '更新成功', 'data': _row_to_milestone(row)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'更新纪念日失败: {str(e)}'}, status=500)


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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'删除纪念日失败: {str(e)}'}, status=500)
