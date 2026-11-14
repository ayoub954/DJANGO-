from django.urls import path

from . import views

app_name = "vehicules"

urlpatterns = [
    path("", views.liste_vehicules, name="liste"),
    path("ajouter/", views.ajouter_vehicule, name="ajouter"),
    path("<int:pk>/", views.detail_vehicule, name="detail"),
    path("<int:pk>/modifier/", views.modifier_vehicule, name="modifier"),
    path("<int:pk>/supprimer/", views.supprimer_vehicule, name="supprimer"),
]
