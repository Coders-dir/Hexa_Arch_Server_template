from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # During type checking, use a simple base so mypy doesn't try to interpret
    # pydantic's runtime-produced BaseSettings object which can confuse the type
    # checker. At runtime we import the real BaseSettings below.
    BaseSettings = object
    from pydantic import AnyUrl
else:
    from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: AnyUrl | None
    jwt_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
