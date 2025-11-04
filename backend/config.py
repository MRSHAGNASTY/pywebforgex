
from __future__ import annotations
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PYWEBFORGE_KEYS: str = "admin:dev-admin,editor:dev-editor,viewer:dev-viewer"
    EgressDeny: int = 1
    CORS_ALLOW_ORIGINS: str = "http://localhost:7860,http://localhost:8080"
    IP_ALLOWLIST: str = ""
    RATE_LIMIT_RPM: int = 120
    JWT_ISSUER: Optional[str] = None
    JWT_AUDIENCE: Optional[str] = None
    JWT_JWKS_URL: Optional[str] = None
    CSRF_SECRET: str = "change-me"
    HOOK_URL: Optional[str] = None

    @property
    def origins(self) -> List[str]:
        return [o.strip() for o in self.CORS_ALLOW_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
