import os
import pytz
from typing import List, Optional
from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    SERVER_NAME: str = os.environ.get("SERVER_NAME", "Hewo Events")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    ROOT_PATH: str = os.environ.get("ROOT_PATH", "/api")

    ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost",
    ]

    DATABASE_SERVER: str = os.environ.get("DB_HOST", "db")
    DATABASE_USER: str = os.environ.get("DB_USER")
    DATABASE_PASSWORD: str = os.environ.get("DB_PASS")
    DATABASE_NAME: str = os.environ.get("DB_NAME")
    TIME_ZONE: pytz.timezone = pytz.timezone(
        os.environ.get("TIMEZONE", os.environ.get("TZ", "UTC"))
    )
    OIDC: bool = os.environ.get("ENABLE_OIDC", True)
    OIDC_SERVER_METADATA_URL: Optional[AnyHttpUrl] = os.environ.get(
        "OIDC_SERVER_METADATA_URL"
    )
    OIDC_SCOPE: List[str] = (
        os.environ.get("OIDC_SCOPE", ["openid", "email", "profile"]),
    )
    OIDC_CLIENT_ID: Optional[str] = os.environ.get("OIDC_CLIENT_ID")
    OIDC_CLIENT_SECRET: Optional[str] = os.environ.get("OIDC_CLIENT_SECRET")

    VERSION: str = os.environ.get("VERSION", "UNKNOWN")
    BUILD: str = os.environ.get("BUILD", "UNKNOWN")

    class Config:
        case_sensitive = True


settings = Settings()
