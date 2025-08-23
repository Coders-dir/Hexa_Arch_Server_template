
from fastapi import APIRouter
from src.app.adapters.inbound.http.controllers.user_controller import router as user_router

# The `main.py` mounts this router at prefix "/api", so keep sub-routers unprefixed
router = APIRouter()
router.include_router(user_router)
