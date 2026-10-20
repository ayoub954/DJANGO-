from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from VehiculesApp.models import Vehicule

from .models import Entreprise, Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ("user_id", "username", "email", "role", "telephone", "is_active", "created_at")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("user_id", "username", "email", "telephone")
    list_editable = ("is_active",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25
    readonly_fields = ("user_id", "created_at", "updated_at", "last_login", "date_joined")
    fieldsets = (
        ("Identite", {"fields": ("user_id", "username", "password", "first_name", "last_name")}),
        ("Contact et role", {"fields": ("email", "telephone", "role")}),
        ("Droits", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Suivi", {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {"fields": ("username", "email", "telephone", "role", "password1", "password2")}),
    )


class VehiculeInline(admin.TabularInline):
    model = Vehicule
    extra = 1
    fields = ("immatriculation", "type_vehicule", "capacite_kg", "disponible")


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ("raison_sociale", "matricule_fiscal", "type_entreprise", "gerant", "created_at")
    list_filter = ("type_entreprise",)
    search_fields = ("raison_sociale", "matricule_fiscal", "gerant__username")
    ordering = ("raison_sociale",)
    date_hierarchy = "created_at"
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("gerant",)
    fieldsets = (
        ("Identite", {"fields": ("raison_sociale", "matricule_fiscal", "type_entreprise")}),
        ("Coordonnees", {"fields": ("adresse", "gerant")}),
        ("Suivi", {"fields": ("created_at", "updated_at")}),
    )
    inlines = [VehiculeInline]
