import uuid

from django.db import models

from EntreprisesApp.models import Entreprise


def generer_reference():
    """Référence unique générée automatiquement, ex. EXP-3F9A2C7B."""
    return "EXP-" + uuid.uuid4().hex[:8].upper()


class Expedition(models.Model):
    class Statut(models.TextChoices):
        PUBLIEE = "publiee", "Publiée"
        ATTRIBUEE = "attribuee", "Attribuée"
        EN_COURS = "en_cours", "En cours"
        LIVREE = "livree", "Livrée"
        ANNULEE = "annulee", "Annulée"

    reference = models.CharField(max_length=12, unique=True, editable=False, default=generer_reference)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2)
    date_souhaitee = models.DateField()
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.PUBLIEE)
    # 1 entreprise (chargeur) publie * expéditions
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name="expeditions",
        limit_choices_to={"type_entreprise": Entreprise.TypeEntreprise.CHARGEUR},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference} : {self.ville_depart} → {self.ville_arrivee}"
