from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request, 'accounts/login.html')

def sign_up(request):
    return render(request, 'accounts/sign_up.html')

def change_info(request):
    return render(request, "accounts/change_info.html")
