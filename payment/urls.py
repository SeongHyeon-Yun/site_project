from django.urls import path
from . import views

urlpatterns = [
    path("depoist/", views.deposit, name="deposit"),
]
