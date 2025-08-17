from django.shortcuts import render

# Create your views here.
def sport(request):
    return render(request, "about/sport.html")

def casino(request):
    return render(request, "about/casino.html")

def slot(request):
    return render(request, "about/slot.html")