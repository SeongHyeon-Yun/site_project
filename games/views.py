from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.conf import settings as set
from django.utils import timezone
from datetime import timedelta
from .casino_fun import (
    get_casino_list,
    get_slot_list,
    casino_run,
    get_slot_page,
    bacara_money,
)
from games.mapping import LEAGUE_KO, TEAM_KO
from accounts.models import Leagues, Market, Event, BetSlip, Bet
from django.db.models import Q
from django import template
import math, json
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal

register = template.Library()


@login_required
@require_POST
def betting(request):
    try:
        data = json.loads(request.body)
        stake = Decimal(data.get("amount", "0"))
        cart = data.get("cart", [])

        if not cart:
            return JsonResponse({"success": False, "message": "카트가 비어있습니다."})

        user = request.user
        balance_before = user.money  # ✅ 커스텀 User 모델에 money 있다고 가정

        # 👉 전체 배당 계산
        total_odds = 1.0
        for item in cart:
            total_odds *= float(item["odds"])

        expected_amount = stake * Decimal(str(total_odds))

        with transaction.atomic():
            # ✅ 슬립 생성
            slip = BetSlip.objects.create(
                user=user,
                stake=stake,
                total_odds=total_odds,
                expected_amount=expected_amount,
                balance_before=balance_before,
                balance_after=balance_before - stake,
            )

            # ✅ 개별 Bet 생성
            for item in cart:
                event = Event.objects.get(id=item["event_id"])
                market = Market.objects.get(id=item["market_id"])

                # 경기 설명: 홈 vs 원정 + pick
                desc = f"{event.home} vs {event.away} | Pick: {item['pick']}"

                Bet.objects.create(
                    slip=slip,
                    event=event,
                    market=market,
                    pick=item["pick"],
                    odds=float(item["odds"]),
                    description=desc,
                )

            # ✅ 유저 머니 차감
            user.money = balance_before - stake
            user.save()

        return JsonResponse(
            {
                "success": True,
                "message": "베팅 완료",
                "slip_id": slip.id,
                "expected_amount": str(expected_amount),
                "balance_after": str(user.money),
            }
        )

    except Exception as e:
        print("❌ betting error:", e)
        return JsonResponse({"success": False, "message": str(e)})


@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))


# 경기 한글 매핑
def korea_mapping(name: str) -> str:
    # 필요하다면 문자열 정규화 (공백/대소문자/다른 하이픈 등)
    clean = (
        name.strip()
        .replace("–", "-")  # en dash → 일반 하이픈
        .replace("\u00a0", " ")  # non-breaking space → 일반 스페이스
    )
    return TEAM_KO.get(clean, LEAGUE_KO.get(clean, name))


# 경기 배당 기준점 수정
def round_half(x: float) -> float:
    if x is None:
        return None
    return math.floor(x * 2 + 0.5) / 2


# 스포츠 종목 리스트 + 경기 가져오기
def game_base(request, template_name):
    sport_type = request.GET.get("type", "0")

    type_list = {
        "0": "ALL",
        "1": "축구",
        "3": "농구",
        "4": "하키",
        "5": "배구",
        "7": "미식축구",
        "9": "야구",
        "10": "E스포츠",
    }

    now_utc = timezone.now()
    ten_hours_later = now_utc + timedelta(hours=10)

    # 기본 쿼리셋
    event_qs = (
        Event.objects.filter(
            starts__gte=now_utc,
            starts__lte=ten_hours_later,
        )
        .filter(markets__period="num_1")  # num_1 마켓이 있는 경기만
        .select_related("league")
        .prefetch_related("markets")
        .order_by("starts")
        .exclude(
            Q(league__name__icontains="Corners")
            | Q(home__icontains="Hits+Runs+Errors")
            | Q(away__icontains="Hits+Runs+Errors")
        )
        .distinct()
    )

    # sport_type이 "0"이 아닐 때만 sport_id 필터 적용
    if sport_type != "0":
        event_qs = event_qs.filter(league__sport_id=sport_type)

    event = event_qs

    # ✅ 매핑 및 best spread/total 계산
    for e in event:
        # 리그 이름 매핑
        e.league.display_name = korea_mapping(e.league.name)

        # 팀 이름 매핑
        e.home_display = korea_mapping(e.home)
        e.away_display = korea_mapping(e.away)

        # 마켓 값 라운딩
        for m in e.markets.all():
            m.hdp = round_half(m.hdp)
            m.points = round_half(m.points)

        # 종목명 매핑
        e.sport_display = type_list.get(str(e.league.sport_id), "")

        # ✅ 핸디캡(spread) 중 배당 차이가 가장 작은 것
        spreads = [m for m in e.markets.all() if m.market_type == "spread"]
        e.best_spread = (
            min(spreads, key=lambda m: abs((m.home or 0) - (m.away or 0)))
            if spreads
            else None
        )

        # ✅ 오버언더(total) 중 배당 차이가 가장 작은 것
        totals = [m for m in e.markets.all() if m.market_type == "total"]
        e.best_total = (
            min(totals, key=lambda m: abs((m.over or 0) - (m.under or 0)))
            if totals
            else None
        )

    context = {
        "type_list": type_list,
        "sport_type": sport_type,
        "sport_name": type_list.get(sport_type, "ALL"),
        "event": event,
    }

    return render(request, template_name, context)


# 스포츠 크로스
@never_cache
@login_required(login_url="recoards:login")
def sport(request):
    return game_base(request, "games/sport.html")


# 스포츠 스페셜
@never_cache
@login_required(login_url="recoards:login")
def special(request):
    return game_base(request, "games/special.html")


# 카지노 벤더 리스트
@never_cache
@login_required(login_url="recoards:login")
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
@login_required(login_url="recoards:login")
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
@login_required(login_url="recoards:login")
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
