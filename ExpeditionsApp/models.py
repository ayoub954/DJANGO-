from django.db import models
from EntreprisesApp.models import Entreprise


class Expedition(models.Model):
    reference = models.CharField(max_length=20, unique=True)
    ville_depart = models.CharField()
    ville_arrivee = models.CharField()
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2)
    date_souhaitee = models.DateField()
    description = models.TextField()
    statut = models.CharField(
        max_length=30,
        choices=[
            ("publiee", "publiee"),
            ("attribuee", "attribuee"),
            ("en_cours", "en_cours"),
            ("livree", "livree"),
            ("annulee", "annulee"),
        ],
        default="publiee",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name="expedition",
    )
