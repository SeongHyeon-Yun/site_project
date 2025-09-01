import requests, os, pprint, json, sys
import django
from pathlib import Path
from datetime import datetime, timedelta, timezone as dt_timezone
from django.utils import timezone
import argparse

# -------------------------------------------
GET_DATA = [1, 3, 4, 5, 7, 9, 10]
TODAY = datetime.now().strftime("%Y-%m-%d")
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_DIR = BASE_DIR / "games/json"
ROOT_DIR = BASE_DIR.parent
CACHE_EXPIRE_MINUTES = 30

sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "new_bet.settings")
django.setup()

from accounts.models import Leagues, Market, Event

# --------------------------------------

# ✅ 공통 JSON 저장 함수
def save_json(data, filename):
    folder_path = JSON_DIR / f"leagues_{TODAY}"
    folder_path.mkdir(parents=True, exist_ok=True)  # 폴더 없으면 생성

    filepath = folder_path / filename

    # 캐시 파일이 이미 있으면 검사
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                old_data = json.load(f)
            except json.JSONDecodeError:
                old_data = {}

        # 저장된 데이터에 timestamp 있으면 확인
        if "timestamp" in old_data:
            cached_time = datetime.fromisoformat(old_data["timestamp"])
            if datetime.now() - cached_time < timedelta(minutes=CACHE_EXPIRE_MINUTES):
                print(f"👉 캐시 사용 (아직 {CACHE_EXPIRE_MINUTES}분 안 지남)")
                return old_data["data"]

    # 새로 저장
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            {"timestamp": datetime.now().isoformat(), "data": data},
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"✅ 새 데이터 저장: {filepath}")
    return data


# 공통 json 읽기 함수
def load_json(filename):
    folder_path = JSON_DIR / f"leagues_{TODAY}"
    filepath = folder_path / filename

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


# 원본 리그 목록 가져오기
def get_league(num):
    url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/leagues"
    querystring = {"sport_id": num}
    headers = {
        "x-rapidapi-key": "0bff1c23f6msh61d123e9767cc5cp1bdd95jsn3db1e7cd86a1",
        "x-rapidapi-host": "pinnacle-odds.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    save_json(data, f"original_league_{TODAY}_{num}.json")  # ✅ 단순 저장

    return data


# 원본 리그 슬라이싱 하기
def get_slicing_league(num):

    file_name = f"original_league_{TODAY}_{num}.json"
    mapping_name = f"mapping_league_{TODAY}_{num}.json"
    data = load_json(file_name)

    league_list = []

    for i in data["data"]["leagues"]:
        event_count = i["event_count"]
        if event_count > 0:
            id = i["id"]
            sport_id = i["sport_id"]
            name = i["name"]

            league_list.append(
                {
                    "id": id,
                    "sport_id": sport_id,
                    "name": name,
                    "event_count": event_count,
                }
            )

    save_json(league_list, mapping_name)
    model_insert(league_list)

    return league_list


# 슬라이싱 리그 db 업데이트
def model_insert(league_list):
    for league in league_list:
        obj, created = Leagues.objects.update_or_create(
            id=league["id"],  # PK 기준
            defaults={
                "sport_id": league["sport_id"],
                "name": league["name"],
                "event_count": league["event_count"],
            },
        )
    return


# 이벤트 경기 가져오기
def get_event_games(num):
    data = get_slicing_league(num)

    event_list = []
    for i in data:
        event_list.append(
            {
                "sport_id": i["sport_id"],
                "league_ids": i["id"],
                "event_type": "prematch",
                "is_have_odds": "true",
            }
        )

    for m in event_list:
        event = event_game_api(m)
        filename = f"original_event_{TODAY}_{m['league_ids']}.json"
        event_save_json(event, filename)
        event_load_json(m["league_ids"])
    return


# 이벤트 경기 api 호출
def event_game_api(params):
    url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/markets"
    querystring = params
    headers = {
        "x-rapidapi-key": "0bff1c23f6msh61d123e9767cc5cp1bdd95jsn3db1e7cd86a1",
        "x-rapidapi-host": "pinnacle-odds.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    return data


# 이벤트 경기 js 저장
def event_save_json(data, filename):
    folder_path = JSON_DIR / f"event_{TODAY}"
    folder_path.mkdir(parents=True, exist_ok=True)  # 폴더 없으면 생성

    filepath = folder_path / filename

    # 캐시 파일이 이미 있으면 검사
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                old_data = json.load(f)
            except json.JSONDecodeError:
                old_data = {}

        # 저장된 데이터에 timestamp 있으면 확인
        if "timestamp" in old_data:
            cached_time = datetime.fromisoformat(old_data["timestamp"])
            if datetime.now() - cached_time < timedelta(minutes=CACHE_EXPIRE_MINUTES):
                print(f"👉 캐시 사용 (아직 {CACHE_EXPIRE_MINUTES}분 안 지남)")
                return old_data["data"]

    # 새로 저장
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            {"timestamp": datetime.now().isoformat(), "data": data},
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"✅ 새 데이터 저장: {filepath}")
    return data


# 이벤트 경기 json 읽기
def event_load_json(league_ids):
    folder_path = JSON_DIR / f"event_{TODAY}"
    file_name = f"original_event_{TODAY}_{league_ids}.json"
    filepath = folder_path / file_name

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    event_slicing(data)

    return


def event_slicing(data):
    print("📌 event_slicing 시작")
    events = data.get("data", {}).get("events", [])
    print("이벤트 개수:", len(events))

    for i in events:
        # ✅ 리그 존재 여부 확인 (없으면 스킵)
        league_id = i["league_id"]
        if not Leagues.objects.filter(id=league_id).exists():
            print(f"⚠️ 리그 없음 (league_id={league_id}) → 이벤트 {i['event_id']} 스킵")
            continue

        starts = i["starts"]
        if isinstance(starts, str):
            starts = datetime.fromisoformat(starts)

        # tz 정보 없으면 UTC로 지정 후 한국시간으로 변환
        if timezone.is_naive(starts):
            starts = timezone.make_aware(starts, dt_timezone.utc)
            
        starts = timezone.localtime(starts, timezone=timezone.get_fixed_timezone(9 * 60))

        # ✅ 이벤트 저장
        event_obj, _ = Event.objects.update_or_create(
            id=i["event_id"],
            defaults={
                "sport_id": i["sport_id"],
                "league_id": league_id,
                "league_name": i["league_name"],
                "starts": starts,
                "home": i["home"],
                "away": i["away"],
                "event_type": i["event_type"],
            },
        )

        # ✅ 마켓 저장
        for period_key, period_val in i.get("periods", {}).items():
            # money_line
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

            # spreads
            for spread in (period_val.get("spreads") or {}).values():
                Market.objects.update_or_create(
                    event=event_obj,
                    market_type="spread",
                    period=period_key,
                    defaults={
                        "hdp": spread.get("hdp"),
                        "home": spread.get("home"),
                        "away": spread.get("away"),
                    },
                )

            # totals
            for total in (period_val.get("totals") or {}).values():
                Market.objects.update_or_create(
                    event=event_obj,
                    market_type="total",
                    period=period_key,
                    defaults={
                        "points": total.get("points"),
                        "over": total.get("over"),
                        "under": total.get("under"),
                    },
                )

        print("✅ 저장됨:", event_obj.id)


def sync_all():
    """전체 리그 + 전체 경기 싱크"""
    print("🚀 전체 스포츠 데이터 수집 시작")
    for sport_id in GET_DATA:
        print(f"\n==================== [ Sport ID: {sport_id} ] ====================")
        try:
            # 1. 원본 리그 저장
            get_league(sport_id)

            # 2. 리그 슬라이싱 + DB 저장
            leagues = get_slicing_league(sport_id)
            print(f"리그 {len(leagues)}개 저장 완료")

            # 3. 이벤트 경기 가져오기 + DB 저장
            get_event_games(sport_id)

        except Exception as e:
            print(f"❌ 오류 발생 (sport_id={sport_id}): {e}")
    print("\n✅ 전체 스포츠 데이터 수집 완료")


def sync_today():
    """오늘 경기만 업데이트"""
    print("🚀 오늘 경기 업데이트 시작")
    today = datetime.now().date()

    for sport_id in GET_DATA:
        print(
            f"\n==================== [ Sport ID: {sport_id} (오늘 경기만) ] ===================="
        )
        try:
            leagues = get_slicing_league(sport_id)
            today_events = Event.objects.filter(sport_id=sport_id, starts__date=today)

            if not today_events.exists():
                print("⚠️ 오늘 예정된 경기 없음 → 스킵")
                continue

            get_event_games(sport_id)

        except Exception as e:
            print(f"❌ 오류 발생 (sport_id={sport_id}): {e}")
    print("\n✅ 오늘 경기 업데이트 완료")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["all", "today"],
        default="all",
        help="실행 모드: all=전체 싱크, today=오늘 경기만",
    )
    args = parser.parse_args()

    if args.mode == "all":
        sync_all()
    elif args.mode == "today":
        sync_today()
