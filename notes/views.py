from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from accounts.models import Post
import calendar
from datetime import date
from django.utils import timezone
from accounts.models import Bet, BetSlip


# 공지/규정 페이지
@never_cache
@login_required(login_url="recoards:login")
def notice(request):
    post = Post.objects.filter(type="note")
    return render(request, "notes/notice.html", {"post": post})


# 출석체크 페이지
@never_cache
@login_required(login_url="recoards:login")
def check_day(request):
    today = timezone.now().date()
    year = today.year
    default_month = today.month

    # GET에서 month 값 가져오기 (없으면 현재 달)
    get_month = int(request.GET.get("month", default_month))

    # monthrange → (첫째날 요일, 마지막날)
    last_day = calendar.monthrange(year, get_month)[1]

    # 1일부터 마지막날까지 range 생성
    days = range(1, last_day + 1)

    context = {
        "last_day": last_day,
        "year": year,
        "month": get_month,
        "days": days,
    }
    return render(request, "notes/check_day.html", context)


# 이벤트 페이지
@never_cache
@login_required(login_url="recoards:login")
def event(request):
    post = Post.objects.filter(type="event")
    return render(request, "notes/event.html", {"post": post})


# 게시물 상세보기
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "notes/post_detail.html", {"post": post})


def bet_list(request):
    bets = BetSlip.objects.filter(user=request.user).order_by("-placed_at")
    return render(request, "notes/bet_list.html", {"bets": bets})