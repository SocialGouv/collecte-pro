from django.urls import path

from . import views


app_name = "presentation"

urlpatterns = [
    path('', views.Accueil.as_view(), name='accueil'),
    path('presentation', views.Presentation.as_view(), name='presentation'),
]
