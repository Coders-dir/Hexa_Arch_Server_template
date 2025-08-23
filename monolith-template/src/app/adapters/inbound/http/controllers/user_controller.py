from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class CreateUserRequest(BaseModel):
    email: str
    name: str | None = None

@router.post("/", status_code=201)
async def create_user(req: CreateUserRequest):
    # Stub: call application use-case
    if not req.email:
        raise HTTPException(status_code=400, detail="email required")
    return {"id": "uuid-sample", "email": req.email, "name": req.name}

@router.get("/{user_id}")
async def get_user(user_id: str):
    # Stub: call application use-case
    return {"id": user_id, "email": "user@example.com", "name": "Example"}
