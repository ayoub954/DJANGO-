# AI_LOG — Workshop Models TransConnect (Part 1)

## Entrée 2026-10-05 — Modèles des 5 entités
- **Outil IA utilisé :** Claude (Anthropic)
- **Prompt :** « À partir du cahier des charges et du diagramme de classe TransConnect, génère les models.py des applications EntreprisesApp, VehiculesApp, ExpeditionsApp et OffresApp. »
- **Sortie obtenue (résumé) :** Modèles Utilisateur (hérite d'AbstractUser), Entreprise, Vehicule, Expedition, Offre avec choix, relations et champs created_at / updated_at.
- **Écarts identifiés vs cahier des charges :**
  - Vérifier que `user_id` remplace bien l'`id` d'AbstractUser (`primary_key=True`, `max_length=8`).
  - Vérifier que `user_id` est généré aussi pour `createsuperuser` (sinon PK vide).
- **Correction apportée et justification :**
  - `UtilisateurManager` personnalisé (hérite de `UserManager`) qui génère un `user_id` unique de 8 caractères (`U` + 7 chiffres) dans `create_user` et `create_superuser` ; le superuser reçoit automatiquement `role='admin'`.
  - `AUTH_USER_MODEL = 'EntreprisesApp.Utilisateur'` déclaré dans settings.py **avant** la première migration (le changer après coup casse les migrations).

## Entrée 2026-10-05 — Bug Hunt entité Offre (section IV)
- **Outil IA utilisé :** Claude (Anthropic)
- **Prompt :** « Identifie les anomalies du modèle Offre fourni par rapport au cahier des charges. »
- **Sortie obtenue (résumé) :** 4 anomalies identifiées + 1 remarque.
- **Écarts identifiés vs cahier des charges :**

| # | Code fourni | Problème | Correction |
|---|---|---|---|
| 1 | `prix = CharField(max_length=10)` | Un prix stocké en texte : pas de tri, pas de calcul, accepte « abc ». Le CDC impose DecimalField. | `DecimalField(max_digits=10, decimal_places=2)` (Decimal et non Float pour éviter les erreurs d'arrondi sur des montants) |
| 2 | `delai_jours = IntegerField()` | Accepte un délai négatif. Le CDC impose PositiveIntegerField. | `PositiveIntegerField()` |
| 3 | `date_proposition = DateField(auto_now=True)` | `auto_now` met à jour la date à **chaque** save (ex. lors de l'acceptation) : on perd la date réelle de proposition. | `DateField(auto_now_add=True)` |
| 4 | `save()` qui ne fait qu'appeler `super().save()` | Ne déclenche pas les effets en cascade exigés lors de l'acceptation. | Si `statut == 'acceptee'` : expédition → `attribuee`, autres offres `proposee` → `refusee`, véhicule → `disponible=False`, le tout dans `transaction.atomic()` |

- **Remarque complémentaire :** `vehicule` avait `null=True`, or le CDC dit qu'une offre est proposée « en l'associant à l'un de ses véhicules » → champ rendu obligatoire, avec `on_delete=PROTECT` (on ne supprime pas un véhicule qui a des offres). `STATUT_CHOICES` n'était pas défini → remplacé par `models.TextChoices`. Ajout de `created_at` / `updated_at` (obligatoires pour tous les modèles).
- **Correction apportée et justification :** voir `OffresApp/models.py`. Test réalisé : création de 2 offres, acceptation de la 1ʳᵉ → expédition `attribuee`, 2ᵉ offre `refusee`, véhicule indisponible.

## Commits correspondants
```
AI: génération initiale des modèles (Utilisateur, Entreprise, Vehicule, Expedition, Offre)
Review: Offre.prix en DecimalField (AI_LOG Bug Hunt #1)
Review: Offre.delai_jours en PositiveIntegerField (AI_LOG Bug Hunt #2)
Review: Offre.date_proposition auto_now_add (AI_LOG Bug Hunt #3)
Review: effets en cascade dans Offre.save() (AI_LOG Bug Hunt #4)
Feat: AUTH_USER_MODEL + nom de base de données
Docs: ajout AI_LOG.md
```
