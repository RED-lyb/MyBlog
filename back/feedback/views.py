"""
反馈相关视图
"""
import json
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from common.jwt_utils import jwt_required
from functools import wraps
from datetime import datetime


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
@require_GET
def get_feedback_list(request):
    """
    获取反馈列表（公开接口，不需要登录）
    支持按问题类型筛选
    """
    try:
        issue_type = request.GET.get('issue_type', '')
        
        with connection.cursor() as cursor:
            # 构建查询条件
            where_conditions = []
            params = []
            
            if issue_type and issue_type in ['使用错误', '功能建议']:
                where_conditions.append("issue_type = %s")
                params.append(issue_type)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # 获取列表（按时间倒序）
            cursor.execute(f"""
                SELECT id, user_id, issue_type, description, created_at, is_resolved, resolved_at
                FROM feedbacks 
                WHERE {where_clause}
                ORDER BY created_at DESC
            """, params)
            rows = cursor.fetchall()
            
            feedback_list = []
            for row in rows:
                # 获取用户名（不显示用户ID，只显示用户名或匿名）
                username = None
                if row[1]:
                    cursor.execute("SELECT username FROM users WHERE id = %s", [row[1]])
                    user_row = cursor.fetchone()
                    username = user_row[0] if user_row else None
                
                feedback_list.append({
                    'id': row[0],
                    'user_id': row[1],  # 返回user_id，用于前端判断是否是自己的反馈
                    'username': username or '匿名用户',
                    'issue_type': row[2],
                    'description': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'is_resolved': row[5],
                    'resolved_at': row[6].isoformat() if row[6] else None
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'feedbacks': feedback_list
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取反馈列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@require_POST
def create_feedback(request):
    """
    创建反馈（需要登录）
    user_id 和 created_at 自动获取
    """
    try:
        data = json.loads(request.body.decode())
        issue_type = data.get('issue_type', '').strip()
        description = data.get('description', '').strip()
        
        # 验证问题类型
        if issue_type not in ['使用错误', '功能建议']:
            return JsonResponse({
                'success': False,
                'error': '问题类型必须是"使用错误"或"功能建议"'
            }, status=400)
        
        if not description:
            return JsonResponse({
                'success': False,
                'error': '问题描述不能为空'
            }, status=400)
        
        user_id = request.user_id  # 从JWT获取用户ID
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO feedbacks (user_id, issue_type, description) 
                VALUES (%s, %s, %s)
            """, [user_id, issue_type, description])
            
            feedback_id = cursor.lastrowid
            
            # 获取创建后的记录
            cursor.execute("""
                SELECT id, user_id, issue_type, description, created_at, is_resolved, resolved_at
                FROM feedbacks 
                WHERE id = %s
            """, [feedback_id])
            row = cursor.fetchone()
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': row[0],
                    'user_id': row[1],
                    'issue_type': row[2],
                    'description': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'is_resolved': row[5],
                    'resolved_at': row[6].isoformat() if row[6] else None
                },
                'message': '反馈提交成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'提交反馈失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_GET
def admin_get_feedback_list(request):
    """
    获取反馈列表（管理员）
    支持筛选和分页
    """
    try:
        # 获取查询参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        issue_type = request.GET.get('issue_type', '')
        is_resolved = request.GET.get('is_resolved', '')
        
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        
        offset = (page - 1) * page_size
        
        with connection.cursor() as cursor:
            # 构建查询条件
            where_conditions = []
            params = []
            
            if issue_type:
                where_conditions.append("issue_type = %s")
                params.append(issue_type)
            
            if is_resolved:
                where_conditions.append("is_resolved = %s")
                params.append(is_resolved)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # 获取总数
            cursor.execute(f"""
                SELECT COUNT(*) FROM feedbacks WHERE {where_clause}
            """, params)
            total = cursor.fetchone()[0]
            
            # 获取列表
            params_with_limit = params + [page_size, offset]
            cursor.execute(f"""
                SELECT id, user_id, issue_type, description, created_at, is_resolved, resolved_at
                FROM feedbacks 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, params_with_limit)
            rows = cursor.fetchall()
            
            feedback_list = []
            for row in rows:
                # 获取用户名
                username = None
                if row[1]:
                    cursor.execute("SELECT username FROM users WHERE id = %s", [row[1]])
                    user_row = cursor.fetchone()
                    username = user_row[0] if user_row else None
                
                feedback_list.append({
                    'id': row[0],
                    'user_id': row[1],
                    'username': username,
                    'issue_type': row[2],
                    'description': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'is_resolved': row[5],
                    'resolved_at': row[6].isoformat() if row[6] else None
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'feedbacks': feedback_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取反馈列表失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_GET
def admin_get_feedback(request, feedback_id):
    """
    获取单条反馈详情（管理员）
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, issue_type, description, created_at, is_resolved, resolved_at
                FROM feedbacks 
                WHERE id = %s
            """, [feedback_id])
            row = cursor.fetchone()
            
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '反馈不存在'
                }, status=404)
            
            # 获取用户名
            username = None
            if row[1]:
                cursor.execute("SELECT username FROM users WHERE id = %s", [row[1]])
                user_row = cursor.fetchone()
                username = user_row[0] if user_row else None
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': row[0],
                    'user_id': row[1],
                    'username': username,
                    'issue_type': row[2],
                    'description': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'is_resolved': row[5],
                    'resolved_at': row[6].isoformat() if row[6] else None
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取反馈失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["PUT"])
def admin_update_feedback_status(request, feedback_id):
    """
    更新反馈状态（管理员）
    每次更新状态时，如果状态不是"未解决"，则更新 resolved_at 为当前时间
    """
    try:
        data = json.loads(request.body.decode())
        is_resolved = data.get('is_resolved', '').strip()
        
        # 验证状态值
        if is_resolved not in ['未解决', '已解决', '未采纳']:
            return JsonResponse({
                'success': False,
                'error': '状态必须是"未解决"、"已解决"或"未采纳"'
            }, status=400)
        
        with connection.cursor() as cursor:
            # 检查记录是否存在
            cursor.execute("SELECT id, is_resolved FROM feedbacks WHERE id = %s", [feedback_id])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '反馈不存在'
                }, status=404)
            
            old_status = row[1]
            
            # 如果状态改变且新状态不是"未解决"，更新 resolved_at
            if old_status != is_resolved and is_resolved != '未解决':
                cursor.execute("""
                    UPDATE feedbacks 
                    SET is_resolved = %s, resolved_at = NOW()
                    WHERE id = %s
                """, [is_resolved, feedback_id])
            else:
                # 如果状态改为"未解决"，清空 resolved_at
                if is_resolved == '未解决':
                    cursor.execute("""
                        UPDATE feedbacks 
                        SET is_resolved = %s, resolved_at = NULL
                        WHERE id = %s
                    """, [is_resolved, feedback_id])
                else:
                    # 状态不变，只更新状态
                    cursor.execute("""
                        UPDATE feedbacks 
                        SET is_resolved = %s
                        WHERE id = %s
                    """, [is_resolved, feedback_id])
            
            # 获取更新后的记录
            cursor.execute("""
                SELECT id, user_id, issue_type, description, created_at, is_resolved, resolved_at
                FROM feedbacks 
                WHERE id = %s
            """, [feedback_id])
            row = cursor.fetchone()
            
            # 获取用户名
            username = None
            if row[1]:
                cursor.execute("SELECT username FROM users WHERE id = %s", [row[1]])
                user_row = cursor.fetchone()
                username = user_row[0] if user_row else None
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': row[0],
                    'user_id': row[1],
                    'username': username,
                    'issue_type': row[2],
                    'description': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'is_resolved': row[5],
                    'resolved_at': row[6].isoformat() if row[6] else None
                },
                'message': '反馈状态更新成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'更新反馈状态失败: {str(e)}'
        }, status=500)


@csrf_exempt
@admin_required
@require_http_methods(["DELETE"])
def admin_delete_feedback(request, feedback_id):
    """
    删除反馈（管理员）
    """
    try:
        with connection.cursor() as cursor:
            # 检查记录是否存在
            cursor.execute("SELECT id FROM feedbacks WHERE id = %s", [feedback_id])
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': '反馈不存在'
                }, status=404)
            
            # 删除记录
            cursor.execute("DELETE FROM feedbacks WHERE id = %s", [feedback_id])
            
            return JsonResponse({
                'success': True,
                'message': '反馈删除成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'删除反馈失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@require_http_methods(["PUT"])
def update_my_feedback(request, feedback_id):
    """
    更新自己的反馈（用户）
    只能更新自己提交的反馈
    """
    try:
        data = json.loads(request.body.decode())
        issue_type = data.get('issue_type', '').strip()
        description = data.get('description', '').strip()
        
        user_id = request.user_id  # 从JWT获取用户ID
        
        # 验证问题类型
        if issue_type and issue_type not in ['使用错误', '功能建议']:
            return JsonResponse({
                'success': False,
                'error': '问题类型必须是"使用错误"或"功能建议"'
            }, status=400)
        
        if description and not description.strip():
            return JsonResponse({
                'success': False,
                'error': '问题描述不能为空'
            }, status=400)
        
        with connection.cursor() as cursor:
            # 检查反馈是否存在且属于当前用户
            cursor.execute("SELECT id, user_id FROM feedbacks WHERE id = %s", [feedback_id])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '反馈不存在'
                }, status=404)
            
            if row[1] != user_id:
                return JsonResponse({
                    'success': False,
                    'error': '只能编辑自己的反馈'
                }, status=403)
            
            # 构建更新语句
            update_fields = []
            params = []
            
            if issue_type:
                update_fields.append("issue_type = %s")
                params.append(issue_type)
            
            if description:
                update_fields.append("description = %s")
                params.append(description)
            
            if not update_fields:
                return JsonResponse({
                    'success': False,
                    'error': '没有需要更新的字段'
                }, status=400)
            
            params.append(feedback_id)
            update_sql = f"""
                UPDATE feedbacks 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            cursor.execute(update_sql, params)
            
            # 获取更新后的记录
            cursor.execute("""
                SELECT id, user_id, issue_type, description, created_at, is_resolved, resolved_at
                FROM feedbacks 
                WHERE id = %s
            """, [feedback_id])
            row = cursor.fetchone()
            
            # 获取用户名
            username = None
            if row[1]:
                cursor.execute("SELECT username FROM users WHERE id = %s", [row[1]])
                user_row = cursor.fetchone()
                username = user_row[0] if user_row else None
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': row[0],
                    'user_id': row[1],
                    'username': username or '匿名用户',
                    'issue_type': row[2],
                    'description': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'is_resolved': row[5],
                    'resolved_at': row[6].isoformat() if row[6] else None
                },
                'message': '反馈更新成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'更新反馈失败: {str(e)}'
        }, status=500)


@csrf_exempt
@jwt_required
@require_http_methods(["DELETE"])
def delete_my_feedback(request, feedback_id):
    """
    删除自己的反馈（用户）
    只能删除自己提交的反馈
    """
    try:
        user_id = request.user_id  # 从JWT获取用户ID
        
        with connection.cursor() as cursor:
            # 检查反馈是否存在且属于当前用户
            cursor.execute("SELECT id, user_id FROM feedbacks WHERE id = %s", [feedback_id])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': '反馈不存在'
                }, status=404)
            
            if row[1] != user_id:
                return JsonResponse({
                    'success': False,
                    'error': '只能删除自己的反馈'
                }, status=403)
            
            # 删除记录
            cursor.execute("DELETE FROM feedbacks WHERE id = %s", [feedback_id])
            
            return JsonResponse({
                'success': True,
                'message': '反馈删除成功'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'删除反馈失败: {str(e)}'
        }, status=500)
