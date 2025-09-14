import requests
import django, os, sys
from pathlib import Path

# ---------------- Django 환경 설정 ----------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "new_bet.settings")
django.setup()

from accounts.models import Bet, GameResult, BetSlip
from django.db import transaction

# ---------------- API 설정 ----------------
API_KEY = "0bff1c23f6msh61d123e9767cc5cp1bdd95jsn3db1e7cd86a1"
API_HOST = "pinnacle-odds.p.rapidapi.com"


def get_sport_result():
    # 1. 중복 없는 경기만 가져오기
    events = (
        Bet.objects.filter(status="pending").values_list("event", flat=True).distinct()
    )

    for event_id in events:
        url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/details"
        querystring = {"event_id": event_id}
        headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        for event in data.get("events", []):
            home_team_type = event.get("home_team_type", "Team1")  # 기본값 Team1

            for score in event.get("period_results", []):
                # 2. 홈/원정 점수 매핑
                if home_team_type == "Team1":
                    home_score = score["team_1_score"]
                    away_score = score["team_2_score"]
                else:  # Team2
                    home_score = score["team_2_score"]
                    away_score = score["team_1_score"]

                # 3. 경기 결과 저장
                result, _ = GameResult.objects.update_or_create(
                    event=event_id,
                    game_num=f"num_{score['number']}",
                    defaults={
                        "home_score": home_score,
                        "away_score": away_score,
                        "status": (
                            "canceled" if score["cancellation_reason"] else "finished"
                        ),
                        "settled_at": score.get("settled_at"),
                    },
                )
    return

def judge_bet(bet, result):
    """
    개별 베팅 결과 판정
    bet: Bet 객체
    result: GameResult 객체
    return: "won" / "lost" / "canceled" / "push"
    """

    home = result.home_score
    away = result.away_score
    total = home + away

    pick = bet.pick.strip()  # 문자열 안전 처리
    point = bet.point

    # 무효 경기
    if result.status == "canceled":
        return "canceled"

    # ---- 승무패 ----
    if pick in ["홈승", "home"]:
        return "won" if home > away else "lost"
    if pick in ["원정승", "away"]:
        return "won" if away > home else "lost"
    if pick in ["무", "draw"]:
        return "won" if home == away else "lost"

    # ---- 오버/언더 ----
    if pick in ["오버", "오바", "over"]:
        if point is None:
            return "pending"
        if total > point:
            return "won"
        elif total == point:  # 기준점과 같으면 → 적중특례
            return "push"
        else:
            return "lost"

    if pick in ["언더", "under"]:
        if point is None:
            return "pending"
        if total < point:
            return "won"
        elif total == point:  # 기준점과 같으면 → 적중특례
            return "push"
        else:
            return "lost"

    # ---- 핸디캡 ----
    if pick in ["홈핸승", "handicap_home"]:
        if point is None:
            return "pending"
        if (home + point) > away:
            return "won"
        elif (home + point) == away:  # 무승부 → 적중특례
            return "push"
        else:
            return "lost"

    if pick in ["원정핸승", "handicap_away"]:
        if point is None:
            return "pending"
        if (away + point) > home:
            return "won"
        elif (away + point) == home:  # 무승부 → 적중특례
            return "push"
        else:
            return "lost"

    # 정의되지 않은 pick → 판정 보류
    return "pending"

if __name__ == "__main__":
    get_sport_result()
