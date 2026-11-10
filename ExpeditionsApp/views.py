from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView

from .models import Expedition


def home(request):
    return render(request, "expeditions/home.html")


def welcome(request, name):
    return HttpResponse(f"Bienvenue {name} !")


def list_expeditions(request):
    expeditions = (
        Expedition.objects
        .filter(statut="publiee")
        .select_related("entreprise")
        .order_by("-created_at")
    )
    return render(request, "expeditions/liste.html", {"expeditions": expeditions})


def expedition_detail(request, pk):
    expedition = get_object_or_404(
        Expedition.objects.select_related("entreprise"), pk=pk
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
def expedition_delete(request, pk):
    """GET : page de confirmation. POST : suppression effective.
    Une suppression ne doit jamais etre declenchee par un simple GET (lien, robot, prefetch)."""
    expedition = get_object_or_404(Expedition, pk=pk)
    if request.method == "POST":
        reference = expedition.reference
        expedition.delete()
        messages.success(request, f"Expedition {reference} supprimee.")
        return redirect("list")
    return render(request, "expeditions/confirmer_suppression.html", {"expedition": expedition})


class Expedition_list(ListView):
    model = Expedition
    template_name = "expeditions/liste.html"
    context_object_name = "expeditions"

    def get_queryset(self):
        return (
            Expedition.objects
            .filter(statut="publiee")
            .select_related("entreprise")
            .order_by("-created_at")
        )


class ExpeditionDetailView(DetailView):
    model = Expedition
    template_name = "expeditions/detail.html"
    context_object_name = "expedition"

    def get_queryset(self):
        return Expedition.objects.select_related("entreprise")


class ExpeditionDeleteView(DeleteView):
    
    model = Expedition
    template_name = "expeditions/confirmer_suppression.html"
    context_object_name = "expedition"
    success_url = reverse_lazy("expedition_list")

    def form_valid(self, form):
        reference = self.object.reference
        response = super().form_valid(form)
        messages.success(self.request, f"Expedition {reference} supprimee.")
        return response
