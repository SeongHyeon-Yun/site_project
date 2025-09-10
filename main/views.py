from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

@never_cache
@login_required(login_url="recoards:login")
def home(request):
    return render(request, "main/main.html")
