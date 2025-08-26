# Politique de Rate Limiting et Dispatcher

Ce document décrit la politique de rate limiting, quotas et le design du dispatcher pour le monolith-template (Node).

Voir `specs/dispatcher.md` pour un diagramme et le détail d'implémentation.

Principes
- Multi-niveau : Global Node, API key, endpoint, provider.
- Algorithme : Token Bucket + Sliding Window + Circuit Breaker.
- Coût par requête : chaque endpoint a un coût configuré.
- Modes : interactive (sync) et batch (async).

Presets par défaut (dev)
- Global Node : 200 req/min
- Per key : 60 req/min
- Per endpoint : 30 req/min

Batch windows
- Doivent être demandés explicitement (admin flag) et planifiés hors-peak.

Mesures et observabilité
- Exposer métriques : `rate_limit.hits`, `dispatcher.queue.depth`, `quota.consumed`.
- Logs : évènements d'audit pour chaque dépassement, rejet ou requeue.

Runbook
- Comment réduire la charge, révoquer clefs, débloquer circuit breakers : voir `specs/dispatcher.md`.
