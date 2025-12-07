from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET


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
