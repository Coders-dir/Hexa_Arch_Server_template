# Quickstart Quant — Monolith Template (Node)

Ce document explique en une page comment un quant démarre avec le template, installe l’environnement, récupère un snapshot et publie un endpoint.

1) Cloner le template

```bash
git clone <repo>
cd monolith-template
```

2) Démarrer les services de dev

```bash
docker-compose -f docker-compose.test.yml up -d
```

3) Installer les dépendances

```bash
poetry install
```

4) Récupérer un snapshot depuis data-truth

Utilisez l’endpoint fourni par data-truth pour télécharger le snapshot et placez-le dans `data/snapshots/`.

5) Lancer un backtest minimal

```bash
poetry run python -m src.app.tools.run_backtest --snapshot data/snapshots/2025-08-24.json
```

6) Exposer un endpoint de prédiction

Créez un routeur dans `src/app/adapters/inbound/http/` et utilisez le module `src/app/services` pour appeler votre core.

7) Créer une clé API pour accès externe

Utilisez l’admin UI (ou l’endpoint `/admin/api-keys`) pour créer une clé. La valeur brute est affichée une fois.

8) Tests rapides

```bash
PYTHONPATH="$PWD" poetry run pytest tests/test_user_service.py -q
```

Voir `docs/RATE_LIMIT_POLICY.md` et `specs/dispatcher.md` pour l’usage responsable des quotas.
