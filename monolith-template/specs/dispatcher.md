# Spécification technique : Dispatcher et Quotas

Résumé
-------
Le dispatcher est un composant responsable de l'enforcement des quotas, de la mise en file d'attente des requêtes vers des providers externes et de la gestion du backpressure.

Composants
----------
- Ingress middleware: tagge chaque requête (api_key, endpoint, cost, provider).
- Quota manager: atomique, sur Redis. Implémentation recommandée: scripts Lua pour cohérence.
- Queueing layer: Redis streams ou listes avec priorité.
- Scheduler: worker qui pop les tâches et exécute selon quotas.
- Executor/adaptor: effectue l'appel externe et applique circuit breaker.

Flux
----
1. Requête entrante -> Ingress
2. Quota manager check -> si ok exécute, sinon push queue
3. Scheduler pop -> recheck quotas -> exécute
4. Executor -> provider -> publish result + audit

Contraintes
-----------
- Mémoire: limiter taille queue et nombre worker selon env var
- Atomicité: utiliser LUA scripts pour updates atomiques de quota
- Observabilité: tracer chaque étape et exporter métriques

Endpoints opératoires
- `/admin/dispatcher/queue` : status
- `/admin/dispatcher/metrics` : exporter métriques

See also: `docs/RATE_LIMIT_POLICY.md` and `db/ddl_api_keys.sql` for audit events.
