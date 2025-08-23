from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

@dataclass
class User:
    id: str
    email: str
    name: str | None
    created_at: datetime

    @staticmethod
    def create(email: str, name: str | None = None) -> "User":
        return User(id=str(uuid4()), email=email, name=name, created_at=datetime.utcnow())
