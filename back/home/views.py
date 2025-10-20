from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

# Create your views here.
def home(request):
    print("主页测试")
    return HttpResponse("主页测试请求成功")