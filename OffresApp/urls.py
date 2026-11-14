from django.urls import path

from . import views

app_name = "offres"

urlpatterns = [
    path("", views.liste_offres, name="liste"),
    path("ajouter/", views.ajouter_offre, name="ajouter"),
    path("<int:pk>/", views.detail_offre, name="detail"),
    path("<int:pk>/modifier/", views.modifier_offre, name="modifier"),
    path("<int:pk>/supprimer/", views.supprimer_offre, name="supprimer"),
]
