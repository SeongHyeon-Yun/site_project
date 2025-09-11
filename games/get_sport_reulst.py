import requests
import django, os, sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "new_bet.settings")
django.setup()

from accounts.models import Bet, BetSlip

# ---------------- API 설정 ----------------
API_KEY = "0bff1c23f6msh61d123e9767cc5cp1bdd95jsn3db1e7cd86a1"
API_HOST = "pinnacle-odds.p.rapidapi.com"


def get_sport_result():
    bet = Bet.objects.all()
    for i in bet:
        if i.status == 'pending':
            url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/details"
            querystring = {"event_id": i.event}
            headers = {
                "x-rapidapi-key": API_KEY,
                "x-rapidapi-host": API_HOST,
            }
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()
            for event in data['events']:
                try:
                    print(event['period_results'])
                    for score in event['period_results']:
                        print(score)
                        if score['cancellation_reason'] != None:
                            print('경기가 취소되었습니다.')
                            bet = Bet.objects.filter(event=i.event)
                            for b in bet:
                                b.status = 'canceled'
                                b.save()
                        else:
                            game_num = Bet.objects.filter(event=i.event).filter(game_num=score['number'])
                            print(game_num)
                            for g in game_num:
                                print(g)

                except KeyError:
                    continue
                # if event['period_results'][0]['team_1_score'] > event['period_results'][0]['team_2_score']:
                #     winner = 'home'
                # elif event['period_results'][0]['team_1_score'] < event['period_results'][0]['team_2_score']:
                #     winner = 'away'
                # else:
                #     winner = 'draw'
                
                # if i.bet_type == winner:
                #     i.status = 'win'
                #     i.save()
                #     bet_slips = BetSlip.objects.filter(bet=i)
                #     for slip in bet_slips:
                #         slip.status = 'win'
                #         slip.save()
                # else:
                #     i.status = 'lose'
                #     i.save()
                #     bet_slips = BetSlip.objects.filter(bet=i)
                #     for slip in bet_slips:
                #         slip.status = 'lose'
                #         slip.save()
        # get_sport_reulst_api(i.event)


# def get_sport_reulst_api(event_id):
#     url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/details"

#     querystring = {"event_id": event_id}

#     headers = {
#         "x-rapidapi-key": "0bff1c23f6msh61d123e9767cc5cp1bdd95jsn3db1e7cd86a1",
#         "x-rapidapi-host": "pinnacle-odds.p.rapidapi.com",
#     }

#     response = requests.get(url, headers=headers, params=querystring)

#     data = response.json()
#     for event in data['events']:
#         print(event['period_results'])

#     return data


if __name__ == "__main__":  
    get_sport_result()
