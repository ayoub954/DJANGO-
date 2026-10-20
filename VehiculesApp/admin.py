from django.contrib import admin

from .models import Vehicule


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ("immatriculation", "type_vehicule", "capacite_kg", "disponible", "entreprise", "created_at")
    list_filter = ("type_vehicule", "disponible")
    search_fields = ("immatriculation", "entreprise__raison_sociale")
    list_editable = ("disponible",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("entreprise",)
    fieldsets = (
        ("Caracteristiques", {"fields": ("immatriculation", "type_vehicule", "capacite_kg")}),
        ("Exploitation", {"fields": ("entreprise", "disponible")}),
        ("Suivi", {"fields": ("created_at", "updated_at")}),
    )
