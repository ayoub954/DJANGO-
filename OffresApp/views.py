from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Offre


def liste_offres(request):
    offres = (
        Offre.objects
        .select_related("expedition", "transporteur", "vehicule")
        .order_by("-date_proposition")
    )
    return render(request, "offres/liste.html", {"offres": offres})


def detail_offre(request, pk):
    offre = get_object_or_404(
        Offre.objects.select_related("expedition", "transporteur", "vehicule"), pk=pk
    )
    return render(request, "offres/detail.html", {"offre": offre})


@require_http_methods(["GET", "POST"])
def supprimer_offre(request, pk):
    offre = get_object_or_404(Offre.objects.select_related("expedition"), pk=pk)
    if request.method == "POST":
        reference = offre.expedition.reference
        offre.delete()
        messages.success(request, f"Offre sur {reference} supprimee.")
        return redirect("offres:liste")
    return render(request, "offres/confirmer_suppression.html", {"offre": offre})
