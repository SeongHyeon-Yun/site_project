from accounts.models import Event, Grade
from games.casino_fun import bacara_money
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q


def common_context(request):
    type_list = {
        "1": "축구",
        "3": "농구",
        "4": "하키",
        "5": "배구",
        "7": "미식축구",
        "9": "야구",
        "10": "E스포츠",
    }

    sport_count_list = []
    all_count = 0

    for key, name in type_list.items():
        if key == "0":
            continue

        # 👉 실제 경기 가져오는 조건과 동일하게 맞춤
        event_count = (
            Event.objects.filter(
                league__sport_id=key,
            )
            .exclude(
                Q(league__name__icontains="Corners")
                | Q(home__icontains="Hits+Runs+Errors")
                | Q(away__icontains="Hits+Runs+Errors")
            )
            .filter(
                Q(starts__gt=timezone.now())
                & Q(starts__lte=timezone.now() + timedelta(hours=5))
            )
            .distinct()
            .count()
        )

        all_count += event_count
        sport_count_list.append({"id": key, "name": name, "count": event_count})

    username = request.user.username if request.user.is_authenticated else None
    nickname = (
        getattr(request.user, "nickname", None)
        if request.user.is_authenticated
        else None
    )
    grade = (
        getattr(request.user.grade, "name", None)
        if request.user.is_authenticated and getattr(request.user, "grade", None)
        else None
    )

    casino_money = bacara_money(
        settings.GAME_SECRET_KEY, settings.GAME_API_BASE, username
    )

    accounts_password = (
        getattr(request.user, "accounts_password", None)
        if request.user.is_authenticated
        else None
    )

    return {
        "sport_count_list": sport_count_list,
        "username": username,
        "nickname": nickname,
        "grade": grade,
        "casino_money": casino_money,
        "accounts_password": accounts_password,
    }