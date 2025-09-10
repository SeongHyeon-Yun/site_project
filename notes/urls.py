from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    path("notice/", views.notice, name="notice"),
    path("check_day/", views.check_day, name="check_day"),
    path("event/", views.event, name="event"),
    path('post_detail/<int:pk>', views.post_detail, name="post_detail"),
    path('bet_list/', views.bet_list, name="bet_list")
]
