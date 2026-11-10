from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Vehicule


def liste_vehicules(request):
    vehicules = Vehicule.objects.select_related("entreprise").order_by("immatriculation")
    return render(request, "vehicules/liste.html", {"vehicules": vehicules})


def detail_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule.objects.select_related("entreprise"), pk=pk)
    offres = (
        vehicule.offres
        .select_related("expedition")
        .order_by("-date_proposition")
    )
    return render(request, "vehicules/detail.html", {"vehicule": vehicule, "offres": offres})


@require_http_methods(["GET", "POST"])
def supprimer_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == "POST":
        try:
            vehicule.delete()
        except ProtectedError:
            # Offre.vehicule est en on_delete=PROTECT
            messages.error(
                request,
                f"Impossible de supprimer {vehicule.immatriculation} : il est utilise dans des offres.",
            )
            return redirect("vehicules:detail", pk=pk)
        messages.success(request, f"Vehicule {vehicule.immatriculation} supprime.")
        return redirect("vehicules:liste")
    return render(request, "vehicules/confirmer_suppression.html", {"vehicule": vehicule})
