import json
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from common.jwt_utils import jwt_required
from common.captcha_utils import CaptchaUtils
import time


@require_GET
def get_comments(request, article_id):
    """
    获取文章的所有评论
    按时间倒序排列（最新的在前）
    """
    try:
        with connection.cursor() as cursor:
            # 查询评论，关联用户表获取评论人信息
            cursor.execute("""
                SELECT 
                    c.id,
                    c.article_id,
                    c.user_id,
                    u.username as user_name,
                    u.avatar as user_avatar,
                    c.content,
                    c.created_at
                FROM article_comments c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE c.article_id = %s
                ORDER BY c.created_at DESC
            """, [article_id])
            
            rows = cursor.fetchall()
            
            comments = []
            for row in rows:
                comment = {
                    'id': row[0],
                    'article_id': row[1],
                    'user_id': row[2],
                    'user_name': row[3] if row[3] else '未知用户',
                    'user_avatar': row[4] if row[4] else None,
                    'content': row[5],
                    'created_at': row[6].isoformat() if row[6] else None
                }
                comments.append(comment)
            
            return JsonResponse({
                'success': True,
                'message': '获取评论列表成功',
                'data': {
                    'comments': comments,
                    'total': len(comments)
                }
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取评论列表失败: {str(e)}',
            'data': {
                'comments': [],
                'total': 0
            }
        }, status=500)


@csrf_exempt
@jwt_required
@require_POST
def create_comment(request, article_id):
    """
    创建评论
    需要JWT认证和验证码验证
    """
    try:
        # 获取用户ID（由JWT中间件设置）
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户未登录'
            }, status=401)
        
        # 解析请求数据
        data = json.loads(request.body.decode())
        content = data.get('content', '').strip()
        captcha_key = data.get('captcha_key', '')
        captcha_value = data.get('captcha_value', '')
        
        # 验证内容
        if not content:
            return JsonResponse({
                'success': False,
                'error': '评论内容不能为空'
            }, status=400)
        
        if len(content) > 200:
            return JsonResponse({
                'success': False,
                'error': '评论内容不能超过200个字符'
            }, status=400)
        
        # 检查文章是否存在
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM blog_articles WHERE id = %s", [article_id])
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': '文章不存在'
                }, status=404)
        
        # 检查发布限制（基于用户ID）
        identifier = f"comment_limit_user_{user_id}"
        lock_key = f"comment_lock_{identifier}"
        
        # 检查是否被锁定
        if cache.get(lock_key):
            lock_time = cache.get(f"{lock_key}_time", 0)
            remaining_seconds = 300 - (int(time.time()) - lock_time)
            if remaining_seconds > 0:
                minutes = remaining_seconds // 60
                seconds = remaining_seconds % 60
                return JsonResponse({
                    'success': False,
                    'error': f'评论失败次数过多，已被禁止评论5分钟，剩余时间：{minutes}分{seconds}秒'
                }, status=429)
            else:
                # 锁定时间已过，清除锁定
                cache.delete(lock_key)
                cache.delete(f"{lock_key}_time")
                cache.delete(f"comment_fail_{identifier}")
        
        # 验证验证码
        if not captcha_key or not captcha_value:
            # 记录失败次数
            fail_key = f"comment_fail_{identifier}"
            fail_count = cache.get(fail_key, 0)
            fail_count += 1
            
            if fail_count >= 5:
                # 锁定5分钟
                cache.set(lock_key, True, 300)  # 300秒 = 5分钟
                cache.set(f"{lock_key}_time", int(time.time()), 300)
                cache.delete(fail_key)
                return JsonResponse({
                    'success': False,
                    'error': '验证码错误次数过多，已被禁止评论5分钟'
                }, status=429)
            else:
                cache.set(fail_key, fail_count, 300)  # 失败计数5分钟内有效
                remaining = 5 - fail_count
                return JsonResponse({
                    'success': False,
                    'error': f'请输入验证码（剩余尝试次数：{remaining}）'
                }, status=400)
        
        # 验证验证码
        is_valid, message = CaptchaUtils.verify_captcha(captcha_key, captcha_value)
        if not is_valid:
            # 记录失败次数
            fail_key = f"comment_fail_{identifier}"
            fail_count = cache.get(fail_key, 0)
            fail_count += 1
            
            if fail_count >= 5:
                # 锁定5分钟
                cache.set(lock_key, True, 300)  # 300秒 = 5分钟
                cache.set(f"{lock_key}_time", int(time.time()), 300)
                cache.delete(fail_key)
                return JsonResponse({
                    'success': False,
                    'error': '验证码错误次数过多，已被禁止评论5分钟'
                }, status=429)
            else:
                cache.set(fail_key, fail_count, 300)  # 失败计数5分钟内有效
                remaining = 5 - fail_count
                return JsonResponse({
                    'success': False,
                    'error': f'{message}（剩余尝试次数：{remaining}）'
                }, status=400)
        
        # 验证码验证成功，清除失败计数
        fail_key = f"comment_fail_{identifier}"
        cache.delete(fail_key)
        
        # 写入数据库（触发器会自动更新文章的评论数）
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO article_comments (article_id, user_id, content, created_at)
                VALUES (%s, %s, %s, NOW())
            """, [article_id, user_id, content])
            
            comment_id = cursor.lastrowid
            
            return JsonResponse({
                'success': True,
                'message': '评论发布成功',
                'data': {
                    'comment_id': comment_id
                }
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'发布评论失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@require_http_methods(["DELETE"])
def delete_comment(request, article_id, comment_id):
    """
    删除评论
    只能删除自己的评论
    """
    try:
        # 获取用户ID（由JWT中间件设置）
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户未登录'
            }, status=401)
        
        with connection.cursor() as cursor:
            # 检查评论是否存在且属于当前用户
            cursor.execute("""
                SELECT id, user_id, article_id 
                FROM article_comments 
                WHERE id = %s AND article_id = %s
            """, [comment_id, article_id])
            row = cursor.fetchone()
            
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '评论不存在'
                }, status=404)
            
            if row[1] != user_id:
                return JsonResponse({
                    'success': False,
                    'error': '只能删除自己的评论'
                }, status=403)
            
            # 删除评论（触发器会自动更新文章的评论数）
            cursor.execute("DELETE FROM article_comments WHERE id = %s", [comment_id])
            
            return JsonResponse({
                'success': True,
                'message': '评论删除成功'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'删除评论失败: {str(e)}'
        }, status=500)

