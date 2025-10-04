import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

@csrf_exempt
def register(request):
    if request.method == "POST":
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        security_question = data.get('protect')
        security_answer = data.get('answer')
        #要添加错误处理了！！！
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, password, security_question, security_answer) VALUES (%s, %s, %s, %s)",
                [username, password, security_question, security_answer]
            )

        return JsonResponse({"msg": "注册成功"})
    return JsonResponse({"error": "只支持POST"}, status=405)