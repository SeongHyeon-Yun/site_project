from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, LoginForm


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
                return redirect("main:home")
            else:
                messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


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
            user = form.save()
            login(request, user)
            return redirect("main:home")
    else:
        form = SignUpForm()

    return render(request, "accounts/sign_up.html", {"form": form})


# 고객센터 페이지
@never_cache
@login_required(login_url="accounts:login")
def customer(request):
    return render(request, "accounts/customer.html")


# 입출금 페이지
@never_cache
@login_required(login_url="accounts:login")
def deposit(request):
    return render(request, "accounts/deposit.html")


# 쪽지함 페이지
@never_cache
@login_required(login_url="accounts:login")
def message(request):
    return render(request, "accounts/message.html")
