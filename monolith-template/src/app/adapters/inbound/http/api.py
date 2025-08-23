from fastapi import APIRouter
from src.app.adapters.inbound.http.controllers import user_controller

router = APIRouter()

router.include_router(user_controller.router, prefix="/users", tags=["users"]) 
