from django.urls import path

from . import views


app_name = "presentation"

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('who', views.Who.as_view(), name='who'),
    path('test', views.Test.as_view(), name='test'),
    path('faq', views.Faq.as_view(), name='faq'),
]
