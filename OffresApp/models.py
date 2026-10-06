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

    
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    
    delai_jours = models.PositiveIntegerField()
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

    def save(self, *args, **kwargs):
        
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
