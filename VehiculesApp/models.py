from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from EntreprisesApp.models import Entreprise


class Vehicule(models.Model):
    class TypeVehicule(models.TextChoices):
        CAMIONNETTE = "camionnette", "Camionnette"
        FOURGON = "fourgon", "Fourgon"
        CAMION_PORTEUR = "camion_porteur", "Camion porteur"
        SEMI_REMORQUE = "semi_remorque", "Semi-remorque"

    immatriculation = models.CharField(max_length=20, unique=True)
    type_vehicule = models.CharField(max_length=20, choices=TypeVehicule.choices)
    capacite_kg = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name="vehicules",
        limit_choices_to={"type_entreprise": "transporteur"},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacite_kg__gt=0),
                name="vehicule_capacite_kg_positive",
            )
        ]

    def clean(self):
        if self.entreprise_id and self.entreprise.type_entreprise != "transporteur":
            raise ValidationError(
                {"entreprise": "Le vehicule doit appartenir a une entreprise de type transporteur."}
            )

    def __str__(self):
        return f"{self.immatriculation} ({self.get_type_vehicule_display()})"
