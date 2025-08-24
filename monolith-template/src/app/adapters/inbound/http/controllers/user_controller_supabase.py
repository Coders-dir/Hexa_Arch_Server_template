from fastapi import APIRouter, Depends
from typing import Any

from src.app.services.user_service import UserService
from src.app.adapters.outbound.supabase_client import SupabaseClient

router = APIRouter()


def get_supabase_client() -> SupabaseClient:
    return SupabaseClient()


@router.post("/users")
async def create_user(payload: dict[str, Any], client: SupabaseClient = Depends(get_supabase_client)):
    # Example: store user in supabase table `users`
    created = await client.insert("users", payload)
    return created
