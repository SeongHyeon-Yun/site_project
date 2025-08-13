from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path("sport/", views.sport, name="sport")   
]
