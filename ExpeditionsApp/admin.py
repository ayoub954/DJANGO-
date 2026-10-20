from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html

from OffresApp.models import Offre

from .models import Expedition

COULEURS_STATUT = {
    "publiee": "#2563eb",
    "attribuee": "#7c3aed",
    "en_cours": "#d97706",
    "livree": "#16a34a",
    "annulee": "#6b7280",
}


class EnRetardFilter(admin.SimpleListFilter):
    title = "en retard"
    parameter_name = "en_retard"

    def lookups(self, request, model_admin):
        return [("oui", "Oui"), ("non", "Non")]

    def queryset(self, request, queryset):
        if self.value() == "oui":
            return queryset.filter(statut="publiee", date_souhaitee__lt=timezone.now().date())
        if self.value() == "non":
            return queryset.exclude(statut="publiee", date_souhaitee__lt=timezone.now().date())
        return queryset


class OffreInline(admin.TabularInline):
    model = Offre
    extra = 0
    can_delete = False
    fields = ("transporteur", "vehicule", "prix", "delai_jours", "statut", "date_proposition")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "entreprise", "ville_depart", "ville_arrivee",
        "poids_kg", "statut", "statut_badge", "date_souhaitee",
    )
    list_filter = ("statut", "ville_depart", EnRetardFilter)
    search_fields = ("reference", "ville_depart", "ville_arrivee", "entreprise__raison_sociale")
    list_editable = ("statut",)
    ordering = ("-created_at",)
    date_hierarchy = "date_souhaitee"
    list_per_page = 25
    readonly_fields = ("reference", "created_at", "updated_at")
    autocomplete_fields = ("entreprise",)
    fieldsets = (
        ("Identification", {"fields": ("reference", "entreprise", "statut")}),
        ("Trajet et marchandise", {"fields": ("ville_depart", "ville_arrivee", "poids_kg", "date_souhaitee", "description")}),
        ("Suivi", {"fields": ("created_at", "updated_at")}),
    )
    inlines = [OffreInline]
    actions = ["cloturer_expeditions"]

    @admin.display(description="Statut (badge)", ordering="statut")
    def statut_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;">{}</span>',
            COULEURS_STATUT.get(obj.statut, "#6b7280"),
            obj.get_statut_display(),
        )

    @admin.action(description="Cloturer les expeditions selectionnees")
    def cloturer_expeditions(self, request, queryset):
        cloturees, erreurs = 0, 0
        ignorees = queryset.exclude(statut="en_cours").count()
        for expedition in queryset.filter(statut="en_cours"):
            expedition.statut = "livree"
            try:
                expedition.full_clean()
                expedition.save()
                cloturees += 1
            except ValidationError:
                erreurs += 1
        self.message_user(request, f"{cloturees} expedition(s) cloturee(s), {ignorees} ignoree(s) (pas en_cours).")
        if erreurs:
            self.message_user(request, f"{erreurs} expedition(s) refusee(s) par les regles metier.", messages.ERROR)
