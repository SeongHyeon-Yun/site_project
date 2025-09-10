import django, os, sys, pprint
from pathlib import Path
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "new_bet.settings")
django.setup()

from accounts.models import Event, Period, Line, Market


def get_events(sport_id, hours, exclude_corners=True):
    """
    이벤트 + Period + Market + Line 구조를 딕셔너리로 정리해서 반환.

    :param sport_id: 종목 (1=축구, 3=농구 ...)
    :param hours: 앞으로 몇 시간 이내 경기만 가져올지
    :param exclude_corners: 리그명에 'Corners' 들어간 경기 제외 여부
    :return: [ {event dict}, ... ]
    """
    now_time = timezone.now()
    before_time = now_time + timedelta(hours=hours)

    # Market 필터: money_line + spread + total
    markets_qs = Market.objects.filter(
        market_type__in=["money_line", "spread", "total"]
    ).prefetch_related(
        Prefetch(
            "lines",
            queryset=Line.objects.all()
        )
    )

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
        )

    # ================= 딕셔너리로 변환 =================
    all_events = []
    for e in events:
        event_dict = {
            "event_id": e.id,
            "league": e.league_name,
            "starts": e.starts,
            "home": e.home,
            "away": e.away,
            "periods": [],
        }

        for p in e.periods.all():
            period_dict = {
                "code": p.code,
                "description": p.description,
                "markets": [],
            }

            for m in p.markets.all():
                market_dict = {
                    "market_id": m.id,
                    "type": m.market_type,
                    "values": [],
                }

                if m.market_type == "money_line" and m.home and m.away:
                    market_dict["values"].append(
                        {"home": m.home, "draw": m.draw, "away": m.away}
                    )

                elif m.market_type == "spread":
                    for l in m.lines.all():
                        market_dict["values"].append(
                            {
                                "hdp": l.hdp,
                                "home_price": l.home_price,
                                "away_price": l.away_price,
                            }
                        )

                elif m.market_type == "total":
                    for l in m.lines.all():
                        market_dict["values"].append(
                            {
                                "points": l.points,
                                "under_price": l.under_price,
                                "over_price": l.over_price,
                            }
                        )

                if market_dict["values"]:
                    period_dict["markets"].append(market_dict)

            if period_dict["markets"]:
                event_dict["periods"].append(period_dict)

        if event_dict["periods"]:
            all_events.append(event_dict)

    return all_events


# def get_game():
#     event = Event.objects.get(sport_id=9)  # 실제 존재하는 이벤트 ID로 변경
#     print(event.__dict__)

if __name__ == "__main__":
    events_data = get_events(sport_id=9, hours=5)
    pprint.pprint(events_data)

    # get_game()
