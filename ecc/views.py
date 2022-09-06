from datetime import datetime

from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.shortcuts import redirect, render

from alerte.models import Alert


def home(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("control-detail")
    now = datetime.now()
    alerte = Alert.objects.filter(
        Q(start_date__lt=now) | Q(start_date=None)
    ).filter(
        Q(end_date__gt=now) | Q(end_date=None)
    ).first()
    return render(request, "login/login.html", {"alerte": alerte})
