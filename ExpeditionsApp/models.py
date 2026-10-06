from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from EntreprisesApp.models import Entreprise


class Expedition(models.Model):
    reference = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        validators=[
            RegexValidator(
                regex=r"^EXP-\d{2}-\d{5}$",
                message="La reference doit suivre le format EXP-AA-NNNNN.",
            )
        ],
    )
    ville_depart = models.CharField()
    ville_arrivee = models.CharField()
    poids_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
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
        limit_choices_to={"type_entreprise": "chargeur"},
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(poids_kg__gt=0),
                name="expedition_poids_kg_positif",
            )
        ]

    @classmethod
    def generer_reference(cls):
        prefixe = f"EXP-{timezone.now().year % 100:02d}-"
        derniere = (
            cls.objects.filter(reference__startswith=prefixe)
            .order_by("-reference")
            .values_list("reference", flat=True)
            .first()
        )
        numero = int(derniere[-5:]) + 1 if derniere else 1
        if numero > 99999:
            raise ValidationError("Nombre maximum d'expeditions atteint pour cette annee.")
        return f"{prefixe}{numero:05d}"

    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != "chargeur":
            raise ValidationError(
                {"entreprise": "L'expedition doit appartenir a une entreprise de type expediteur."}
            )

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generer_reference()
        super().save(*args, **kwargs)
