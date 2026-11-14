from django.urls import path

from . import views

app_name = "entreprises"

urlpatterns = [
    path("", views.liste_entreprises, name="liste"),
    path("ajouter/", views.ajouter_entreprise, name="ajouter"),
    path("<int:pk>/", views.detail_entreprise, name="detail"),
    path("<int:pk>/modifier/", views.modifier_entreprise, name="modifier"),
    path("<int:pk>/supprimer/", views.supprimer_entreprise, name="supprimer"),
]
