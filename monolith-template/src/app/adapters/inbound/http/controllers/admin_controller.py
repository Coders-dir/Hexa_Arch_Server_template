from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
import json
import secrets
import hashlib
import os
from typing import List
from datetime import datetime, timezone
from uuid import uuid4

router = APIRouter()

# simple in-memory store (replace by DB-backed repo later)
_STORE = {}
_DB_REPO = None

PEPPER = os.getenv("API_KEY_PEPPER", "dev-pepper")


class CreateKeyRequest(BaseModel):
    name: str
    owner: str | None = None
    scopes: List[str] | None = None


class KeyInfo(BaseModel):
    kid: str
    name: str | None
    owner: str | None
    scopes: List[str] | None
    created_at: datetime
    revoked_at: datetime | None = None


def _hash_token(token: str) -> str:
    # PBKDF2-HMAC-SHA256
    return hashlib.pbkdf2_hmac("sha256", token.encode(), PEPPER.encode(), 100000).hex()


@router.post("/admin/api-keys", response_model=dict)
async def create_key(req: CreateKeyRequest, request: Request, background_tasks: BackgroundTasks):
    kid = str(uuid4())
    token = secrets.token_urlsafe(32)
    hashed = _hash_token(token)
    # If DB repo is available, schedule a background write through the app-level repo
    if os.getenv("USE_DB_KEYS") == "1":
        repo = getattr(request.app.state, "api_key_repo", None)

        async def _write():
            if repo:
                await repo.create_key(kid, req.name, req.owner, req.scopes or [], hashed)

        # Under ASGI the background task will be awaited; under TestClient it will also run
        background_tasks.add_task(_write)
    else:
        _STORE[kid] = {
            "kid": kid,
            "name": req.name,
            "owner": req.owner,
            "scopes": req.scopes or [],
            "hashed_token": hashed,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "revoked_at": None,
        }
    # Return the raw token once
    return {"kid": kid, "token": token}


@router.get("/admin/api-keys", response_model=List[KeyInfo])
async def list_keys(request: Request):
    if os.getenv("USE_DB_KEYS") == "1":
        repo = getattr(request.app.state, "api_key_repo", None)

        if repo:
            rows = await repo.list_keys()
        else:
            # fallback to direct repo
            from src.app.adapters.outbound.api_key_repo import ApiKeyRepo

            tmp = ApiKeyRepo()
            rows = await tmp.list_keys()
        # convert to KeyInfo list
        out = []
        for r in rows:
            scopes_val = r.get("scopes", [])
            if isinstance(scopes_val, str):
                try:
                    scopes_val = json.loads(scopes_val)
                except Exception:
                    scopes_val = []

            out.append(
                KeyInfo(
                    kid=r["kid"],
                    name=r.get("name"),
                    owner=r.get("owner"),
                    scopes=scopes_val,
                    created_at=r.get("created_at"),
                    revoked_at=r.get("revoked_at"),
                )
            )
        return out
    return [_to_keyinfo(v) for v in _STORE.values()]


@router.post("/admin/api-keys/{kid}/revoke", response_model=dict)
async def revoke_key(kid: str, request: Request, background_tasks: BackgroundTasks):
    if os.getenv("USE_DB_KEYS") == "1":
        repo = getattr(request.app.state, "api_key_repo", None)

        async def _revoke():
            if repo:
                await repo.revoke_key(kid)
            else:
                from src.app.adapters.outbound.api_key_repo import ApiKeyRepo

                tmp = ApiKeyRepo()
                await tmp.revoke_key(kid)

        background_tasks.add_task(_revoke)
        return {"status": "revoked", "kid": kid}

    if kid not in _STORE:
        raise HTTPException(status_code=404, detail="key not found")
    _STORE[kid]["revoked_at"] = datetime.now(timezone.utc).isoformat()
    return {"status": "revoked", "kid": kid}


def _to_keyinfo(rec: dict) -> KeyInfo:
    return KeyInfo(
        kid=rec["kid"],
        name=rec.get("name"),
        owner=rec.get("owner"),
        scopes=rec.get("scopes", []),
        created_at=datetime.fromisoformat(rec["created_at"]),
        revoked_at=(datetime.fromisoformat(rec["revoked_at"]) if rec.get("revoked_at") else None),
    )


@router.get("/admin/metrics", response_model=dict)
async def admin_metrics(request: Request):
    # try to return repo metrics if available
    repo = getattr(request.app.state, "api_key_repo", None)
    if repo:
        try:
            # repo.get_metrics is a small sync helper
            return repo.get_metrics() if hasattr(repo, 'get_metrics') else {}
        except Exception:
            return {}
    # fallback to module-level metrics
    try:
        from src.app.adapters.outbound.api_key_repo import get_metrics

        return get_metrics()
    except Exception:
        return {}
