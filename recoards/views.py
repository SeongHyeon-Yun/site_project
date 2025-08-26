from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import SignUpForm, LoginForm
from accounts.models import Post


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
    return render(request, "recoards/deposit.html")


# 출금 페이지
@never_cache
@login_required(login_url="recoards:login")
def withdraw(request):
    return render(request, "recoards/withdraw.html")


# 입금내역 페이지
@never_cache
@login_required(login_url="recoards:login")
def deposit_list(request):
    return render(request, "recoards/deposit_list.html")


# 출금내역 페이지
@never_cache
@login_required(login_url="recoards:login")
def withdraw_list(request):
    return render(request, "recoards/withdraw_list.html")


# 쪽지함 페이지
@never_cache
@login_required(login_url="recoards:login")
def message(request):
    return render(request, "recoards/message.html")
