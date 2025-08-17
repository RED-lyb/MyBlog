from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .models import Test
# Create your views here.
class TheHome(View):
    def get(self, request):
        print("来了一个get请求")
        # data=Test.objects.raw(
        #     "select * from test"
        # )
        # for x in data:
        #     print(x.data)
        return HttpResponse("get请求成功")
