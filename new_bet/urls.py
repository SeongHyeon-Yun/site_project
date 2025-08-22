from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("accounts/", include("accounts.urls")),
    path("payment/", include("payment.urls")),
    path("games/", include("games.urls")),
    path("about/", include("about.urls")),
    path("notes/", include("notes.urls")),
]
