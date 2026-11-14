from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import VehiculeForm
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
            messages.error(
                request,
                f"Impossible de supprimer {vehicule.immatriculation} : il est utilise dans des offres.",
            )
            return redirect("vehicules:detail", pk=pk)
        messages.success(request, f"Vehicule {vehicule.immatriculation} supprime.")
        return redirect("vehicules:liste")
    return render(request, "vehicules/confirmer_suppression.html", {"vehicule": vehicule})


def ajouter_vehicule(request):
    form = VehiculeForm(request.POST or None)
    if form.is_valid():
        vehicule = form.save()
        messages.success(request, "Vehicule ajoute.")
        return redirect("vehicules:detail", pk=vehicule.pk)
    return render(request, "vehicules/form.html", {"form": form})


def modifier_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    form = VehiculeForm(request.POST or None, instance=vehicule)
    if form.is_valid():
        form.save()
        messages.success(request, "Vehicule modifie.")
        return redirect("vehicules:detail", pk=pk)
    return render(request, "vehicules/form.html", {"form": form, "vehicule": vehicule})
