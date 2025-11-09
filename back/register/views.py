import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, IntegrityError
from django.contrib.auth.hashers import make_password
from common.captcha_utils import CaptchaUtils, captcha_required

# 与前端完全一致的校验规则（copy 自 logincard.vue）
DB_KEYWORDS = [
    'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
    'USER', 'USERS', 'ORDER', 'GROUP', 'KEY', 'INDEX', 'TABLE', 'PASSWORD', 'ADMIN', 'ROOT'
]

def _validate_username(value: str) -> str:
    """返回错误字符串，空串表示通过"""
    if not value:
        return '请输入用户名'
    if not re.fullmatch(r'^[A-Za-z0-9_\-\u4e00-\u9fa5]+$', value):
        return '只允许字母、数字、下划线、连字符、中文'
    if value.upper() in DB_KEYWORDS:
        return '不得使用该用户名，请更换'
    return ''

def _validate_password(value: str) -> str:
    if not value:
        return '请输入密码'
    if len(value) < 8:
        return '密码至少 8 位'
    if not re.search(r'[0-9]', value):
        return '需包含数字'
    if not re.search(r'[A-Z]', value):
        return '需包含大写字母'
    if not re.search(r'[a-z]', value):
        return '需包含小写字母'
    return ''

def _validate_answer(value: str) -> str:
    if not value:
        return '请输入密保答案'
    if not re.fullmatch(r'[\u4e00-\u9fa5A-Za-z0-9]+', value):
        return '答案只能包含中文、英文和数字'
    return ''

@csrf_exempt
@captcha_required
def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST'}, status=405)

    try:
        data = json.loads(request.body.decode())
        username = data.get('username', '').strip()
        password = data.get('password', '')
        protect = data.get('protect', '').strip()
        answer = data.get('answer', '').strip()
        captcha_key = data.get('captcha_key', '')
        captcha_value = data.get('captcha_value', '')


        # 1. 二次校验
        errors = {}
        if msg := _validate_username(username):
            errors['username'] = msg
        if msg := _validate_password(password):
            errors['password'] = msg
        if not protect:
            errors['protect'] = '请选择密保问题'
        if msg := _validate_answer(answer):
            errors['answer'] = msg

        if errors:
            # 直接按字段名返回，前端可原样塞进 <el-form-item> 的 error 槽
            return JsonResponse({'field_errors': errors}, status=400)

        # 2. 唯一性检查
        with connection.cursor() as c:
            c.execute("SELECT 1 FROM users WHERE username=%s LIMIT 1", [username])
            if c.fetchone():
                return JsonResponse({'field_errors': {'username': '当前用户名已注册'}}, status=400)

        # 3. 入库
        with connection.cursor() as c:
            c.execute(
                "INSERT INTO users (username, password, protect, answer) VALUES (%s, %s, %s, %s)",
                [username, make_password(password), protect, make_password(answer)]
            )
        return JsonResponse({'success': True, 'msg': '注册成功'})
    except IntegrityError as e:
        # 理论上唯一索引二次保护
        return JsonResponse({'field_errors': {'username': '当前用户名已注册'}}, status=400)
    except Exception as e:
        # 其它任何数据库/编码异常
        return JsonResponse({'field_errors': {'non_field': '服务器异常，请稍后重试'}}, status=500)