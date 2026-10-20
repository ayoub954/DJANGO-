from django.contrib import admin
from django.utils.html import format_html

from .models import Offre

COULEURS_STATUT = {
    "proposee": "#2563eb",
    "acceptee": "#16a34a",
    "refusee": "#dc2626",
    "retiree": "#6b7280",
}


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = (
        "expedition", "transporteur", "vehicule", "prix",
        "delai_jours", "statut", "statut_badge", "date_proposition",
    )
    list_filter = ("statut", "date_proposition")
    search_fields = ("expedition__reference", "transporteur__raison_sociale", "vehicule__immatriculation")
    list_editable = ("statut",)
    ordering = ("-created_at",)
    date_hierarchy = "date_proposition"
    list_per_page = 25
    readonly_fields = ("date_proposition", "created_at", "updated_at")
    autocomplete_fields = ("expedition", "transporteur", "vehicule")
    fieldsets = (
        ("Parties", {"fields": ("expedition", "transporteur", "vehicule")}),
        ("Conditions", {"fields": ("prix", "delai_jours")}),
        ("Suivi", {"fields": ("statut", "date_proposition", "created_at", "updated_at")}),
    )

    @admin.display(description="Statut (badge)", ordering="statut")
    def statut_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;">{}</span>',
            COULEURS_STATUT.get(obj.statut, "#6b7280"),
            obj.get_statut_display(),
        )
