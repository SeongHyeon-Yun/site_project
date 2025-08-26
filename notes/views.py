from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from accounts.models import Post


# 공지/규정 페이지
@never_cache
@login_required(login_url="accounts:login")
def notice(request):
    post = Post.objects.filter(type="note")
    return render(request, "notes/notice.html", {"post": post})


# 출석체크 페이지
@never_cache
@login_required(login_url="accounts:login")
def check_day(request):
    return render(request, "notes/check_day.html")


# 이벤트 페이지
@never_cache
@login_required(login_url="accounts:login")
def event(request):
    post = Post.objects.filter(type="event")
    return render(request, "notes/event.html", {"post": post})


# 게시물 상세보기
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "notes/post_detail.html", {"post": post})
