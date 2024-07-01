from django.urls import path

from . import views


app_name = "presentation"

urlpatterns = [
    path('', views.Accueil.as_view(), name='accueil'),
    path('presentation', views.Presentation.as_view(), name='presentation'),
    path('demo', views.demo, name='demo'),
    path('simple-captcha-endpoint', views.simple_captcha_endpoint, name='simple-captcha-endpoint'),
    path('validationFormulaire', views.validationFormulaire, name='validationFormulaire'),

]
