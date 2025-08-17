from django.urls import path
from . import views

app_name = "about"

urlpatterns = [
    path("sport/", views.sport, name="sport"),
    path("casino/", views.casino, name="casino"),
    path("slot/", views.slot, name="slot"),
]
