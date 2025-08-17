from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.conf import settings as set
from .casino_fun import (
    get_casino_list,
    get_slot_list,
    casino_run,
    get_slot_page,
    bacara_money,
)


# 스포츠 크로스
@never_cache
@login_required(login_url="accounts:login")
def sport(request):
    return render(request, "games/sport.html")


# 스포츠 스페셜
@never_cache
@login_required(login_url="accounts:login")
def special(request):
    return render(request, "games/special.html")


# 카지노 벤더 리스트
@never_cache
@login_required(login_url="accounts:login")
def casino(request):
    casino_data = get_casino_list(set.GAME_SECRET_KEY, set.GAME_API_BASE)
    ip = get_client_ip(request)
    username = request.user.get_username()
    money = bacara_money(set.GAME_SECRET_KEY, set.GAME_API_BASE, username)
    return render(
        request,
        "games/casino.html",
        {"casino_data": casino_data, "ip": ip, "money": money},
    )


# 슬롯 벤더 리스트
@never_cache
@login_required(login_url="accounts:login")
def slot(request):
    slot_data = get_slot_list(set.GAME_SECRET_KEY, set.GAME_API_BASE)
    ip = get_client_ip(request)
    username = request.user.get_username()
    money = bacara_money(set.GAME_SECRET_KEY, set.GAME_API_BASE, username)
    return render(
        request, "games/slot.html", {"slot_data": slot_data, "ip": ip, "money": money}
    )


# 슬롯 게임 목록 페이지
@never_cache
@login_required(login_url="accounts:login")
def slot_detail(request):
    key = request.POST.get("key")
    vendor = request.POST.get("vendor")
    ip = request.POST.get("ip")

    data = {"key": key, "vendor": vendor, "ip": ip}
    slot_detail = get_slot_page(set.GAME_SECRET_KEY, set.GAME_API_BASE, key)
    return render(
        request, "games/slot_detail.html", {"data": data, "slot_detail": slot_detail}
    )


# 카지노 게임시작
@require_POST
def casino_start(request):
    key = request.POST.get("key")
    skin = request.POST.get("skin")
    ip = request.POST.get("ip")
    username = request.POST.get("username")

    payload = casino_run(
        key, skin, ip, username, set.GAME_SECRET_KEY, set.GAME_API_BASE
    )

    game_url = payload.get("url")

    return redirect(game_url)


# 슬롯 게임 시작
@require_POST
def slot_start(request):
    key = request.POST.get("key")
    username = request.POST.get("username")
    ip = request.POST.get("ip")
    gameName = request.POST.get("gameName")

    payload = casino_run(
        gameName, key, ip, username, set.GAME_SECRET_KEY, set.GAME_API_BASE
    )

    game_url = payload.get("url")

    return redirect(game_url)


# ip 조회
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # 여러 IP가 있을 수 있으니 첫 번째 값 사용
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
