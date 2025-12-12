import json
import re
import html
import time
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from common.jwt_utils import jwt_required
from common.captcha_utils import CaptchaUtils, LoginLimitUtils


@require_GET
def get_all_articles(request):
    """
    获取文章列表（支持分页）
    返回分页后的文章信息
    """
    try:
        # 获取分页参数
        page = int(request.GET.get('page', 1))  # 当前页码，默认第1页
        page_size = int(request.GET.get('page_size', 4))  # 每页数量，默认4条
        
        # 确保页码和每页数量有效
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 4
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        with connection.cursor() as cursor:
            # 先查询总记录数
            cursor.execute("""
                SELECT COUNT(*) 
                FROM blog_articles
            """)
            total_count = cursor.fetchone()[0]
            
            # 查询分页后的文章，并关联用户表获取作者用户名和头像
            # 按发布时间降序排列（最先发布的在最后面）
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
                ORDER BY a.published_at DESC
                LIMIT %s OFFSET %s
            """, [page_size, offset])
            
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


def sanitize_html(content):
    """
    清理HTML内容，防止XSS攻击
    允许安全的HTML标签和属性，过滤危险的标签和属性
    """
    # 允许的HTML标签（白名单）
    allowed_tags = {
        'p', 'br', 'strong', 'em', 'u', 's', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img',
        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'div', 'span'
    }
    
    # 允许的属性
    allowed_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'code': ['class'],
        'pre': ['class'],
        'div': ['class'],
        'span': ['class'],
        'table': ['class'],
        'th': ['class'],
        'td': ['class']
    }
    
    # 转义所有HTML标签
    content = html.escape(content)
    
    # 恢复允许的标签（使用正则表达式）
    # 注意：这是一个简化的实现，实际生产环境建议使用 bleach 库
    
    # 恢复换行符
    content = content.replace('&lt;br&gt;', '<br>')
    content = content.replace('&lt;br/&gt;', '<br>')
    content = content.replace('&lt;br /&gt;', '<br>')
    
    # 恢复允许的标签（使用正则表达式匹配）
    tag_pattern = r'&lt;(\/?)(\w+)([^&]*?)&gt;'
    
    def replace_tag(match):
        closing = match.group(1)  # / 或空
        tag_name = match.group(2).lower()
        attrs = match.group(3)
        
        if tag_name not in allowed_tags:
            return match.group(0)  # 保持转义状态
        
        # 处理属性
        if attrs and tag_name in allowed_attrs:
            # 提取允许的属性
            allowed_attrs_list = allowed_attrs[tag_name]
            attr_pattern = r'(\w+)=["\']([^"\']*)["\']'
            valid_attrs = []
            
            for attr_match in re.finditer(attr_pattern, attrs):
                attr_name = attr_match.group(1).lower()
                attr_value = attr_match.group(2)
                
                if attr_name in allowed_attrs_list:
                    # 对于 href 和 src，需要额外验证
                    if attr_name in ['href', 'src']:
                        # 只允许 http/https 和相对路径
                        if attr_value.startswith(('http://', 'https://', '/', '#')) or not attr_value.startswith('javascript:'):
                            valid_attrs.append(f'{attr_name}="{html.escape(attr_value)}"')
                    else:
                        valid_attrs.append(f'{attr_name}="{html.escape(attr_value)}"')
            
            attrs_str = ' ' + ' '.join(valid_attrs) if valid_attrs else ''
        else:
            attrs_str = ''
        
        return f'<{closing}{tag_name}{attrs_str}>'
    
    content = re.sub(tag_pattern, replace_tag, content)
    
    return content


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
        
        # 直接存储原始内容，不做HTML转义
        # 因为内容是Markdown格式，会被marked安全解析
        # 转义会导致代码块中的引号等字符变成HTML实体（如 &quot;），影响显示
        
        # 写入数据库
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
