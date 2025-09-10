from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from accounts.models import Money_list, User
import datetime
from django.db import connection
from django.contrib.auth.decorators import login_required

# Create your views here.


@csrf_exempt
@login_required(login_url="recoards:login")
def amount(request):
    amount = (
        Money_list.objects.filter(user=request.user)
        .filter(type="deposit")
        .order_by("-created_at")
    )
    return render(request, "amount/deposit.html", {"amount": amount})


@csrf_exempt
@login_required(login_url="recoards:login")
def money_exit(request):
    amount = (
        Money_list.objects.filter(user=request.user)
        .filter(type="withdraw")
        .order_by("-created_at")
    )
    return render(request, "amount/money_exit.html", {"amount": amount})


def get_today_money(username):
    qs = Money_list.objects.filter(
        username=username,
        created_at__date=datetime.date.today(),  # () ← 괄호 빠뜨리면 안돼요
        type="deposit",
    )
    print(qs.query)  # 👉 실제 SQL 확인
    return qs.count()


@csrf_exempt
@login_required(login_url="recoards:login")
def deposit(request):
    if request.method == "POST":
        data = json.loads(request.body)
        type_ = data.get("type")

        if type_ == "deposit":
            price = data.get("price")
            bonus = data.get("bonus")
            username = data.get("username")

            if bonus == "yes":
                today_count = get_today_money(username)
                print("오늘 입금 횟수:", today_count)
                if today_count == 0:
                    bonus_money = int(int(price) * 0.05)
                else:
                    bonus_money = int(int(price) * 0.03)
            else:
                bonus_money = 0

            money = Money_list.objects.create(
                user=request.user,  # FK → user_id 자동 채워짐
                username=request.user.username,  # 문자열 저장
                amount=price,  # 금액
                type=type_,  # 입금 / 출금
                bonus=bonus_money,  # 보너스
            )
        
        else :
            price = data.get("price")
            username = data.get("username")
            user = User.objects.get(username=username)
            user.money -= int(price)
            user.save()

            money = Money_list.objects.create(
                user=request.user,  # FK → user_id 자동 채워짐
                username=request.user.username,  # 문자열 저장
                amount=price,  # 금액
                type=type_,  # 입금 / 출금
            )
        return JsonResponse({"status": "success"})
    return render(request, "main/main.html")
