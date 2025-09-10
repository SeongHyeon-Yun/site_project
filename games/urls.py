from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path("sport/", views.sport, name="sport"),
    path("special/", views.special, name="special"),
    path("casino/", views.casino, name="casino"),
    path("slot/", views.slot, name="slot"),
    path("slot_detail/", views.slot_detail, name="slot_detail"),
    path("runCasino/", views.casino_start, name="casino_start"),
    path("runSlot/", views.slot_start, name="slot_start"),
    path("submit/", views.submit_bet, name="submit"),
    path("money_change/", views.casino_money_change, name="money_change"),
]
