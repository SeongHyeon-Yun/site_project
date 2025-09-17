import json
import math
from datetime import timedelta
from decimal import Decimal

from django import template
from django.conf import settings as set
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.models import Leagues, Market, Event, BetSlip, Bet, Period, Line, User
from games.mapping import LEAGUE_KO, TEAM_KO, PERIOD_KO, MARKET_KO
from .casino_fun import (
    get_casino_list,
    get_slot_list,
    casino_run,
    get_slot_page,
    bacara_money,
    money_in_out,
)


@require_POST
@login_required(login_url="recoards:login")
def betting(request):
    try:
        data = json.loads(request.body)
        game_list = data.get("game_list", [])
        print(game_list)
        if not game_list:
            return JsonResponse({"success": False, "message": "베팅할 경기가 없습니다."})

        # ✅ 유저
        user = request.user

        # ✅ 공통 값 (모든 게임에 동일)
        bet_money = Decimal(str(game_list[0]["bet_money"]))
        win_money = Decimal(str(game_list[0]["win_money"]))

        # ✅ 총 배당 (win_money / bet_money)
        try:
            total_odds = float(win_money / bet_money)
        except ZeroDivisionError:
            total_odds = 1.0

        balance_before = Decimal(user.money)
        balance_after = balance_before - bet_money

        if balance_after < 0:
            return JsonResponse({"success": False, "message": "보유 금액이 부족합니다."})

        with transaction.atomic():
            # ✅ 유저 잔액 차감
            user.money = balance_after
            user.save()

            # ✅ BetSlip 생성
            slip = BetSlip.objects.create(
                user=user,
                stake=bet_money,
                total_odds=total_odds,
                expected_amount=win_money,
                balance_before=balance_before,
                balance_after=balance_after,
            )

            # ✅ Bet 생성 (슬립 안에 여러 경기)
            for g in game_list:
                raw_point = g.get("point")
                if raw_point == "-" or raw_point == "" or raw_point is None:
                    point = None   # ✅ DB에 NULL 저장
                else:
                    point = float(raw_point)
                Bet.objects.create(
                    slip=slip,
                    event=int(g["event_id"]),
                    pick=g["pick"],
                    odds=float(g["odds"]),
                    description=f"{g['team']} {g['market']} {g['point']}",
                    game_num = f"{g['sport_number']}",
                    point = point
                )

        return JsonResponse({"success": True, "message": "베팅 성공", "slip_id": slip.id})

    except Exception as e:
        return JsonResponse({"success": False, "message": "베팅 접수 중 오류가 발생했습니다."})


def get_events(sport_id, hours, exclude_corners=True):
    """
    이벤트 + Period + Market + Line 구조를 딕셔너리로 정리해서 반환.
    """
    now_time = timezone.now()
    before_time = now_time + timedelta(hours=hours)

    # Market 필터
    markets_qs = Market.objects.filter(
        market_type__in=["money_line", "spread", "total"]
    ).prefetch_related(Prefetch("lines", queryset=Line.objects.all()))

    # Periods → Markets
    periods_qs = Period.objects.prefetch_related(
        Prefetch("markets", queryset=markets_qs)
    )

    # Events → Periods
    events = Event.objects.filter(
        starts__gt=now_time,
        starts__lte=before_time,
        sport_id=sport_id,
    ).prefetch_related(Prefetch("periods", queryset=periods_qs))

    if exclude_corners:
        events = (
            events.exclude(league_name__icontains="Corners")
            .exclude(league_name__icontains="Bookings")
            .exclude(league_name__icontains="Hits+Runs+Errors")
            .order_by("starts")
        )

    # ================= 변환 =================
    all_events = []
    for e in events:
        event_dict = {
            "event_id": e.id,
            "league": LEAGUE_KO.get(e.league_name, e.league_name),
            "starts": e.starts,
            "home": TEAM_KO.get(e.home, e.home),
            "away": TEAM_KO.get(e.away, e.away),
            "periods": [],
        }

        for p in e.periods.all():
            period_dict = {
                "code": p.code,
                "description": PERIOD_KO.get(p.description, p.description),
                "markets": [],
            }

            for m in p.markets.all():
                market_dict = {
                    "market_id": m.id,
                    "type": m.market_type,
                    "type_ko": MARKET_KO.get(m.market_type, m.market_type),
                    "values": [],
                }

                if m.market_type == "money_line":
                    if any([m.home, m.away, m.draw]):
                        market_dict["values"].append(
                            {"home": m.home, "draw": m.draw, "away": m.away}
                        )

                elif m.market_type == "spread":
                    for l in m.lines.all():
                        if (l.home_price and l.away_price):
                            # ✅ 기준점 필터 (.0 / .5만 허용)
                            if l.hdp % 0.5 == 0:
                                # ✅ 양쪽 배당 차이 필터 (예: 0.5 이하만 허용)
                                if abs(l.home_price - l.away_price) <= 0.5:
                                    market_dict["values"].append(
                                        {
                                            "hdp": l.hdp,
                                            "home_price": l.home_price,
                                            "away_price": l.away_price,
                                        }
                                    )

                elif m.market_type == "total":
                    for l in m.lines.all():
                        if (l.under_price and l.over_price):
                            # ✅ 기준점 필터 (.0 / .5만 허용)
                            if l.points % 0.5 == 0:
                                # ✅ 오버/언더 배당 차이 필터 (예: 0.5 이하만 허용)
                                if abs(l.over_price - l.under_price) <= 0.5:
                                    market_dict["values"].append(
                                        {
                                            "points": l.points,
                                            "under_price": l.under_price,
                                            "over_price": l.over_price,
                                        }
                                    )


                # ✅ 값이 있으면 마켓 추가
                if market_dict["values"]:
                    period_dict["markets"].append(market_dict)

            # ✅ 마켓이 있으면 period 추가
            if period_dict["markets"]:
                event_dict["periods"].append(period_dict)

        # ✅ period가 있으면 event 추가
        if event_dict["periods"]:
            all_events.append(event_dict)
    return all_events


# ✅ 메인 뷰
@never_cache
@login_required(login_url="recoards:login")
def sport(request):
    if request.GET.get:
        get_type = request.GET.get("type", 1)

    sport_type = {
        "1": "축구",
        "9": "야구",
        "3": "농구",
        "5": "배구",
        "4": "하키",
        "7": "미식축구",
        "10": "E-SPORT",
    }

    if get_type == "4":
        target_code = "num_6"
    else:
        target_code = "num_0"

    events = get_events(sport_id=int(get_type), hours=12, exclude_corners=True)

    context = {
        "sport_type": sport_type,
        "get_type": get_type,
        "events": events,
        "target_code": target_code,
    }

    return render(request, "games/sport.html", context)


# ✅ 스페셜 뷰
@never_cache
@login_required(login_url="recoards:login")
def special(request):
    get_type = request.GET.get("type", 1)

    sport_type = {
        "1": "축구",
        "9": "야구",
        "3": "농구",
        "5": "배구",
        "4": "하키",
        "7": "미식축구",
        "10": "E-SPORT",
    }
    # 👉 DB에 존재하는 period 코드 전부 수집
    exist_codes = list(Period.objects.values_list("code", flat=True).distinct())

    if get_type == "4":
        target_codes = ["num_6"]

    elif get_type == "10":
        # num_3 이상만 필터
        target_codes = [
            c for c in exist_codes if c.startswith("num_") and int(c.split("_")[1]) >= 3
        ]

    if get_type == "9":
        target_codes = ["num_1", "num_3"]

    else:
        target_codes = ["num_1"]

    events = get_events(sport_id=int(get_type), hours=12, exclude_corners=True)

    context = {
        "sport_type": sport_type,
        "get_type": get_type,
        "events": events,
        "target_codes": target_codes,
    }

    return render(request, "games/special.html", context)


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


@require_POST
@login_required
def submit_bet(request):
    try:
        data = json.loads(request.body)

        bet_money = Decimal(data.get("bet_money", 0))
        expected_win = Decimal(data.get("expected_win", 0))
        games = data.get("games", [])

        if not games:
            return JsonResponse({"success": False, "message": "경기 정보가 없습니다."})

        # ✅ 합산 배당 계산 (프론트에서 안 보내주므로 서버에서 직접 계산)
        total_odds = 1.0
        for g in games:
            try:
                total_odds *= float(g.get("odds", 1))
            except Exception:
                continue

        # ✅ 유저 잔액 확인
        balance_before = request.user.money or 0
        balance_after = balance_before - int(bet_money)

        if balance_after < 0:
            return JsonResponse(
                {"success": False, "message": "보유 금액이 부족합니다."}
            )

        # ✅ 부모: BetSlip 생성
        slip = BetSlip.objects.create(
            user=request.user,
            stake=bet_money,
            total_odds=total_odds,
            expected_amount=expected_win,
            balance_before=balance_before,
            balance_after=balance_after,
        )

        # ✅ 자식: Bet 생성
        for g in games:
            Bet.objects.create(
                slip=slip,
                event_id=g["event_id"],  # FK → id로 저장 가능
                market_id=g["market_id"],  # FK → id로 저장 가능
                pick=g["pick"],
                odds=float(g["odds"]),
                description=f"{g['teamname']} {g['smarket']} {g['point']}",
            )

        # ✅ 유저 잔액 차감
        request.user.money = balance_after
        request.user.save(update_fields=["money"])

        return JsonResponse({"success": True, "slip_id": slip.id})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


# 카지노 머지 입출금
def casino_money_change(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        money = data.get("money")
        money_type = data.get("money_type")

        result = money_in_out(username, money, money_type)

        user = User.objects.get(username=username)

        print(result["code"])
        print(user.money)
        if money_type == "out":
            if result.get("code") != 0:
                return JsonResponse({"success": False, "message": "머니 전환 실패"})
            else:
                user.money += int(money)
                user.save()
                return JsonResponse({"success": True, "message": "머니 전환 완료"})

        else:
            if result.get("code") != 0:
                return JsonResponse({"success": False, "message": "머니 전환 실패"})
            else:
                user.money -= int(money)
                user.save()
                return JsonResponse({"success": True, "message": "머니 전환 완료"})
