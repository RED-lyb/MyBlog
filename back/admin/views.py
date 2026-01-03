"""
管理员相关视图
提供管理员后台管理功能
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.conf import settings
from functools import wraps
from common.jwt_utils import jwt_required, JWTUtils


def admin_required(view_func):
    """
    管理员权限装饰器
    需要先通过JWT认证，然后检查用户是否为管理员
    """
    @wraps(view_func)
    @jwt_required
    def _wrapped_view(request, *args, **kwargs):
        # jwt_required 已经设置了 request.user_id
        user_id = request.user_id
        
        # 检查用户是否为管理员
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_admin FROM users WHERE id = %s", [user_id])
            row = cursor.fetchone()
            
            if not row or not row[0]:
                return JsonResponse({
                    'success': False,
                    'error': '需要管理员权限',
                    'code': 'ADMIN_REQUIRED'
                }, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


@csrf_exempt
@admin_required
@require_http_methods(["GET"])
def get_statistics(request):
    """
    获取统计数据
    返回用户数、文章数、浏览量、喜欢数、网盘文件数等统计信息
    """
    try:
        with connection.cursor() as cursor:
            # 总用户数
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # 今日新增用户数
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE registered_time >= %s",
                [today_start]
            )
            today_new_users = cursor.fetchone()[0]
            
            # 总文章数
            cursor.execute("SELECT COUNT(*) FROM blog_articles")
            total_articles = cursor.fetchone()[0]
            
            # 今日新增文章数
            cursor.execute(
                "SELECT COUNT(*) FROM blog_articles WHERE published_at >= %s",
                [today_start]
            )
            today_new_articles = cursor.fetchone()[0]
            
            # 总浏览量
            cursor.execute("SELECT SUM(view_count) FROM blog_articles")
            total_views = cursor.fetchone()[0] or 0
            
            # 总喜欢数
            cursor.execute("SELECT SUM(love_count) FROM blog_articles")
            total_likes = cursor.fetchone()[0] or 0
            
            # 网盘文件统计
            network_disk_root = Path(settings.BASE_DIR) / 'api' / 'static' / 'files'
            file_count = 0
            total_size_bytes = 0
            
            if network_disk_root.exists():
                for item in network_disk_root.rglob('*'):
                    if item.is_file():
                        file_count += 1
                        try:
                            total_size_bytes += item.stat().st_size
                        except (OSError, PermissionError):
                            pass
            
            total_size_gb = round(total_size_bytes / (1024 ** 3), 2)
            
            # 最近7天的数据趋势
            trend_data = []
            for i in range(6, -1, -1):
                date = (datetime.now() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
                next_date = date + timedelta(days=1)
                
                # 该日新增用户数
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE registered_time >= %s AND registered_time < %s",
                    [date, next_date]
                )
                day_users = cursor.fetchone()[0]
                
                # 该日新增文章数
                cursor.execute(
                    "SELECT COUNT(*) FROM blog_articles WHERE published_at >= %s AND published_at < %s",
                    [date, next_date]
                )
                day_articles = cursor.fetchone()[0]
                
                trend_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'users': day_users,
                    'articles': day_articles
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'users': {
                        'total': total_users,
                        'today_new': today_new_users
                    },
                    'articles': {
                        'total': total_articles,
                        'today_new': today_new_articles
                    },
                    'views': {
                        'total': total_views
                    },
                    'likes': {
                        'total': total_likes
                    },
                    'network_disk': {
                        'file_count': file_count,
                        'total_size_gb': total_size_gb
                    },
                    'trend': trend_data
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取统计数据失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["GET"])
def list_articles(request):
    """
    获取文章列表（分页）
    """
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        search = request.GET.get('search', '').strip()
        
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        
        offset = (page - 1) * page_size
        
        with connection.cursor() as cursor:
            # 构建查询条件
            where_clause = ""
            params = []
            
            if search:
                where_clause = "WHERE a.title LIKE %s OR u.username LIKE %s"
                params.extend([f'%{search}%', f'%{search}%'])
            
            # 查询总数
            count_sql = f"SELECT COUNT(*) FROM blog_articles a LEFT JOIN users u ON a.author_id = u.id {where_clause}"
            cursor.execute(count_sql, params)
            total_count = cursor.fetchone()[0]
            
            # 查询分页数据
            sql = f"""
                SELECT 
                    a.id,
                    a.title,
                    a.author_id,
                    u.username as author_name,
                    a.view_count,
                    a.love_count,
                    a.comment_count,
                    a.published_at
                FROM blog_articles a
                LEFT JOIN users u ON a.author_id = u.id
                {where_clause}
                ORDER BY a.published_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, params + [page_size, offset])
            
            rows = cursor.fetchall()
            articles = []
            for row in rows:
                articles.append({
                    'id': row[0],
                    'title': row[1],
                    'author_id': row[2],
                    'author_name': row[3] if row[3] else '未知用户',
                    'view_count': row[4],
                    'love_count': row[5],
                    'comment_count': row[6],
                    'published_at': row[7].isoformat() if row[7] else None
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'articles': articles,
                    'total': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取文章列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["GET"])
def get_article(request, article_id):
    """
    获取文章详情
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    a.id,
                    a.title,
                    a.content,
                    a.author_id,
                    u.username as author_name,
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
                    'error': '文章不存在'
                }, status=404)
            
            article = {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'author_id': row[3],
                'author_name': row[4] if row[4] else '未知用户',
                'view_count': row[5],
                'love_count': row[6],
                'comment_count': row[7],
                'published_at': row[8].isoformat() if row[8] else None
            }
            
            return JsonResponse({
                'success': True,
                'data': article
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取文章详情失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["POST"])
def create_article(request):
    """
    创建文章
    """
    try:
        data = json.loads(request.body.decode())
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        author_id = data.get('author_id')
        
        if not title or not content:
            return JsonResponse({
                'success': False,
                'error': '标题和内容不能为空'
            }, status=400)
        
        if not author_id:
            author_id = request.user_id
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO blog_articles (title, content, author_id, published_at)
                VALUES (%s, %s, %s, NOW())
            """, [title, content, author_id])
            
            article_id = cursor.lastrowid
            
            return JsonResponse({
                'success': True,
                'data': {'id': article_id},
                'message': '文章创建成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'创建文章失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["PUT"])
def update_article(request, article_id):
    """
    更新文章
    """
    try:
        data = json.loads(request.body.decode())
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        author_id = data.get('author_id')
        
        if not title or not content:
            return JsonResponse({
                'success': False,
                'error': '标题和内容不能为空'
            }, status=400)
        
        with connection.cursor() as cursor:
            # 检查文章是否存在
            cursor.execute("SELECT id FROM blog_articles WHERE id = %s", [article_id])
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': '文章不存在'
                }, status=404)
            
            # 更新文章
            if author_id:
                cursor.execute("""
                    UPDATE blog_articles 
                    SET title = %s, content = %s, author_id = %s
                    WHERE id = %s
                """, [title, content, author_id, article_id])
            else:
                cursor.execute("""
                    UPDATE blog_articles 
                    SET title = %s, content = %s
                    WHERE id = %s
                """, [title, content, article_id])
            
            return JsonResponse({
                'success': True,
                'message': '文章更新成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'更新文章失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["DELETE"])
def delete_article(request, article_id):
    """
    删除文章
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM blog_articles WHERE id = %s", [article_id])
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': '文章不存在'
                }, status=404)
            
            cursor.execute("DELETE FROM blog_articles WHERE id = %s", [article_id])
            
            return JsonResponse({
                'success': True,
                'message': '文章删除成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'删除文章失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["GET"])
def list_users(request):
    """
    获取用户列表（分页）
    """
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        search = request.GET.get('search', '').strip()
        
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        
        offset = (page - 1) * page_size
        
        with connection.cursor() as cursor:
            # 构建查询条件
            where_clause = ""
            params = []
            
            if search:
                where_clause = "WHERE username LIKE %s"
                params.append(f'%{search}%')
            
            # 查询总数
            count_sql = f"SELECT COUNT(*) FROM users {where_clause}"
            cursor.execute(count_sql, params)
            total_count = cursor.fetchone()[0]
            
            # 查询分页数据
            sql = f"""
                SELECT 
                    id,
                    username,
                    registered_time,
                    avatar,
                    follow_count,
                    article_count,
                    liked_article_count,
                    follower_count,
                    is_admin
                FROM users
                {where_clause}
                ORDER BY registered_time DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, params + [page_size, offset])
            
            rows = cursor.fetchall()
            users = []
            for row in rows:
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'registered_time': row[2].isoformat() if row[2] else None,
                    'avatar': row[3],
                    'follow_count': row[4],
                    'article_count': row[5],
                    'liked_article_count': row[6],
                    'follower_count': row[7],
                    'is_admin': bool(row[8]) if row[8] is not None else False
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'users': users,
                    'total': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取用户列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["GET"])
def get_user(request, user_id):
    """
    获取用户详情
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    id,
                    username,
                    registered_time,
                    avatar,
                    bg_color,
                    bg_pattern,
                    corner_radius,
                    follow_count,
                    article_count,
                    liked_article_count,
                    follower_count,
                    is_admin
                FROM users
                WHERE id = %s
            """, [user_id])
            
            row = cursor.fetchone()
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '用户不存在'
                }, status=404)
            
            user_data = {
                'id': row[0],
                'username': row[1],
                'registered_time': row[2].isoformat() if row[2] else None,
                'avatar': row[3],
                'bg_color': row[4],
                'bg_pattern': row[5],
                'corner_radius': row[6],
                'follow_count': row[7],
                'article_count': row[8],
                'liked_article_count': row[9],
                'follower_count': row[10],
                'is_admin': bool(row[11]) if row[11] is not None else False
            }
            
            return JsonResponse({
                'success': True,
                'data': user_data
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取用户详情失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["PUT"])
def update_user(request, user_id):
    """
    更新用户信息
    """
    try:
        data = json.loads(request.body.decode())
        
        # 构建更新字段
        update_fields = []
        params = []
        
        if 'username' in data:
            update_fields.append("username = %s")
            params.append(data['username'].strip())
        
        if 'avatar' in data:
            update_fields.append("avatar = %s")
            params.append(data['avatar'])
        
        if 'bg_color' in data:
            update_fields.append("bg_color = %s")
            params.append(data['bg_color'])
        
        if 'bg_pattern' in data:
            update_fields.append("bg_pattern = %s")
            params.append(data['bg_pattern'])
        
        if 'corner_radius' in data:
            update_fields.append("corner_radius = %s")
            params.append(data['corner_radius'])
        
        if not update_fields:
            return JsonResponse({
                'success': False,
                'error': '没有要更新的字段'
            }, status=400)
        
        params.append(user_id)
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", [user_id])
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': '用户不存在'
                }, status=404)
            
            sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(sql, params)
            
            return JsonResponse({
                'success': True,
                'message': '用户信息更新成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'更新用户信息失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    """
    删除用户
    """
    try:
        # 不能删除自己
        if request.user_id == user_id:
            return JsonResponse({
                'success': False,
                'error': '不能删除自己的账户'
            }, status=400)
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", [user_id])
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': '用户不存在'
                }, status=404)
            
            cursor.execute("DELETE FROM users WHERE id = %s", [user_id])
            
            return JsonResponse({
                'success': True,
                'message': '用户删除成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'删除用户失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["POST"])
def toggle_admin(request, user_id):
    """
    切换用户管理员状态
    """
    try:
        # 不能修改自己的管理员状态
        if request.user_id == user_id:
            return JsonResponse({
                'success': False,
                'error': '不能修改自己的管理员状态'
            }, status=400)
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_admin FROM users WHERE id = %s", [user_id])
            row = cursor.fetchone()
            
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '用户不存在'
                }, status=404)
            
            current_admin_status = bool(row[0]) if row[0] is not None else False
            new_admin_status = not current_admin_status
            
            cursor.execute("UPDATE users SET is_admin = %s WHERE id = %s", [new_admin_status, user_id])
            
            return JsonResponse({
                'success': True,
                'data': {'is_admin': new_admin_status},
                'message': f'管理员状态已{"开启" if new_admin_status else "关闭"}'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'切换管理员状态失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["GET"])
def list_network_files(request):
    """
    获取网盘文件列表
    """
    try:
        network_disk_root = Path(settings.BASE_DIR) / 'api' / 'static' / 'files'
        
        if not network_disk_root.exists():
            return JsonResponse({
                'success': True,
                'data': {
                    'files': [],
                    'total_size_gb': 0
                }
            })
        
        files = []
        total_size_bytes = 0
        
        # 遍历所有用户文件夹
        for user_dir in network_disk_root.iterdir():
            if not user_dir.is_dir():
                continue
            
            user_id = user_dir.name
            
            # 获取用户名
            with connection.cursor() as cursor:
                cursor.execute("SELECT username FROM users WHERE id = %s", [user_id])
                row = cursor.fetchone()
                username = row[0] if row else f'用户{user_id}'
            
            # 遍历用户文件夹下的所有文件
            for file_path in user_dir.rglob('*'):
                if file_path.is_file():
                    try:
                        file_stat = file_path.stat()
                        relative_path = file_path.relative_to(network_disk_root)
                        
                        files.append({
                            'path': str(relative_path),
                            'name': file_path.name,
                            'size': file_stat.st_size,
                            'size_mb': round(file_stat.st_size / (1024 ** 2), 2),
                            'user_id': user_id,
                            'username': username,
                            'modified_time': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        })
                        
                        total_size_bytes += file_stat.st_size
                    except (OSError, PermissionError):
                        pass
        
        total_size_gb = round(total_size_bytes / (1024 ** 3), 2)
        
        return JsonResponse({
            'success': True,
            'data': {
                'files': files,
                'total_size_gb': total_size_gb,
                'file_count': len(files)
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取网盘文件列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["DELETE"])
def delete_network_file(request):
    """
    删除网盘文件
    """
    try:
        data = json.loads(request.body.decode())
        file_path = data.get('path', '').strip()
        
        if not file_path:
            return JsonResponse({
                'success': False,
                'error': '文件路径不能为空'
            }, status=400)
        
        network_disk_root = Path(settings.BASE_DIR) / 'api' / 'static' / 'files'
        target_file = network_disk_root / file_path
        
        # 安全检查：确保文件在网盘根目录下
        try:
            target_file.resolve().relative_to(network_disk_root.resolve())
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': '无效的文件路径'
            }, status=400)
        
        if not target_file.exists():
            return JsonResponse({
                'success': False,
                'error': '文件不存在'
            }, status=404)
        
        if target_file.is_file():
            target_file.unlink()
        elif target_file.is_dir():
            import shutil
            shutil.rmtree(target_file)
        
        return JsonResponse({
            'success': True,
            'message': '文件删除成功'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'删除文件失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["GET"])
def get_config(request):
    """
    获取全局配置（前端配置 + 后端配置）
    """
    try:
        # 前端配置文件路径
        front_config_path = Path(settings.BASE_DIR).parent / 'front' / 'blog_front' / 'public' / 'config_front.json'
        # 后端配置文件路径
        back_config_path = Path(settings.BASE_DIR) / 'config' / 'config_back.json'
        
        config_data = {}
        
        # 读取前端配置
        if front_config_path.exists():
            try:
                with open(front_config_path, 'r', encoding='utf-8') as f:
                    front_config = json.load(f)
                    config_data.update(front_config)
            except Exception as e:
                print(f'读取前端配置失败: {str(e)}')
        
        # 读取后端配置
        if back_config_path.exists():
            try:
                with open(back_config_path, 'r', encoding='utf-8') as f:
                    back_config = json.load(f)
                    # 合并后端配置
                    for key, value in back_config.items():
                        if key not in config_data:
                            config_data[key] = value
                        elif isinstance(config_data[key], dict) and isinstance(value, dict):
                            config_data[key].update(value)
                        else:
                            config_data[key] = value
            except Exception as e:
                print(f'读取后端配置失败: {str(e)}')
        
        # 如果两个配置文件都不存在，返回默认配置
        if not config_data:
            from common.config_utils import load_config
            default_back_config = load_config()
            config_data = {
                'author_id': 1,
                'author': '',
                'blog_name': '',
                'github_link': '',
                'gitee_link': '',
                'bilibili_link': '',
                **default_back_config
            }
        
        return JsonResponse({
            'success': True,
            'data': config_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'读取配置文件失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["PUT"])
def update_config(request):
    """
    更新全局配置（分别保存前端和后端配置）
    """
    try:
        data = json.loads(request.body.decode())
        
        # 验证必需字段
        required_fields = ['author_id', 'author', 'blog_name']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }, status=400)
        
        # 前端配置文件路径
        front_config_path = Path(settings.BASE_DIR).parent / 'front' / 'blog_front' / 'public' / 'config_front.json'
        # 后端配置文件路径
        back_config_path = Path(settings.BASE_DIR) / 'config' / 'config_back.json'
        
        # 分离前端和后端配置
        front_config = {
            'author_id': data.get('author_id', 1),
            'author': data.get('author', ''),
            'blog_name': data.get('blog_name', ''),
            'github_link': data.get('github_link', ''),
            'gitee_link': data.get('gitee_link', ''),
            'bilibili_link': data.get('bilibili_link', '')
        }
        
        # 添加主题颜色配置
        if 'light' in data:
            front_config['light'] = data.get('light', {})
        if 'dark' in data:
            front_config['dark'] = data.get('dark', {})
        
        back_config = {
            'network_disk': data.get('network_disk', {}),
            'captcha': data.get('captcha', {}),
            'jwt': data.get('jwt', {})
        }
        
        # 保存前端配置
        try:
            front_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(front_config_path, 'w', encoding='utf-8') as f:
                json.dump(front_config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'保存前端配置失败: {str(e)}'
            }, status=500)
        
        # 保存后端配置
        try:
            back_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(back_config_path, 'w', encoding='utf-8') as f:
                json.dump(back_config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'保存后端配置失败: {str(e)}'
            }, status=500)
        
        # 合并返回完整配置
        merged_config = {**front_config, **back_config}
        
        return JsonResponse({
            'success': True,
            'data': merged_config,
            'message': '配置更新成功'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'更新配置文件失败: {str(e)}'
        }, status=500)

