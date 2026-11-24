from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Entreprise, Utilisateur


class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ["raison_sociale", "matricule_fiscal", "type_entreprise", "adresse", "gerant"]


class InscriptionForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ["username", "email", "telephone", "role"]
