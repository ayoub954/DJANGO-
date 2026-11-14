from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import OffreForm
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


def ajouter_offre(request):
    form = OffreForm(request.POST or None)
    if form.is_valid():
        offre = form.save()
        messages.success(request, "Offre ajoutee.")
        return redirect("offres:detail", pk=offre.pk)
    return render(request, "offres/form.html", {"form": form})


def modifier_offre(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    form = OffreForm(request.POST or None, instance=offre)
    if form.is_valid():
        form.save()
        messages.success(request, "Offre modifiee.")
        return redirect("offres:detail", pk=pk)
    return render(request, "offres/form.html", {"form": form, "offre": offre})
