import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

# Create your views here.
@csrf_exempt
def forgot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode())
            username = data.get('username', '').strip()
            answer = data.get('answer', '').strip()

            # 如果提供了密保答案，则进行验证
            if answer:
                return verify_security_answer(username, answer)
            # 否则只是检查用户是否存在
            else:
                return check_user_exists(username)

        except Exception as e:
            return JsonResponse({'status': 'false', 'message': '验证异常，请稍后再试'}, status=500)

    elif request.method == 'PUT':
        return update_password(request)
    else:
        return JsonResponse({'error': '方法不允许'}, status=405)


def check_user_exists(username):
    """
    检查用户是否存在
    """
    if not username:
        return JsonResponse({'status': 'false', 'message': '用户名不能为空'}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT protect FROM users WHERE username=%s", [username])
            row = cursor.fetchone()

            if row:
                # 用户存在，返回密保问题
                return JsonResponse({
                    'status': 'true',
                    'message': '用户存在',
                    'protect': row[0]  # 返回密保问题
                })
            else:
                # 用户不存在
                return JsonResponse({'status': 'false', 'message': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'false', 'message': '验证异常，请稍后再试'}, status=500)


def verify_security_answer(username, answer):
    """
    验证密保答案
    """
    if not username or not answer:
        return JsonResponse({'status': 'false', 'message': '用户名和密保答案不能为空'}, status=400)

    try:
        from django.contrib.auth.hashers import check_password

        with connection.cursor() as cursor:
            cursor.execute("SELECT answer FROM users WHERE username=%s", [username])
            row = cursor.fetchone()

            if row:
                # 用户存在，验证密保答案
                stored_answer = row[0]
                if check_password(answer, stored_answer):
                    return JsonResponse({
                        'status': 'true',
                        'message': '密保验证成功'
                    })
                else:
                    return JsonResponse({
                        'status': 'false',
                        'message': '密保答案错误'
                    }, status=400)
            else:
                # 用户不存在
                return JsonResponse({'status': 'false', 'message': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'false', 'message': '验证异常，请稍后再试'}, status=500)
def update_password(request):
    """
    更新用户密码
    """
    try:
        data = json.loads(request.body.decode())
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return JsonResponse({'status': 'false', 'message': '用户名和密码不能为空'}, status=400)

        from django.contrib.auth.hashers import make_password

        with connection.cursor() as cursor:
            # 先检查用户是否存在
            cursor.execute("SELECT id FROM users WHERE username=%s", [username])
            row = cursor.fetchone()

            if not row:
                return JsonResponse({'status': 'false', 'message': '用户不存在'}, status=404)

            # 更新密码
            hashed_password = make_password(password)
            cursor.execute("UPDATE users SET password=%s WHERE username=%s", [hashed_password, username])

        return JsonResponse({
            'status': 'true',
            'message': '密码更新成功'
        })

    except Exception as e:
        return JsonResponse({'status': 'false', 'message': '密码更新失败，请稍后再试'}, status=500)