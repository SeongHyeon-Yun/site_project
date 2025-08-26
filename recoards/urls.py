from django.urls import path
from . import views

app_name = "recoards"

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("signUp/", views.sign_up, name="sign_up"),
    path("customer/", views.customer, name="customer"),
    path("customer_create/", views.customer_create, name="customer_create"),
    path("customer_detail/<int:pk>", views.customer_detail, name="customer_detail"),
    path("message/", views.message, name="message"),
    path("deposit/", views.deposit, name="deposit"),
    path("withdraw/", views.withdraw, name="withdraw"),
    path("deposit_list/", views.deposit_list, name="deposit_list"),
    path("withdraw_list/", views.withdraw_list, name="withdraw_list"),
]
