from .db.mongo_user_repo import MongoUserRepository

# Backwards-compatible alias used by older tests and imports
MongoUserRepo = MongoUserRepository

__all__ = ["MongoUserRepository", "MongoUserRepo"]
