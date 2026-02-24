from django.urls import path

from . import views


app_name = "stats"

urlpatterns = [
    path('', views.Stats.as_view(), name='index'),
    path('call_get_statistique/', views.Stats.as_view(), name='call_get_statistique'),
    path('call_get_top_20/', views.Stats.call_get_top_20, name='call_get_top_20'), 
    path('call_get_espace_depot_modele/', views.Stats.call_get_espace_depot_modele, name='call_get_espace_depot_modele'), 
    path('call_get_espace_depot_elig_supp/', views.Stats.call_get_espace_depot_elig_supp, name='call_get_espace_depot_elig_supp'),
    path('call_get_repondants_orphelins/', views.Stats.call_get_repondants_orphelins, name='call_get_repondants_orphelins'), 
    path('call_get_liste_utilisateurs/', views.Stats.call_get_liste_utilisateurs, name='call_get_liste_utilisateurs'), 
]
