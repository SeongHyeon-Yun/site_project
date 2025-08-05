from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login, name="login"),  # 루트(/) 요청 처리
    path("signUp/", views.sign_up, name="sign_up"),  # 루트(/) 요청 처리
    path("changeInfo/", views.change_info, name="change_info"),  # 루트(/) 요청 처리
]
