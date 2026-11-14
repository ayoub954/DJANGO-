from django import forms

from .models import Offre


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ["expedition", "transporteur", "vehicule", "prix", "delai_jours", "statut"]
