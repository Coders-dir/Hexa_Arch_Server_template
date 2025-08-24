from fastapi import FastAPI, Response
from src.app.adapters.inbound.http.api import router as api_router, init_app
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Hexa Monolith Template")
app.include_router(api_router, prefix="/api")

# initialize app (middleware, quota manager)
init_app(app)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
