from django.shortcuts import get_object_or_404, render

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
