from django.urls import path
from . import views

app_name = "amount"

urlpatterns = [
    path("", views.amount, name="amount"),
    path("money_exit/", views.money_exit, name="money_exit"),
    path("deposit/", views.deposit, name="deposit"),

]
