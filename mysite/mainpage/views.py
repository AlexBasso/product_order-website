from timeit import default_timer

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View


class MainpageView(View):
    def get(self, request: HttpRequest) -> HttpResponse:

        context = {
            "time_running": default_timer(),
        }
        return render(request, 'mainpage/index.html', context=context)
