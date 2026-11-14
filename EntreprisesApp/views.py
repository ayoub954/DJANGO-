from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EntrepriseForm
from .models import Entreprise


def liste_entreprises(request):
    entreprises = Entreprise.objects.select_related("gerant").order_by("raison_sociale")
    return render(request, "entreprises/liste.html", {"entreprises": entreprises})


def detail_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise.objects.select_related("gerant"), pk=pk)
    context = {
        "entreprise": entreprise,
        "vehicules": entreprise.vehicules.order_by("immatriculation"),
        "expeditions": entreprise.expedition.order_by("-created_at"),
        "offres": entreprise.offres.select_related("expedition").order_by("-date_proposition"),
    }
    return render(request, "entreprises/detail.html", context)


def ajouter_entreprise(request):
    form = EntrepriseForm(request.POST or None)
    if form.is_valid():
        entreprise = form.save()
        messages.success(request, "Entreprise ajoutee.")
        return redirect("entreprises:detail", pk=entreprise.pk)
    return render(request, "entreprises/form.html", {"form": form})


def modifier_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise, pk=pk)
    form = EntrepriseForm(request.POST or None, instance=entreprise)
    if form.is_valid():
        form.save()
        messages.success(request, "Entreprise modifiee.")
        return redirect("entreprises:detail", pk=pk)
    return render(request, "entreprises/form.html", {"form": form, "entreprise": entreprise})


def supprimer_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise, pk=pk)
    if request.method == "POST":
        entreprise.delete()
        messages.success(request, "Entreprise supprimee.")
        return redirect("entreprises:liste")
    return render(request, "entreprises/confirmer_suppression.html", {"entreprise": entreprise})
