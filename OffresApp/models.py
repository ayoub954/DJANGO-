from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction

from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule


class Offre(models.Model):
    class Statut(models.TextChoices):
        PROPOSEE = "proposee", "Proposee"
        ACCEPTEE = "acceptee", "Acceptee"
        REFUSEE = "refusee", "Refusee"
        RETIREE = "retiree", "Retiree"

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    delai_jours = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.PROPOSEE)
    date_proposition = models.DateField(auto_now_add=True)
    expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE, related_name="offres")
    transporteur = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name="offres",
        limit_choices_to={"type_entreprise": "transporteur"},
    )
    vehicule = models.ForeignKey(Vehicule, on_delete=models.PROTECT, related_name="offres")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(prix__gt=0), name="offre_prix_positif"),
            models.CheckConstraint(condition=models.Q(delai_jours__gte=1), name="offre_delai_min_1"),
            models.UniqueConstraint(
                fields=["expedition", "transporteur"],
                condition=models.Q(statut="proposee"),
                name="offre_une_proposee_par_transporteur_et_expedition",
                violation_error_message="Cette entreprise a deja une offre proposee sur cette expedition.",
            ),
        ]

    def clean(self):
        super().clean()
        erreurs = {}
        if self.transporteur_id and self.transporteur.type_entreprise != "transporteur":
            erreurs["transporteur"] = "L'offre doit etre proposee par une entreprise de type transporteur."
        if self.vehicule_id and self.transporteur_id and self.vehicule.entreprise_id != self.transporteur_id:
            erreurs["vehicule"] = "Le vehicule doit appartenir au transporteur qui fait l'offre."
        if self.expedition_id and not self.pk and self.expedition.statut != "publiee":
            erreurs["expedition"] = "On ne peut proposer une offre que sur une expedition publiee."
        if (
            self.expedition_id
            and self.transporteur_id
            and self.statut == self.Statut.PROPOSEE
            and Offre.objects.filter(
                expedition_id=self.expedition_id,
                transporteur_id=self.transporteur_id,
                statut=self.Statut.PROPOSEE,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            erreurs["transporteur"] = "Cette entreprise a deja une offre proposee sur cette expedition."
        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.statut == self.Statut.ACCEPTEE:
                Expedition.objects.filter(pk=self.expedition_id).update(
                    statut="attribuee"
                )
                Offre.objects.filter(
                    expedition_id=self.expedition_id, statut=self.Statut.PROPOSEE
                ).exclude(pk=self.pk).update(statut=self.Statut.REFUSEE)
                Vehicule.objects.filter(pk=self.vehicule_id).update(disponible=False)

    def __str__(self):
        return f"Offre {self.prix} DT / {self.delai_jours} j sur {self.expedition.reference}"
