from django.urls import path

from . import views

app_name = "expeditions"

urlpatterns = [
    path("", views.liste_expeditions, name="liste"),
    path("home/", views.home, name="home"),
    path("welcome/<str:name>/", views.welcome, name="welcome"),
    path("<str:reference>/", views.detail_expedition, name="detail"),
    path("<str:reference>/supprimer/", views.supprimer_expedition, name="supprimer"),
]
