from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# 공지/규정 페이지
@never_cache
@login_required(login_url="accounts:login")
def notice(request):
    return render(request, "notes/notice.html")


# 출석체크 페이지
@never_cache
@login_required(login_url="accounts:login")
def check_day(request):
    return render(request, "notes/check_day.html")


# 이벤트 페이지
@never_cache
@login_required(login_url="accounts:login")
def event(request):
    return render(request, "notes/event.html")
