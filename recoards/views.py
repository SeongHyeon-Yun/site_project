from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import SignUpForm, LoginForm
from accounts.models import Post, Deposit


# IP 주소 가져오기
def get_client_ip(request):
    # Cloudflare 우선
    cf_ip = request.META.get("HTTP_CF_CONNECTING_IP")
    if cf_ip:
        return cf_ip

    # 일반적인 프록시 (Nginx)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    # 마지막 fallback
    return request.META.get("REMOTE_ADDR")


@never_cache
def user_login(request):
    if request.user.is_authenticated:
        return redirect("main:home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # ✅ 로그인 성공 시 IP 저장 + 로그 찍기
                ip = get_client_ip(request)
                print("🔎 로그인 META:", request.META)  # 전체 META 출력
                print("🔎 X_FORWARDED_FOR:", request.META.get("HTTP_X_FORWARDED_FOR"))
                print("🔎 X_REAL_IP:", request.META.get("HTTP_X_REAL_IP"))
                print("🔎 REMOTE_ADDR:", request.META.get("REMOTE_ADDR"))
                print("🔎 get_client_ip:", ip)

                user.ip_address = ip
                user.save(update_fields=["ip_address"])
                # git cicd 추가

                return redirect("main:home")
            else:
                messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
    else:
        form = LoginForm()

    return render(request, "recoards/login.html", {"form": form})


def user_logout(request):
    logout(request)  # 세션 종료
    return redirect("main:home")  # 로그아웃 후 이동할 페이지


@never_cache
def sign_up(request):
    if request.user.is_authenticated:
        return redirect("main:home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # 아직 DB 저장 안 함
            user.is_active = False  # 무조건 비활성으로
            user.save()
            login(request, user)
            return redirect("main:home")
    else:
        form = SignUpForm()

    return render(request, "recoards/sign_up.html", {"form": form})


# 고객센터 페이지
@never_cache
@login_required(login_url="recoards:login")
def customer(request):
    username = request.user.username
    post = Post.objects.filter(type="customer", username=username)
    return render(request, "recoards/customer.html", {"post": post})


# 고객센터 글작성 페이지
@never_cache
@login_required(login_url="recoards:login")
def customer_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        contents = request.POST.get("contents")
        customer = request.POST.get("customer")
        username = request.POST.get("username")

        if not title:
            error_message = "제목을 입력 하세요"
            return render(
                request,
                "recoards/customer_create.html",
                {"error_message": error_message},
            )

        post = Post.objects.create(
            title=title, content=contents, type=customer, username=username
        )

        return redirect("recoards:customer")

    return render(request, "recoards/customer_create.html")


# 고객센터 글보기 페이지
@never_cache
@login_required(login_url="recoards:login")
def customer_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "recoards/customer_detail.html", {"post": post})


# 입금 페이지
@never_cache
@login_required(login_url="recoards:login")
def deposit(request):
    if request.method == "POST":
        amount = request.POST.get("amount", "0").replace(",", "")
        bonus = request.POST.get("bonus")
        username = request.POST.get("username")
        yes_no = "no"
        type = "deposit"

        if amount is None or amount == "":
            messages.error(request, "금액을 입력하세요.")
            return redirect("recoards:deposit")

        if duplicate := Deposit.objects.filter(
            username=username, yes_no=yes_no
        ).exists():
            messages.error(request, "이미 입금 신청이 대기중입니다.")
            return redirect("recoards:deposit")

        if bonus == "yes":
            check_object = Deposit.objects.filter(username=username).exists()
            if not check_object:
                bonus_money = int(amount) * 0.05
            else:
                bonus_money = int(amount) * 0.03
        else:
            bonus_money = 0

        deposit = Deposit.objects.create(
            user_id=request.user.id,
            username=username,
            amount=int(amount),
            bouns=bonus_money,
            yes_no=yes_no,
            type=type,
        )

        deposit.save()

        return redirect("recoards:deposit_list")
    return render(request, "recoards/deposit.html")


# 출금 페이지
@never_cache
@login_required(login_url="recoards:login")
def withdraw(request):
    if request.method == "POST":
        money = int(request.POST.get("get_money"))
        amount_str = request.POST.get("amount", "0").replace(",", "")
        username = request.POST.get("username")
        type = "withdraw"
        yes_no = "no"

        if amount_str == "":
            amount = 0
        else:
            amount = int(amount_str)

        if amount == 0:
            messages.error(request, "금액을 확인하세요.")
        elif amount > money:
            messages.error(request, "보유머니가 부족합니다.")

            return redirect("recoards:withdraw")

        print(amount)
        print(username)
        print(type)

        withdraw = Deposit.objects.create(
            user_id=request.user.id,
            username=username,
            amount=amount,
            type=type,
            yes_no=yes_no,
        )
        request.user.money -= amount
        withdraw.save()

        return redirect("recoards:withdraw")
    return render(request, "recoards/withdraw.html")


# 입금내역 페이지
@never_cache
@login_required(login_url="recoards:login")
def deposit_list(request):
    username = request.user.username
    deposits = Deposit.objects.filter(username=username).order_by("-created_at")
    return render(request, "recoards/deposit_list.html", {"deposits": deposits})


# 출금내역 페이지
@never_cache
@login_required(login_url="recoards:login")
def withdraw_list(request):
    username = request.user.username
    deposits = Deposit.objects.filter(username=username).order_by("-created_at")
    return render(request, "recoards/withdraw_list.html", {"deposits": deposits})


# 쪽지함 페이지
@never_cache
@login_required(login_url="recoards:login")
def message(request):
    return render(request, "recoards/message.html")
