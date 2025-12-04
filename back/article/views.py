from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET


@require_GET
def get_all_articles(request):
    """
    获取所有文章列表
    返回所有文章的完整信息
    """
    try:
        with connection.cursor() as cursor:
            # 查询所有文章，并关联用户表获取作者用户名和头像
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
            """)
            
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
                    'total': len(articles)
                }
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取文章列表失败: {str(e)}',
            'data': {
                'articles': [],
                'total': 0
            }
        }, status=500)
