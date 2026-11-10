from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Expedition


def home(request):
    return render(request, "expeditions/home.html")


def welcome(request, name):
    return HttpResponse(f"Bienvenue {name} !")


def liste_expeditions(request):
    expeditions = (
        Expedition.objects
        .filter(statut="publiee")
        .select_related("entreprise")
        .order_by("-created_at")
    )
    return render(request, "expeditions/liste.html", {"expeditions": expeditions})


def detail_expedition(request, reference):
    expedition = get_object_or_404(
        Expedition.objects.select_related("entreprise"), reference=reference
    )
    offres = (
        expedition.offres
        .select_related("transporteur", "vehicule")
        .order_by("-date_proposition")
    )
    return render(
        request,
        "expeditions/detail.html",
        {"expedition": expedition, "offres": offres},
    )


@require_http_methods(["GET", "POST"])
def supprimer_expedition(request, reference):
    """GET : page de confirmation. POST : suppression effective.
    Une suppression ne doit jamais etre declenchee par un simple GET (lien, robot, prefetch)."""
    expedition = get_object_or_404(Expedition, reference=reference)
    if request.method == "POST":
        expedition.delete()
        messages.success(request, f"Expedition {reference} supprimee.")
        return redirect("expeditions:liste")
    return render(request, "expeditions/confirmer_suppression.html", {"expedition": expedition})
