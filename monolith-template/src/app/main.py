from fastapi import FastAPI
from src.app.adapters.inbound.http.api import router as api_router

app = FastAPI(title="Hexa Monolith Template")
app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}
