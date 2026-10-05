import random
import string

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


def generer_user_id():
    """Génère un identifiant de 8 caractères : 'U' + 7 chiffres (ex. U4821937)."""
    return "U" + "".join(random.choices(string.digits, k=7))


class UtilisateurManager(UserManager):
    """Manager personnalisé : garantit la génération de user_id et l'attribution du rôle."""

    def _generer_id_unique(self):
        while True:
            uid = generer_user_id()
            if not self.model.objects.filter(user_id=uid).exists():
                return uid

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("user_id", self._generer_id_unique())
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("user_id", self._generer_id_unique())
        extra_fields.setdefault("role", Utilisateur.Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class Utilisateur(AbstractUser):
    class Role(models.TextChoices):
        CHARGEUR = "chargeur", "Chargeur"
        TRANSPORTEUR = "transporteur", "Transporteur"
        ADMIN = "admin", "Administrateur"

    # PK personnalisée : remplace le champ id par défaut d'AbstractUser
    user_id = models.CharField(primary_key=True, max_length=8, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CHARGEUR)
    telephone = models.CharField(max_length=20, blank=True)
    # first_name / last_name (nom, prénom) sont hérités d'AbstractUser
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UtilisateurManager()

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = Utilisateur.objects._generer_id_unique()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id} - {self.username} ({self.role})"


class Entreprise(models.Model):
    class TypeEntreprise(models.TextChoices):
        CHARGEUR = "chargeur", "Chargeur"
        TRANSPORTEUR = "transporteur", "Transporteur"

    raison_sociale = models.CharField(max_length=255)
    matricule_fiscal = models.CharField(max_length=17, unique=True)
    type_entreprise = models.CharField(max_length=20, choices=TypeEntreprise.choices)
    adresse = models.TextField()
    # Relation 1—1 : une entreprise est gérée par un compte utilisateur unique
    utilisateur = models.OneToOneField(
        "EntreprisesApp.Utilisateur",
        on_delete=models.CASCADE,
        related_name="entreprise",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.raison_sociale} ({self.type_entreprise})"
