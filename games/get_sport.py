import requests
from datetime import datetime, timedelta, timezone
import django, os, sys
from pathlib import Path
from django.utils import timezone as dj_timezone
from dateutil.parser import isoparse  # ✅ 안전한 ISO 파싱

# ---------------- Django 설정 ----------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "new_bet.settings")
django.setup()

from accounts.models import Leagues, Event, Market

# ---------------- API 설정 ----------------
API_KEY = "0bff1c23f6msh61d123e9767cc5cp1bdd95jsn3db1e7cd86a1"
API_HOST = "pinnacle-odds.p.rapidapi.com"


# ✅ 리그 가져오기 (event_count > 0 만)
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


# ✅ 이벤트/마켓 가져오기 (리그별 호출, 현재~10시간만 저장)
def fetch_events(sport_id, leagues):
    url = f"https://{API_HOST}/kit/v1/markets"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}

    now_utc = datetime.now(timezone.utc)
    until = now_utc + timedelta(hours=5)

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
            try:
                starts = isoparse(ev["starts"])
                if starts.tzinfo is None:
                    starts = starts.replace(tzinfo=timezone.utc)
            except Exception as e:
                print(f"⚠️ 시간 파싱 오류: {ev.get('starts')} / {e}")
                continue

            if not (now_utc <= starts <= until):
                continue

            try:
                league_obj = Leagues.objects.get(id=ev["league_id"])
            except Leagues.DoesNotExist:
                print(f"⚠️ 리그 없음 → Event 스킵: {ev['league_name']} (ID={ev['league_id']})")
                continue

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

            # ---- 마켓 저장 ----
            for period_key, period_val in ev.get("periods", {}).items():
                # Money Line
                ml = period_val.get("money_line")
                if ml:
                    Market.objects.update_or_create(
                        event=event_obj,
                        market_type="money_line",
                        period=period_key,
                        defaults={
                            "home": ml.get("home"),
                            "away": ml.get("away"),
                            "draw": ml.get("draw"),
                        },
                    )

                # Spread (핸디캡 여러 개 저장 가능)
                for spread in (period_val.get("spreads") or {}).values():
                    Market.objects.update_or_create(
                        event=event_obj,
                        market_type="spread",
                        period=period_key,
                        hdp=spread.get("hdp"),  # ✅ 핸디캡 값 포함시켜서 중복 방지
                        defaults={
                            "home": spread.get("home"),
                            "away": spread.get("away"),
                        },
                    )

                # Totals (오버언더 여러 개 저장 가능)
                for total in (period_val.get("totals") or {}).values():
                    Market.objects.update_or_create(
                        event=event_obj,
                        market_type="total",
                        period=period_key,
                        points=total.get("points"),  # ✅ 기준점 포함
                        defaults={
                            "over": total.get("over"),
                            "under": total.get("under"),
                        },
                    )


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


if __name__ == "__main__":
    sync_all()
