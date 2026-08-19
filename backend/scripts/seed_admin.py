"""Crea el organizador semilla a partir de variables de entorno.

Principio VI: no existe credencial por defecto. Si SEED_ADMIN_USERNAME o
SEED_ADMIN_PASSWORD faltan, el script falla en vez de inventar un admin/admin
que acabaría en producción (research.md §10).

Uso:  python -m scripts.seed_admin
"""

import asyncio
import sys

from sqlalchemy import func, select
from src.auth.models import Usuario
from src.auth.security import LONGITUD_MINIMA, hashear_password
from src.core.config import get_settings
from src.core.db import SessionLocal


async def main() -> int:
    # Vía Settings, no os.getenv: así se respeta el archivo .env igual que en
    # el resto de la app (pydantic-settings lo carga; os.getenv no).
    settings = get_settings()
    username = settings.seed_admin_username.strip()
    password = settings.seed_admin_password

    if not username or not password:
        print(
            "ERROR: define SEED_ADMIN_USERNAME y SEED_ADMIN_PASSWORD en el entorno.\n"
            "       No hay credencial por defecto, a propósito.",
            file=sys.stderr,
        )
        return 1

    if len(password) < LONGITUD_MINIMA:
        print(
            f"ERROR: la contraseña debe tener al menos {LONGITUD_MINIMA} caracteres.",
            file=sys.stderr,
        )
        return 1

    async with SessionLocal() as db:
        existente = await db.execute(
            select(Usuario).where(func.lower(Usuario.username) == username.lower())
        )
        if existente.scalar_one_or_none() is not None:
            print(f"El usuario '{username}' ya existe; no se hace nada.")
            return 0

        db.add(
            Usuario(
                username=username,
                password_hash=hashear_password(password),
                role="organizador",
                created_by=None,  # semilla: no la creó otro usuario
            )
        )
        await db.commit()

    print(f"Organizador semilla '{username}' creado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
