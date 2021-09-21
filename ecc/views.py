from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def home(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("control-detail")
    return render(request, 'login/login.html')