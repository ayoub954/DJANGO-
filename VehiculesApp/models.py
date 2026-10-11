from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from EntreprisesApp.models import Entreprise


class Vehicule(models.Model):
    class TypeVehicule(models.TextChoices):
        CAMIONNETTE = "camionnette", "Camionnette / utilitaire leger"
        FOURGON = "fourgon", "Fourgon"
        CAMION_PORTEUR = "camion_porteur", "Camion porteur"
        SEMI_REMORQUE = "semi_remorque", "Semi-remorque"

    # Capacite indicative (kg) par type de vehicule : (minimum, maximum)
    CAPACITES_KG = {
        TypeVehicule.CAMIONNETTE: (1, 1500),
        TypeVehicule.FOURGON: (1, 3500),
        TypeVehicule.CAMION_PORTEUR: (3500, 19000),
        TypeVehicule.SEMI_REMORQUE: (19000, 26000),
    }

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

    def capacite_max_type(self):
        return self.CAPACITES_KG[self.type_vehicule][1]

    def peut_transporter(self, poids_kg):
        return poids_kg <= min(self.capacite_kg, self.capacite_max_type())

    def clean(self):
        super().clean()
        erreurs = {}
        if self.entreprise_id and self.entreprise.type_entreprise != "transporteur":
            erreurs["entreprise"] = "Le vehicule doit appartenir a une entreprise de type transporteur."
        if self.type_vehicule in self.CAPACITES_KG and self.capacite_kg:
            minimum, maximum = self.CAPACITES_KG[self.type_vehicule]
            if not minimum <= self.capacite_kg <= maximum:
                erreurs["capacite_kg"] = (
                    f"La capacite d'un vehicule de type {self.get_type_vehicule_display()} "
                    f"doit etre comprise entre {minimum} et {maximum} kg."
                )
        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.immatriculation} ({self.get_type_vehicule_display()})"
