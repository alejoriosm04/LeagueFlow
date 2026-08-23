"""Configuración de la aplicación, leída solo de variables de entorno.

Principio VI de la constitución: ningún secreto vive en el código. Todo valor
sensible entra por entorno y se documenta vacío en `.env.example`.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    allowed_origins: str = Field(alias="ALLOWED_ORIGINS")
    cookie_secure: bool = Field(default=True, alias="COOKIE_SECURE")

    # Ventana de inactividad de la sesión — research.md §10.
    session_ttl_seconds: int = Field(default=8 * 60 * 60, alias="SESSION_TTL_SECONDS")

    # Bloqueo del login tras intentos fallidos — specs/017 research.md §9.
    # No son secretos, pero van por entorno como toda la configuración (FR-007).
    login_max_failed_attempts: int = Field(default=5, alias="LOGIN_MAX_FAILED_ATTEMPTS")
    login_lockout_seconds: int = Field(default=15 * 60, alias="LOGIN_LOCKOUT_SECONDS")

    # Organizador semilla. Vacíos por defecto: el script de semilla falla si no
    # se definen, en vez de inventar una credencial (research.md §10).
    seed_admin_username: str = Field(default="", alias="SEED_ADMIN_USERNAME")
    seed_admin_password: str = Field(default="", alias="SEED_ADMIN_PASSWORD")

    @field_validator("database_url")
    @classmethod
    def normalizar_driver(cls, v: str) -> str:
        """Railway inyecta `postgresql://`; SQLAlchemy async necesita asyncpg."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def origenes_permitidos(self) -> list[str]:
        """Lista explícita de orígenes. NUNCA '*' (Estándares de Seguridad)."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
