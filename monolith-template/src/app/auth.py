import os
from datetime import datetime, timedelta
from typing import Any, Dict

import jwt
from fastapi import HTTPException, Request, status

SECRET = os.getenv("JWT_SECRET", "dev-secret")
ALGORITHM = "HS256"


def create_access_token(subject: str = "svc", role: str = "admin", minutes: int = 60) -> str:
    now = datetime.utcnow()
    payload: Dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def get_current_admin(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")
    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    role = payload.get("role")
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return payload
