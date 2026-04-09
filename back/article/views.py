import json
import time
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from common.jwt_utils import jwt_required
from common.captcha_utils import CaptchaUtils, LoginLimitUtils
from common.article_content_sanitize import sanitize_article_content_embeds


@require_GET
def get_all_articles(request):
    """
    获取文章列表（支持分页、筛选和排序）
    返回分页后的文章信息
    """
    try:
        # 获取分页参数
        page = int(request.GET.get('page', 1))  # 当前页码，默认第1页
        page_size = int(request.GET.get('page_size', 3))  # 每页数量，默认3条
        
        # 确保页码和每页数量有效
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 3
        
        # 获取筛选参数
        author_id = request.GET.get('author_id', '').strip()
        author_name = request.GET.get('author_name', '').strip()
        title = request.GET.get('title', '').strip()
        start_date = request.GET.get('start_date', '').strip()
        end_date = request.GET.get('end_date', '').strip()
        
        # 获取排序参数
        sort_by = request.GET.get('sort_by', 'published_at')  # 默认按发布时间排序
        sort_order = request.GET.get('sort_order', 'desc')  # 默认降序
        
        # 验证排序字段
        valid_sort_fields = ['published_at', 'view_count', 'love_count', 'comment_count']
        if sort_by not in valid_sort_fields:
            sort_by = 'published_at'
        
        # 验证排序方向
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        # 构建 WHERE 条件
        where_conditions = []
        params = []
        
        if author_id:
            try:
                author_id_int = int(author_id)
                where_conditions.append("a.author_id = %s")
                params.append(author_id_int)
            except ValueError:
                pass  # 如果 author_id 不是有效整数，忽略
        
        if author_name:
            where_conditions.append("u.username LIKE %s")
            params.append(f'%{author_name}%')
        
        if title:
            where_conditions.append("a.title LIKE %s")
            params.append(f'%{title}%')
        
        if start_date:
            where_conditions.append("DATE(a.published_at) >= %s")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("DATE(a.published_at) <= %s")
            params.append(end_date)
        
        # 构建 WHERE 子句
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # 构建 ORDER BY 子句
        order_clause = f"ORDER BY a.{sort_by} {sort_order.upper()}"
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        with connection.cursor() as cursor:
            # 先查询总记录数
            count_sql = f"""
                SELECT COUNT(*) 
                FROM blog_articles a
                LEFT JOIN users u ON a.author_id = u.id
                {where_clause}
            """
            cursor.execute(count_sql, params)
            total_count = cursor.fetchone()[0]
            
            # 查询分页后的文章，并关联用户表获取作者用户名和头像
            query_sql = f"""
                SELECT 
                    a.id,
                    a.title,
                    a.content,
                    a.author_id,
                    u.username as author_name,
                    u.avatar as author_avatar,
                    a.view_count,
                    a.love_count,
                    a.comment_count,
                    a.published_at
                FROM blog_articles a
                LEFT JOIN users u ON a.author_id = u.id
                {where_clause}
                {order_clause}
                LIMIT %s OFFSET %s
            """
            query_params = params + [page_size, offset]
            cursor.execute(query_sql, query_params)
            
            rows = cursor.fetchall()
            
            articles = []
            for row in rows:
                article = {
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'author_id': row[3],
                    'author_name': row[4] if row[4] else '未知用户',
                    'author_avatar': row[5] if row[5] else None,
                    'view_count': row[6],
                    'love_count': row[7],
                    'comment_count': row[8],
                    'published_at': row[9].isoformat() if row[9] else None
                }
                articles.append(article)
            
            return JsonResponse({
                'success': True,
                'message': '获取文章列表成功',
                'data': {
                    'articles': articles,
                    'total': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size  # 向上取整
                }
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取文章列表失败: {str(e)}',
            'data': {
                'articles': [],
                'total': 0,
                'page': 1,
                'page_size': 4,
                'total_pages': 0
            }
        }, status=500)


@require_GET
def get_article_detail(request, article_id):
    """
    获取文章详情
    根据文章ID返回文章的完整信息
    """
    try:
        with connection.cursor() as cursor:

            # 增加浏览量
            cursor.execute("""
                UPDATE blog_articles 
                SET view_count = view_count + 1 
                WHERE id = %s
            """, [article_id])

            # 查询文章详情，并关联用户表获取作者信息
            cursor.execute("""
                SELECT 
                    a.id,
                    a.title,
                    a.content,
                    a.author_id,
                    u.username as author_name,
                    u.avatar as author_avatar,
                    a.view_count,
                    a.love_count,
                    a.comment_count,
                    a.published_at
                FROM blog_articles a
                LEFT JOIN users u ON a.author_id = u.id
                WHERE a.id = %s
            """, [article_id])
            
            row = cursor.fetchone()
            
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '文章不存在',
                    'data': None
                }, status=404)
            
            article = {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'author_id': row[3],
                'author_name': row[4] if row[4] else '未知用户',
                'author_avatar': row[5] if row[5] else None,
                'view_count': row[6],
                'love_count': row[7],
                'comment_count': row[8],
                'published_at': row[9].isoformat() if row[9] else None
            }
            

            
            return JsonResponse({
                'success': True,
                'message': '获取文章详情成功',
                'data': article
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取文章详情失败: {str(e)}',
            'data': None
        }, status=500)


@csrf_exempt
@jwt_required
@require_POST
def create_article(request):
    """
    创建文章
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
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        captcha_key = data.get('captcha_key', '')
        captcha_value = data.get('captcha_value', '')
        
        # 验证标题
        if not title:
            return JsonResponse({
                'success': False,
                'error': '文章标题不能为空'
            }, status=400)
        
        if len(title) > 500:
            return JsonResponse({
                'success': False,
                'error': '文章标题不能超过500个字符'
            }, status=400)
        
        # 验证内容
        if not content:
            return JsonResponse({
                'success': False,
                'error': '文章内容不能为空'
            }, status=400)
        
        # 检查发布限制（基于用户ID）
        identifier = f"publish_limit_user_{user_id}"
        lock_key = f"publish_lock_{identifier}"
        
        # 检查是否被锁定
        if cache.get(lock_key):
            lock_time = cache.get(f"{lock_key}_time", 0)
            remaining_seconds = 300 - (int(time.time()) - lock_time)
            if remaining_seconds > 0:
                minutes = remaining_seconds // 60
                seconds = remaining_seconds % 60
                return JsonResponse({
                    'success': False,
                    'error': f'发布失败次数过多，已被禁止发布5分钟，剩余时间：{minutes}分{seconds}秒'
                }, status=429)
            else:
                # 锁定时间已过，清除锁定
                cache.delete(lock_key)
                cache.delete(f"{lock_key}_time")
                cache.delete(f"publish_fail_{identifier}")
        
        # 验证验证码
        if not captcha_key or not captcha_value:
            # 记录失败次数
            fail_key = f"publish_fail_{identifier}"
            fail_count = cache.get(fail_key, 0)
            fail_count += 1
            
            if fail_count >= 5:
                # 锁定5分钟
                cache.set(lock_key, True, 300)  # 300秒 = 5分钟
                cache.set(f"{lock_key}_time", int(time.time()), 300)
                cache.delete(fail_key)
                return JsonResponse({
                    'success': False,
                    'error': '验证码错误次数过多，已被禁止发布5分钟'
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
            fail_key = f"publish_fail_{identifier}"
            fail_count = cache.get(fail_key, 0)
            fail_count += 1
            
            if fail_count >= 5:
                # 锁定5分钟
                cache.set(lock_key, True, 300)  # 300秒 = 5分钟
                cache.set(f"{lock_key}_time", int(time.time()), 300)
                cache.delete(fail_key)
                return JsonResponse({
                    'success': False,
                    'error': '验证码错误次数过多，已被禁止发布5分钟'
                }, status=429)
            else:
                cache.set(fail_key, fail_count, 300)  # 失败计数5分钟内有效
                remaining = 5 - fail_count
                return JsonResponse({
                    'success': False,
                    'error': f'{message}（剩余尝试次数：{remaining}）'
                }, status=400)
        
        # 验证码验证成功，清除失败计数
        fail_key = f"publish_fail_{identifier}"
        cache.delete(fail_key)
        
        # Markdown 正文原样存储；对 [embed:html:...] 内联 HTML 用 bleach 做结构清洗（去 on*、危险协议、嵌套 iframe 等）
        content = sanitize_article_content_embeds(content)
        
        # 写入数据库（触发器会自动更新用户的文章数）
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO blog_articles (title, content, author_id, view_count, love_count, comment_count, published_at)
                VALUES (%s, %s, %s, 0, 0, 0, NOW())
            """, [title, content, user_id])
            
            article_id = cursor.lastrowid
            
            return JsonResponse({
                'success': True,
                'message': '文章发布成功',
                'data': {
                    'article_id': article_id
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
            'error': f'发布文章失败: {str(e)}'
        }, status=500)
