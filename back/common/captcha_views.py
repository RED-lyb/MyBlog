"""
验证码相关API视图
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .captcha_utils import CaptchaUtils


@csrf_exempt
@require_http_methods(["GET"])
def get_captcha(request):
    """
    获取验证码
    GET /api/captcha/
    """
    try:
        result = CaptchaUtils.generate_captcha(request)
        if result['success']:
            return JsonResponse({
                'success': True,
                'captcha_key': result['captcha_key'],
                'captcha_image': result['captcha_image']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取验证码失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_captcha_image(request, key):
    """
    获取验证码图片
    GET /api/captcha/image/<key>/
    """
    from captcha.views import captcha_image
    return captcha_image(request, key)


@csrf_exempt
@require_http_methods(["POST"])
def verify_captcha(request):
    """
    验证验证码
    POST /api/captcha/verify/
    """
    try:
        data = json.loads(request.body.decode())
        captcha_key = data.get('captcha_key', '')
        captcha_value = data.get('captcha_value', '')
        
        is_valid, message = CaptchaUtils.verify_captcha(captcha_key, captcha_value)
        
        return JsonResponse({
            'success': is_valid,
            'message': message
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'验证码验证失败: {str(e)}'
        }, status=500)
