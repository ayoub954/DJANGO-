from django.db import models, transaction

from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule


class Offre(models.Model):
    class Statut(models.TextChoices):
        PROPOSEE = "proposee", "Proposée"
        ACCEPTEE = "acceptee", "Acceptée"
        REFUSEE = "refusee", "Refusée"
        RETIREE = "retiree", "Retirée"

    # Correction 1 : montant → DecimalField (et non CharField)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    # Correction 2 : un délai ne peut pas être négatif → PositiveIntegerField
    delai_jours = models.PositiveIntegerField()
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.PROPOSEE)
    # Correction 3 : date fixée à la création (auto_now_add), pas à chaque save (auto_now)
    date_proposition = models.DateField(auto_now_add=True)

    # 1 expédition reçoit * offres
    expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE, related_name="offres")
    # 1 entreprise transporteur propose * offres
    transporteur = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name="offres",
        limit_choices_to={"type_entreprise": Entreprise.TypeEntreprise.TRANSPORTEUR},
    )
    # 1 véhicule est assigné à * offres — obligatoire (pas de null=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.PROTECT, related_name="offres")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Correction 4 : l'acceptation d'une offre déclenche les effets en cascade
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.statut == self.Statut.ACCEPTEE:
                # l'expédition passe à "attribuée"
                Expedition.objects.filter(pk=self.expedition_id).update(
                    statut=Expedition.Statut.ATTRIBUEE
                )
                # les autres offres encore proposées sont refusées
                Offre.objects.filter(
                    expedition_id=self.expedition_id, statut=self.Statut.PROPOSEE
                ).exclude(pk=self.pk).update(statut=self.Statut.REFUSEE)
                # le véhicule assigné n'est plus disponible
                Vehicule.objects.filter(pk=self.vehicule_id).update(disponible=False)

    def __str__(self):
        return f"Offre {self.prix} DT / {self.delai_jours} j sur {self.expedition.reference}"
