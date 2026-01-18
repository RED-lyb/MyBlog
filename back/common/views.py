from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
from common.jwt_utils import jwt_required
from common.captcha_utils import captcha_required
from common.user_relation_utils import follow_user, unfollow_user, is_following
import os
import json
from pathlib import Path


@csrf_exempt
def get_user_info(request):
    """
    全局用户信息接口
    返回当前登录用户的详细信息，或访客状态
    适用于所有需要获取用户信息的场景
    """
    # 检查用户是否已认证（由 JWT 中间件设置）
    is_authenticated = getattr(request, 'is_authenticated', False)
    user_id = getattr(request, 'user_id', None)
    username = getattr(request, 'username', None)
    
    if is_authenticated and user_id and username:
        # 用户已登录，获取用户详细信息
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, protect, registered_time, avatar, bg_color, bg_pattern, bio,
                           follow_count, article_count, liked_article_count, follower_count, is_admin
                    FROM users WHERE id = %s
                """, [user_id])
                row = cursor.fetchone()
                
                if row:
                    user_data = {
                        'id': row[0],
                        'username': row[1],
                        'protect': row[2],
                        'registered_time': row[3].isoformat() if row[3] else None,
                        'avatar': row[4],
                        'bg_color': row[5],
                        'bg_pattern': row[6],
                        'bio': row[7],
                        'follow_count': row[8] if len(row) > 8 else 0,
                        'article_count': row[9] if len(row) > 9 else 0,
                        'liked_article_count': row[10] if len(row) > 10 else 0,
                        'follower_count': row[11] if len(row) > 11 else 0,
                        'is_admin': bool(row[12]) if len(row) > 12 and row[12] is not None else False
                    }
                    
                    return JsonResponse({
                        'success': True,
                        'message': '获取用户信息成功',
                        'data': {
                            'user': user_data,
                            'is_authenticated': True
                        }
                    })
                else:
                    # 用户不存在
                    return JsonResponse({
                        'success': False,
                        'error': '用户信息不存在',
                        'data': {
                            'is_authenticated': False
                        }
                    }, status=404)
                    
        except Exception:
            return JsonResponse({
                'success': False,
                'error': '获取用户信息失败',
                'data': {
                    'is_authenticated': False
                }
            }, status=500)
    else:
        # 访客模式
            return JsonResponse({
                'success': True,
                'message': '访客模式',
                'data': {
                    'user': None,
                    'is_authenticated': False
                }
            })


@csrf_exempt
def get_user_by_id(request, user_id):
    """
    根据用户ID获取用户信息（公开接口，不需要认证）
    用于访问其他用户的主页
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, protect, registered_time, avatar, bg_color, bg_pattern, bio,
                       follow_count, article_count, liked_article_count, follower_count
                FROM users WHERE id = %s
            """, [user_id])
            row = cursor.fetchone()
            
            if row:
                user_data = {
                    'id': row[0],
                    'username': row[1],
                    'protect': row[2],
                    'registered_time': row[3].isoformat() if row[3] else None,
                    'avatar': row[4],
                    'bg_color': row[5],
                    'bg_pattern': row[6],
                    'bio': row[7],
                    'follow_count': row[8] if len(row) > 8 else 0,
                    'article_count': row[9] if len(row) > 9 else 0,
                    'liked_article_count': row[10] if len(row) > 10 else 0,
                    'follower_count': row[11] if len(row) > 11 else 0
                }
                
                return JsonResponse({
                    'success': True,
                    'message': '获取用户信息成功',
                    'data': {
                        'user': user_data
                    }
                })
            else:
                # 用户不存在
                return JsonResponse({
                    'success': False,
                    'error': '用户不存在',
                    'data': None
                }, status=404)
                
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取用户信息失败: {str(e)}',
            'data': None
        }, status=500)


@csrf_exempt
@jwt_required
@require_http_methods(["POST"])
def toggle_follow(request, user_id):
    """
    关注/取消关注用户
    """
    try:
        current_user_id = getattr(request, 'user_id', None)
        if not current_user_id:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401)
        
        target_user_id = int(user_id)
        
        if current_user_id == target_user_id:
            return JsonResponse({
                'success': False,
                'error': '不能关注自己'
            }, status=400)
        
        # 检查是否已关注
        is_following_user = is_following(current_user_id, target_user_id)
        
        if is_following_user:
            # 取消关注
            success, message = unfollow_user(current_user_id, target_user_id)
        else:
            # 关注
            success, message = follow_user(current_user_id, target_user_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'data': {
                    'is_following': not is_following_user
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': message
            }, status=400)
            
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'操作失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def check_follow_status(request, user_id):
    """
    检查当前用户是否关注了指定用户（需要认证，但访客也可以调用，返回False）
    """
    try:
        current_user_id = getattr(request, 'user_id', None)
        target_user_id = int(user_id)
        
        if not current_user_id:
            return JsonResponse({
                'success': True,
                'data': {
                    'is_following': False
                }
            })
        
        is_following_user = is_following(current_user_id, target_user_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'is_following': is_following_user
            }
        })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'检查失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@require_http_methods(["POST"])
def upload_avatar(request):
    """
    上传用户头像
    仅限常见图片格式，保存为 {user_id}.{ext}
    """
    try:
        current_user_id = getattr(request, 'user_id', None)
        if not current_user_id:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401)
        
        # 检查是否有文件
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '没有上传文件'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        
        # 验证文件类型
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        file_name = uploaded_file.name.lower()
        file_ext = None
        
        for ext in allowed_extensions:
            if file_name.endswith(ext):
                file_ext = ext
                break
        
        if not file_ext:
            return JsonResponse({
                'success': False,
                'error': f'不支持的文件格式，仅支持: {", ".join(allowed_extensions)}'
            }, status=400)
        
        # 验证文件大小（限制为5MB）
        max_size = 5 * 1024 * 1024  # 5MB
        if uploaded_file.size > max_size:
            return JsonResponse({
                'success': False,
                'error': '文件大小不能超过5MB'
            }, status=400)
        
        # 构建保存路径
        BASE_DIR = Path(__file__).resolve().parent.parent
        avatar_dir = BASE_DIR / 'api' / 'static' / 'user_heads'
        avatar_dir.mkdir(parents=True, exist_ok=True)
        
        # 删除旧头像（如果存在）- 仅根据用户ID，不根据扩展名
        import glob
        old_avatar_pattern = str(avatar_dir / f'{current_user_id}.*')
        for old_avatar_path in glob.glob(old_avatar_pattern):
            try:
                Path(old_avatar_path).unlink()
            except Exception:
                pass
        
        # 保存新头像
        avatar_filename = f'{current_user_id}{file_ext}'
        avatar_path = avatar_dir / avatar_filename
        
        with open(avatar_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        # 更新数据库中的avatar字段（只保存扩展名，如 .jpg）
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET avatar = %s WHERE id = %s",
                [file_ext, current_user_id]
            )
        
        return JsonResponse({
            'success': True,
            'message': '头像上传成功',
            'data': {
                'avatar': file_ext,
                'avatar_url': f'/api/static/user_heads/{avatar_filename}'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'上传失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@require_http_methods(["POST"])
def update_profile(request):
    """
    更新用户资料（bg_color, bg_pattern, bio）
    """
    try:
        current_user_id = getattr(request, 'user_id', None)
        if not current_user_id:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401)
        
        data = json.loads(request.body.decode())
        bg_color = data.get('bg_color', '').strip()
        bg_pattern = data.get('bg_pattern', '').strip()
        bio = data.get('bio', '').strip()
        
        # 构建更新SQL
        updates = []
        params = []
        
        if bg_color is not None:
            updates.append('bg_color = %s')
            params.append(bg_color if bg_color else None)
        
        if bg_pattern is not None:
            updates.append('bg_pattern = %s')
            params.append(bg_pattern if bg_pattern else None)
        
        if 'bio' in data:
            updates.append('bio = %s')
            params.append(bio if bio else None)
        
        if not updates:
            return JsonResponse({
                'success': False,
                'error': '没有要更新的字段'
            }, status=400)
        
        params.append(current_user_id)
        
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = %s",
                params
            )
        
        return JsonResponse({
            'success': True,
            'message': '资料更新成功'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'更新失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_user_following_list(request, user_id):
    """
    获取用户关注的人列表
    """
    try:
        target_user_id = int(user_id)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.username, u.avatar, u.registered_time,
                       u.follow_count, u.article_count, u.liked_article_count, u.follower_count
                FROM users u
                INNER JOIN user_follows uf ON u.id = uf.following_id
                WHERE uf.follower_id = %s
                ORDER BY uf.created_at DESC
            """, [target_user_id])
            rows = cursor.fetchall()
            
            following_list = []
            for row in rows:
                following_list.append({
                    'id': row[0],
                    'username': row[1],
                    'avatar': row[2],
                    'registered_time': row[3].isoformat() if row[3] else None,
                    'follow_count': row[4] if len(row) > 4 else 0,
                    'article_count': row[5] if len(row) > 5 else 0,
                    'liked_article_count': row[6] if len(row) > 6 else 0,
                    'follower_count': row[7] if len(row) > 7 else 0
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'following_list': following_list,
                    'total': len(following_list)
                }
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取关注列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_user_followers_list(request, user_id):
    """
    获取用户的粉丝列表
    """
    try:
        target_user_id = int(user_id)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.username, u.avatar, u.registered_time,
                       u.follow_count, u.article_count, u.liked_article_count, u.follower_count
                FROM users u
                INNER JOIN user_follows uf ON u.id = uf.follower_id
                WHERE uf.following_id = %s
                ORDER BY uf.created_at DESC
            """, [target_user_id])
            rows = cursor.fetchall()
            
            followers_list = []
            for row in rows:
                followers_list.append({
                    'id': row[0],
                    'username': row[1],
                    'avatar': row[2],
                    'registered_time': row[3].isoformat() if row[3] else None,
                    'follow_count': row[4] if len(row) > 4 else 0,
                    'article_count': row[5] if len(row) > 5 else 0,
                    'liked_article_count': row[6] if len(row) > 6 else 0,
                    'follower_count': row[7] if len(row) > 7 else 0
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'followers_list': followers_list,
                    'total': len(followers_list)
                }
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取粉丝列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_user_liked_articles_list(request, user_id):
    """
    获取用户喜欢的文章列表
    """
    try:
        target_user_id = int(user_id)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ba.id, ba.title, ba.content, ba.author_id, ba.view_count,
                       ba.love_count, ba.comment_count, ba.published_at,
                       u.username as author_name
                FROM blog_articles ba
                INNER JOIN user_liked_articles ula ON ba.id = ula.article_id
                INNER JOIN users u ON ba.author_id = u.id
                WHERE ula.user_id = %s
                ORDER BY ula.created_at DESC
            """, [target_user_id])
            rows = cursor.fetchall()
            
            articles_list = []
            for row in rows:
                articles_list.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2][:200] if row[2] else '',  # 只返回前200字符
                    'author_id': row[3],
                    'author_name': row[8],
                    'view_count': row[4] if len(row) > 4 else 0,
                    'love_count': row[5] if len(row) > 5 else 0,
                    'comment_count': row[6] if len(row) > 6 else 0,
                    'published_at': row[7].isoformat() if row[7] else None
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'articles_list': articles_list,
                    'total': len(articles_list)
                }
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取喜欢的文章列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_user_articles_list(request, user_id):
    """
    获取用户发布的文章列表
    """
    try:
        target_user_id = int(user_id)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, content, author_id, view_count,
                       love_count, comment_count, published_at
                FROM blog_articles
                WHERE author_id = %s
                ORDER BY published_at DESC
            """, [target_user_id])
            rows = cursor.fetchall()
            
            articles_list = []
            for row in rows:
                articles_list.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2][:200] if row[2] else '',  # 只返回前200字符
                    'author_id': row[3],
                    'view_count': row[4] if len(row) > 4 else 0,
                    'love_count': row[5] if len(row) > 5 else 0,
                    'comment_count': row[6] if len(row) > 6 else 0,
                    'published_at': row[7].isoformat() if row[7] else None
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'articles_list': articles_list,
                    'total': len(articles_list)
                }
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取文章列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@captcha_required
@require_http_methods(["POST"])
def reset_password(request):
    """
    重设密码（需要验证旧密码和验证码）
    """
    try:
        current_user_id = getattr(request, 'user_id', None)
        if not current_user_id:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401)
        
        data = json.loads(request.body.decode())
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return JsonResponse({
                'success': False,
                'error': '旧密码和新密码不能为空',
                'field_errors': {
                    'old_password': '请输入旧密码' if not old_password else '',
                    'new_password': '请输入新密码' if not new_password else ''
                }
            }, status=400)
        
        # 验证新密码格式（与注册时一致）
        from register.views import _validate_password
        password_error = _validate_password(new_password)
        if password_error:
            return JsonResponse({
                'success': False,
                'error': password_error,
                'field_errors': {
                    'new_password': password_error
                }
            }, status=400)
        
        # 验证旧密码
        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE id = %s", [current_user_id])
            row = cursor.fetchone()
            
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '用户不存在'
                }, status=404)
            
            stored_password = row[0]
            if not check_password(old_password, stored_password):
                return JsonResponse({
                    'success': False,
                    'error': '旧密码错误'
                }, status=400)
            
            # 更新密码
            hashed_password = make_password(new_password)
            cursor.execute(
                "UPDATE users SET password = %s WHERE id = %s",
                [hashed_password, current_user_id]
            )
        
        return JsonResponse({
            'success': True,
            'message': '密码修改成功'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'修改失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@captcha_required
@require_http_methods(["POST"])
def reset_security_question(request):
    """
    重设密保问题和答案（需要验证原密保答案和验证码）
    """
    try:
        current_user_id = getattr(request, 'user_id', None)
        if not current_user_id:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401)
        
        data = json.loads(request.body.decode())
        old_answer = data.get('old_answer', '').strip()
        new_protect = data.get('new_protect', '').strip()
        new_answer = data.get('new_answer', '').strip()
        
        # 验证输入
        if not old_answer or not new_protect or not new_answer:
            return JsonResponse({
                'success': False,
                'error': '原密保答案、新密保问题和新密保答案不能为空',
                'field_errors': {
                    'old_answer': '请输入原密保答案' if not old_answer else '',
                    'new_protect': '请选择或输入新密保问题' if not new_protect else '',
                    'new_answer': '请输入新密保答案' if not new_answer else ''
                }
            }, status=400)
        
        # 验证新密保问题格式（允许自定义问题，与注册时一致）
        import re
        if not re.fullmatch(r'[\u4e00-\u9fa5A-Za-z0-9]+', new_protect):
            return JsonResponse({
                'success': False,
                'error': '密保问题只能包含中文、英文和数字',
                'field_errors': {
                    'new_protect': '密保问题只能包含中文、英文和数字'
                }
            }, status=400)
        
        # 验证新密保答案格式
        from register.views import _validate_answer
        answer_error = _validate_answer(new_answer)
        if answer_error:
            return JsonResponse({
                'success': False,
                'error': answer_error,
                'field_errors': {
                    'new_answer': answer_error
                }
            }, status=400)
        
        # 验证原密保答案
        with connection.cursor() as cursor:
            cursor.execute("SELECT answer FROM users WHERE id = %s", [current_user_id])
            row = cursor.fetchone()
            
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '用户不存在'
                }, status=404)
            
            stored_answer_hash = row[0]
            if not check_password(old_answer, stored_answer_hash):
                return JsonResponse({
                    'success': False,
                    'error': '原密保答案错误',
                    'field_errors': {
                        'old_answer': '原密保答案错误'
                    }
                }, status=400)
            
            # 更新密保问题和答案
            hashed_new_answer = make_password(new_answer)
            cursor.execute(
                "UPDATE users SET protect = %s, answer = %s WHERE id = %s",
                [new_protect, hashed_new_answer, current_user_id]
            )
        
        return JsonResponse({
            'success': True,
            'message': '密保设置成功'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'设置失败: {str(e)}'
        }, status=500)
