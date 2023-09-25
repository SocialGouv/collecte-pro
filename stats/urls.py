from django.urls import path

from . import views


app_name = "stats"

urlpatterns = [
    path('', views.Stats.as_view(), name='index'),
    path('call_get_statistique/', views.Stats.as_view(), name='call_get_statistique'),
    path('call_get_top_20/', views.Stats.call_get_top_20, name='call_get_top_20'), 
]
