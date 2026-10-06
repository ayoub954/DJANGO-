from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone


def valider_email_gmail(valeur):
    if not valeur.lower().endswith("@gmail.com"):
        raise ValidationError("Seuls les emails du domaine gmail.com sont acceptes.")


class Utilisateur(AbstractUser):
    user_id = models.CharField(
        max_length=8,
        primary_key=True,
        editable=False,
        validators=[
            RegexValidator(
                regex=r"^\d{2}user\d{2}$",
                message="user_id doit suivre le format AAuserNN.",
            )
        ],
    )
    email = models.EmailField(unique=True, validators=[valider_email_gmail])
    role = models.CharField(
        max_length=20,
        choices=[
            ("chargeur", "Chargeur"),
            ("transporteur", "Transporteur"),
            ("admin", "Admin"),
        ],
        default="chargeur",
    )
    telephone = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generer_user_id(self):
        prefixe = f"{timezone.now().year % 100:02d}user"
        dernier = (
            Utilisateur.objects.filter(user_id__startswith=prefixe)
            .order_by("-user_id")
            .values_list("user_id", flat=True)
            .first()
        )
        numero = int(dernier[-2:]) + 1 if dernier else 1
        if numero > 99:
            raise ValidationError("Nombre maximum d'utilisateurs atteint pour cette annee.")
        return f"{prefixe}{numero:02d}"

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self.generer_user_id()
        super().save(*args, **kwargs)


class Entreprise(models.Model):
    raison_sociale = models.CharField()
    matricule_fiscal = models.CharField(
        max_length=17,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$",
                message="Matricule fiscal invalide (ex. 1234567AAM000 ou 1234567/A/A/M/000).",
            )
        ],
    )
    type_entreprise = models.CharField(
        choices=[
            ("chargeur", "chargeur"),
            ("transporteur", "transporteur"),
        ]
    )
    adresse = models.TextField(validators=[MinLengthValidator(20)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gerant = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entrprise",
    )
