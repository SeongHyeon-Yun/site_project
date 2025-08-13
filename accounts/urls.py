from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("signUp/", views.sign_up, name="sign_up"),
    path("customer/", views.customer, name="customer"),
]
