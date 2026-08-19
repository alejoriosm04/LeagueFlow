# LeagueFlow — Backend

API FastAPI. Decisiones técnicas en
`specs/001-fundacion-y-autenticacion/research.md`; endpoints en
`specs/001-fundacion-y-autenticacion/contracts/`.

## Requisitos

- [uv](https://docs.astral.sh/uv/) (gestiona Python 3.12 por ti; no hace falta instalarlo aparte)
- Docker, para PostgreSQL local

## Puesta en marcha

```bash
# 1. Base de datos local
# Sin contraseña a propósito: contenedor local, accesible solo desde tu máquina.
# Así no queda ninguna credencial literal en el repo (Principio VI).
docker run -d --name leagueflow-db \
  -e POSTGRES_USER=leagueflow -e POSTGRES_DB=leagueflow \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -p 5432:5432 postgres:16

# 2. Entorno y dependencias
uv venv --python 3.12
uv pip install -e ".[dev]"

# 3. Configuración — copia y rellena; NUNCA commitees .env
cp .env.example .env

# 4. Esquema
.venv/bin/alembic upgrade head

# 5. Organizador inicial (lee SEED_ADMIN_* de .env; falla si faltan)
.venv/bin/python -m scripts.seed_admin

# 6. Servidor
.venv/bin/uvicorn src.main:app --reload
```

API en `http://localhost:8000`, documentación interactiva en `/api/docs`.

## Pruebas

```bash
docker exec leagueflow-db psql -U leagueflow -d postgres -c "CREATE DATABASE leagueflow_test;"
DATABASE_URL="postgresql+asyncpg://leagueflow@localhost:5432/leagueflow_test" \
  .venv/bin/pytest tests/ -v
```

## Calidad

```bash
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format src tests scripts
```

## Estructura

Un módulo por dominio (Principio VIII de la constitución): `auth/` está
implementado; `leagues/`, `teams/`, `players/`, `matches/` y `statistics/`
los pueblan las specs `002` en adelante. `core/` tiene la configuración, la
sesión de BD, el envelope de error y el CORS que todos comparten.
