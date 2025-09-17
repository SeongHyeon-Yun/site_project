import requests
import django, os, sys
from pathlib import Path
from decimal import Decimal
from django.db import transaction

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
    bet = (
        Bet.objects.values("event")
        .distinct()
        .filter(
            status="pending",
        )
    )

    for i in bet:
        event_id = i["event"]

        url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/details"

        querystring = {"event_id": event_id}

        headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}

        response = requests.get(url, headers=headers, params=querystring)

        data = response.json()

        for i in data["events"]:
            event_id = i["event_id"]
            game_finish_check = i["is_have_open_markets"]

            if game_finish_check == False:
                home_team = i["home_team_type"]
                for j in i["period_results"]:
                    num = j["number"]
                    settled_at = j["settled_at"]
                    if home_team == "Team1":
                        home_score = j["team_1_score"]
                        away_score = j["team_2_score"]
                    else:
                        home_score = j["team_2_score"]
                        away_score = j["team_1_score"]

                    # ✅ DB 저장
                    obj, created = GameResult.objects.update_or_create(
                        event=event_id,
                        game_num=str(num),
                        defaults={
                            "home_score": home_score,
                            "away_score": away_score,
                            "status": "finished" if j["status"] == 1 else "pending",
                            "settled_at": settled_at,
                        },
                    )
    return


def bet_game_check():
    bets = Bet.objects.filter(status="pending")

    for bet in bets:
        event_id = bet.event
        point = bet.point
        game_num = bet.game_num.replace("num_", "")
        pick = bet.pick
        status = bet.status

        if status == "pending":
            if pick == "홈승":
                game_result = GameResult.objects.filter(
                    event=event_id, game_num=game_num
                )
                for j in game_result:
                    print(j.home_score)
                    print(j.away_score)
                    if j.home_score > j.away_score:
                        bet.status = "won"
                        bet.save()
                    else:
                        bet.status = "lost"
                        bet.save()

            if pick == "원정승":
                game_result = GameResult.objects.filter(
                    event=event_id, game_num=game_num
                )
                for j in game_result:
                    print(j.home_score)
                    print(j.away_score)
                    if j.home_score < j.away_score:
                        bet.status = "won"
                        bet.save()
                    else:
                        bet.status = "lost"
                        bet.save()

            if pick == "무":
                game_result = GameResult.objects.filter(
                    event=event_id, game_num=game_num
                )
                for j in game_result:
                    print(j.home_score)
                    print(j.away_score)
                    if j.home_score == j.away_score:
                        bet.status = "won"
                        bet.save()
                    else:
                        bet.status = "lost"
                        bet.save()

            if pick == "오버":
                game_result = GameResult.objects.filter(
                    event=event_id, game_num=game_num
                )
                for j in game_result:
                    total_score = j.home_score + j.away_score
                    print(total_score)
                    if total_score > point:
                        bet.status = "won"
                        bet.save()
                    elif total_score == point:
                        bet.status = "push"
                        bet.odds = 1.0
                        bet.save()
                    else:
                        bet.status = "lost"
                        bet.save()

            if pick == "언더":
                game_result = GameResult.objects.filter(
                    event=event_id, game_num=game_num
                )
                for j in game_result:
                    total_score = j.home_score + j.away_score
                    print(total_score)
                    if total_score < point:
                        bet.status = "won"
                        bet.save()
                    elif total_score == point:
                        bet.status = "push"
                        bet.odds = 1.0
                        bet.save()
                    else:
                        bet.status = "lost"
                        bet.save()

            if pick == "홈핸승":
                game_result = GameResult.objects.filter(
                    event=event_id, game_num=game_num
                )
                for j in game_result:
                    handicap_home_score = j.home_score + point
                    print(handicap_home_score)
                    print(j.away_score)
                    if handicap_home_score > j.away_score:
                        bet.status = "won"
                        bet.save()
                    elif handicap_home_score == j.away_score:
                        bet.status = "push"
                        bet.odds = 1.0
                        bet.save()
                    else:
                        bet.status = "lost"
                        bet.save()

            if pick == "원정핸승":
                game_result = GameResult.objects.filter(
                    event=event_id, game_num=game_num
                )
                for j in game_result:
                    handicap_away_score = j.away_score + point
                    print(handicap_away_score)
                    print(j.home_score)
                    if handicap_away_score > j.home_score:
                        bet.status = "won"
                        bet.save()
                    elif handicap_away_score == j.home_score:
                        bet.status = "push"
                        bet.odds = 1.0
                        bet.save()
                    else:
                        bet.status = "lost"
                        bet.save()


def bet_slip_check():
    bet_slips = BetSlip.objects.filter(status="pending")

    for slip in bet_slips:
        bets = Bet.objects.filter(slip=slip)
        bet_status_list = list(bets.values_list("status", flat=True))

        # 총 배당 계산 (push=1.0 자동 반영됨)
        total_odds = Decimal(1.0)
        for bet in bets:
            total_odds *= Decimal(bet.odds)

        # 예상 당첨금 계산
        expected_amount = slip.stake * total_odds

        # 상태 판정
        if "lost" in bet_status_list:
            slip.status = "lost"
            slip.total_odds = float(total_odds)
            slip.expected_amount = 0

        elif all(status == "won" for status in bet_status_list):
            slip.status = "won"
            slip.total_odds = float(total_odds)
            slip.expected_amount = expected_amount
            with transaction.atomic():
                user = slip.user
                user.money += expected_amount
                user.save()

        elif "pending" in bet_status_list:
            # 아직 진행 중
            continue

        elif "push" in bet_status_list and all(
            status in ["won", "push"] for status in bet_status_list
        ):
            # ✅ won + push 조합 = 당첨 (push는 배당 1.0 반영됨)
            slip.status = "won"
            slip.total_odds = float(total_odds)
            slip.expected_amount = expected_amount
            with transaction.atomic():
                user = slip.user
                user.money += expected_amount
                user.save()

        slip.save()


if __name__ == "__main__":
    get_sport_result()
    bet_game_check()
    bet_slip_check()
