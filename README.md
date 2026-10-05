# TransConnect

Plateforme de mise en relation entre chargeurs et transporteurs — Workshop Python Framework for the web (ESPRIT 2026-2027).

## Applications
- **EntreprisesApp** : modèles `Utilisateur` (hérite d'`AbstractUser`) et `Entreprise`
- **VehiculesApp** : modèle `Vehicule`
- **ExpeditionsApp** : modèle `Expedition`
- **OffresApp** : modèle `Offre`

## Lancer le projet
```bash
uv sync
uv run python manage.py makemigrations EntreprisesApp VehiculesApp ExpeditionsApp OffresApp
uv run python manage.py migrate
uv run python manage.py runserver
```

Base de données : `ayoub.sqlite3`. Traçabilité IA : voir `AI_LOG.md`.
