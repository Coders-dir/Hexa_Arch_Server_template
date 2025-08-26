Running the worker (local)

This project provides a standalone worker entrypoint at `src/app/worker.py` which consumes the Redis priority queue `dispatcher:priority_queue`.

Local run (uses the same venv as the project):

```bash
cd service-template
export PYTHONPATH=$PWD
python src/app/worker.py
```

In production, run the worker as a Deployment (`k8s/worker-deployment.yaml`) or as a separate service/process. Ensure `REDIS_URL` env var points to your Redis service and that the worker has permissions to access it.
