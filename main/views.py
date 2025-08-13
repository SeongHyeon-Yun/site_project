from django.shortcuts import render


def home(request):
    if request.user.is_authenticated:
        username = request.user.username
        nickname = request.user.nickname  # 커스텀 User 필드도 접근 가능
    else:
        username = None
        nickname = None

    return render(
        request,
        "main/main.html",
        {
            "username": username,
            "nickname": nickname,
        },
    )
