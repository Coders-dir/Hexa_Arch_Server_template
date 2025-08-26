import os
from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.app.adapters.inbound.http.api import router as api_router, init_app
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Control docs exposure: enable only in dev/local or when ALLOW_PUBLIC_DOCS=1
ENV = os.getenv("ENV", "dev").lower()
ALLOW_PUBLIC_DOCS = os.getenv("ALLOW_PUBLIC_DOCS", "0") == "1"
public_docs = ALLOW_PUBLIC_DOCS or ENV in ("dev", "local", "test")

if public_docs:
    app = FastAPI(title="Hexa Monolith Template", docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")
else:
    # Do not expose OpenAPI schema or docs in production by default
    app = FastAPI(title="Hexa Monolith Template", docs_url=None, redoc_url=None, openapi_url=None)

app.include_router(api_router, prefix="/api")

# initialize app (middleware, quota manager)
init_app(app)


# Serve a small static Admin UI (prototype) at /admin-ui
# Static files are expected in <project_root>/static/admin-ui
static_dir = Path(__file__).resolve().parents[3] / "static" / "admin-ui"
if static_dir.exists():
    # mount JS/CSS under /admin-ui/static/
    app.mount("/admin-ui/static", StaticFiles(directory=str(static_dir)), name="admin-static")


@app.get("/admin-ui", include_in_schema=False)
async def admin_ui_index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"error": "admin UI not available"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
