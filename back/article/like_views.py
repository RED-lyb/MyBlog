from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from common.jwt_utils import jwt_required
from common.user_relation_utils import like_article, unlike_article, is_liked_article


@csrf_exempt
@jwt_required
@require_POST
def toggle_like(request, article_id):
    """
    切换文章的喜欢状态（喜欢/取消喜欢）
    需要JWT认证
    """
    try:
        # 获取用户ID（由JWT中间件设置）
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户未登录'
            }, status=401)
        
        # 检查当前是否已喜欢
        is_liked = is_liked_article(user_id, article_id)
        
        if is_liked:
            # 取消喜欢
            success, message = unlike_article(user_id, article_id)
            if success:
                return JsonResponse({
                    'success': True,
                    'message': '取消喜欢成功',
                    'data': {
                        'is_liked': False
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': message
                }, status=400)
        else:
            # 喜欢
            success, message = like_article(user_id, article_id)
            if success:
                return JsonResponse({
                    'success': True,
                    'message': '喜欢成功',
                    'data': {
                        'is_liked': True
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': message
                }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'操作失败: {str(e)}'
        }, status=500)


@jwt_required
def check_like_status(request, article_id):
    """
    检查用户是否喜欢了某篇文章
    需要JWT认证
    """
    try:
        # 获取用户ID（由JWT中间件设置）
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户未登录'
            }, status=401)
        
        is_liked = is_liked_article(user_id, article_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'is_liked': is_liked
            }
        })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }, status=500)

