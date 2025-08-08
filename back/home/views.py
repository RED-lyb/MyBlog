from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


# Create your views here.
class TheHome(View):
    def get(self, request):
        print("来了一个get请求")
        return HttpResponse("get请求成功")