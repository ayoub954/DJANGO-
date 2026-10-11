from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from EntreprisesApp.models import Entreprise, Utilisateur
from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule


class ReglesMetierTests(TestCase):
    def creer_entreprise(self, nom, type_entreprise, matricule):
        gerant = Utilisateur.objects.create(
            username=nom, email=f"{nom}@gmail.com", role=type_entreprise, telephone="12345678"
        )
        return Entreprise.objects.create(
            raison_sociale=nom,
            matricule_fiscal=matricule,
            type_entreprise=type_entreprise,
            adresse="12 rue de la Republique, Tunis 1000",
            gerant=gerant,
        )

    def setUp(self):
        self.chargeur = self.creer_entreprise("chargeur1", "chargeur", "1234567AAM000")
        self.t1 = self.creer_entreprise("transp1", "transporteur", "1234568AAM000")
        self.t2 = self.creer_entreprise("transp2", "transporteur", "1234569AAM000")
        self.v1 = Vehicule.objects.create(
            immatriculation="100TU1000", type_vehicule="camion_porteur", capacite_kg=10000, entreprise=self.t1
        )
        self.v2 = Vehicule.objects.create(
            immatriculation="200TU2000", type_vehicule="camion_porteur", capacite_kg=10000, entreprise=self.t2
        )
        self.exp = Expedition.objects.create(
            ville_depart="Tunis",
            ville_arrivee="Sfax",
            poids_kg=Decimal("5000"),
            date_souhaitee=date(2026, 12, 1),
            description="Palettes",
            entreprise=self.chargeur,
        )

    def offre(self, transporteur, vehicule, **kwargs):
        return Offre.objects.create(
            prix=Decimal("500"), delai_jours=2, expedition=self.exp,
            transporteur=transporteur, vehicule=vehicule, **kwargs
        )

    def test_regle1_offre_par_transporteur_uniquement(self):
        with self.assertRaises(ValidationError):
            self.offre(self.chargeur, self.v1)

    def test_regle2_vehicule_du_meme_transporteur(self):
        with self.assertRaises(ValidationError):
            self.offre(self.t1, self.v2)

    def test_regle3_expedition_publiee(self):
        self.exp.statut = "en_cours"
        self.exp.save()
        with self.assertRaises(ValidationError):
            self.offre(self.t1, self.v1)

    def test_regle4_une_seule_offre_proposee(self):
        self.offre(self.t1, self.v1)
        with self.assertRaises(ValidationError):
            self.offre(self.t1, self.v1)

    def test_regle5_cascade_acceptation(self):
        o1 = self.offre(self.t1, self.v1)
        o2 = self.offre(self.t2, self.v2)
        o1.statut = Offre.Statut.ACCEPTEE
        o1.save()
        self.exp.refresh_from_db()
        o2.refresh_from_db()
        self.assertEqual(self.exp.statut, "attribuee")
        self.assertEqual(o2.statut, Offre.Statut.REFUSEE)

    def test_regle6_vehicule_indisponible(self):
        self.v1.disponible = False
        self.v1.save()
        with self.assertRaises(ValidationError):
            self.offre(self.t1, self.v1)

    def test_regle7_compatibilite_poids(self):
        petit = Vehicule.objects.create(
            immatriculation="300TU3000", type_vehicule="camionnette", capacite_kg=1500, entreprise=self.t1
        )
        with self.assertRaises(ValidationError):
            self.offre(self.t1, petit)

    def test_regle7_capacite_coherente_avec_type(self):
        with self.assertRaises(ValidationError):
            Vehicule.objects.create(
                immatriculation="400TU4000", type_vehicule="camionnette", capacite_kg=20000, entreprise=self.t1
            )
