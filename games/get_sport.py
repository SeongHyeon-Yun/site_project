import requests
from datetime import timedelta, timezone as dt_timezone
from django.utils import timezone
import django, os, sys
from pathlib import Path
from dateutil.parser import isoparse

# ---------------- Django 설정 ----------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "new_bet.settings")
django.setup()

from accounts.models import Leagues, Event, Period, Market, Line


# ---------------- API 설정 ----------------
API_KEY = "0bff1c23f6msh61d123e9767cc5cp1bdd95jsn3db1e7cd86a1"
API_HOST = "pinnacle-odds.p.rapidapi.com"


# ✅ 리그 가져오기
def fetch_leagues(sport_id):
    url = f"https://{API_HOST}/kit/v1/leagues"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
    resp = requests.get(url, headers=headers, params={"sport_id": sport_id})
    data = resp.json()

    leagues = data.get("leagues", []) or data.get("data", {}).get("leagues", [])
    valid_leagues = [lg for lg in leagues if lg.get("event_count", 0) > 0]
    print(f"📌 리그 개수: {len(leagues)} / 사용 대상: {len(valid_leagues)}")

    for lg in valid_leagues:
        obj, created = Leagues.objects.update_or_create(
            id=lg["id"],
            defaults={
                "sport_id": lg["sport_id"],
                "name": lg["name"],
                "event_count": lg.get("event_count", 0),
            },
        )
        print(f"  ✅ 리그 {'생성' if created else '업데이트'}: {obj.name} (ID={obj.id})")

    return valid_leagues


# ✅ 이벤트/배당 가져오기
def fetch_events(sport_id, leagues):
    url = f"https://{API_HOST}/kit/v1/markets"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}

    now_time = timezone.now()
    until = now_time + timedelta(hours=12)

    for lg in leagues:
        params = {
            "sport_id": sport_id,
            "league_ids": lg["id"],
            "event_type": "prematch",
            "is_have_odds": "true",
        }

        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()
        events = data.get("events", []) or data.get("data", {}).get("events", [])
        print(f"📌 리그 {lg['name']} → 이벤트 개수: {len(events)}")

        for ev in events:
            # ✅ 경기 시작 시간 파싱 (UTC 기준)
            try:
                starts = isoparse(ev["starts"])
                if timezone.is_naive(starts):
                    starts = starts.replace(tzinfo=dt_timezone.utc)
            except Exception as e:
                print(f"⚠️ 시간 파싱 오류: {ev.get('starts')} / {e}")
                continue

            if not (now_time <= starts <= until):
                continue

            # ✅ 리그 확인
            try:
                league_obj = Leagues.objects.get(id=ev["league_id"])
            except Leagues.DoesNotExist:
                print(f"⚠️ 리그 없음 → Event 스킵: {ev['league_name']} (ID={ev['league_id']})")
                continue

            # ✅ 이벤트 저장
            event_obj, created = Event.objects.update_or_create(
                id=ev["event_id"],
                defaults={
                    "sport_id": ev["sport_id"],
                    "league": league_obj,
                    "league_name": ev["league_name"],
                    "starts": starts,
                    "home": ev["home"],
                    "away": ev["away"],
                    "event_type": ev["event_type"],
                },
            )
            print(f"  ✅ Event {'생성' if created else '업데이트'}: {event_obj.home} vs {event_obj.away}")

            # ✅ 기간(Period) 저장
            for period_key, period_val in ev.get("periods", {}).items():
                number = period_val.get("number", int(period_key.split("_")[1]))

                # cutoff 처리 (UTC 기준 tz-aware)
                cutoff = None
                if period_val.get("cutoff"):
                    try:
                        cutoff = isoparse(period_val["cutoff"])
                        if timezone.is_naive(cutoff):
                            cutoff = cutoff.replace(tzinfo=dt_timezone.utc)
                    except Exception as e:
                        print(f"⚠️ cutoff 파싱 오류: {period_val.get('cutoff')} / {e}")
                        cutoff = None

                period_obj, _ = Period.objects.update_or_create(
                    event=event_obj,
                    number=number,
                    defaults={
                        "code": period_key,
                        "description": period_val.get("description"),
                        "cutoff": cutoff,
                        "status": period_val.get("period_status", 1),
                    },
                )

                # ✅ Money Line
                ml = period_val.get("money_line")
                if ml:
                    Market.objects.update_or_create(
                        period=period_obj,
                        market_type="money_line",
                        defaults={
                            "home": ml.get("home"),
                            "away": ml.get("away"),
                            "draw": ml.get("draw"),
                        },
                    )

                # ✅ Spreads
                for spread in (period_val.get("spreads") or {}).values():
                    market_obj, _ = Market.objects.update_or_create(
                        period=period_obj,
                        market_type="spread",
                    )
                    Line.objects.update_or_create(
                        market=market_obj,
                        hdp=spread.get("hdp"),
                        defaults={
                            "home_price": spread.get("home"),
                            "away_price": spread.get("away"),
                            "alt_line_id": spread.get("alt_line_id"),
                            "max_bet": spread.get("max"),
                        },
                    )

                # ✅ Totals
                for total in (period_val.get("totals") or {}).values():
                    market_obj, _ = Market.objects.update_or_create(
                        period=period_obj,
                        market_type="total",
                    )
                    Line.objects.update_or_create(
                        market=market_obj,
                        points=total.get("points"),
                        defaults={
                            "over_price": total.get("over"),
                            "under_price": total.get("under"),
                            "alt_line_id": total.get("alt_line_id"),
                            "max_bet": total.get("max"),
                        },
                    )

                # ✅ Team Totals
                team_total = period_val.get("team_total") or {}
                for team, tt in team_total.items():
                    market_obj, _ = Market.objects.update_or_create(
                        period=period_obj,
                        market_type="team_total",
                        team=team,
                    )
                    Line.objects.update_or_create(
                        market=market_obj,
                        points=tt.get("points"),
                        defaults={
                            "over_price": tt.get("over"),
                            "under_price": tt.get("under"),
                        },
                    )


def clean_old_events():
    now_time = timezone.now()
    deleted, _ = Event.objects.filter(starts__lt=now_time).delete()
    print(f"🗑 지난 경기 {deleted}개 삭제 완료")


# ✅ 전체 동기화
def sync_all():
    SPORT_IDS = [1, 3, 4, 5, 7, 9, 10]
    for sid in SPORT_IDS:
        print(f"\n==================== [ Sport ID: {sid} ] ====================")
        leagues = fetch_leagues(sid)
        if leagues:
            fetch_events(sid, leagues)
        else:
            print("⚠️ 해당 종목에 유효한 리그 없음")
        print(f"✅ Sport ID {sid} 완료")

        clean_old_events()


if __name__ == "__main__":
    sync_all()
