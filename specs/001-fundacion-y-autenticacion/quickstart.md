# Quickstart: Fundación técnica y autenticación

Valida esta spec end-to-end. Detalles de entidades en `data-model.md`,
endpoints en `contracts/auth.openapi.yaml` y `contracts/conventions.md`.

## Prerrequisitos

- Python 3.12, Node 20+, PostgreSQL 16 corriendo localmente (o vía Docker).
- `backend/.env` con `DATABASE_URL`, `ALLOWED_ORIGINS`, `SESSION_SECRET`
  (ver `.env.example` — nunca commitear el `.env` real, Principio VI).

## Setup

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head        # crea el esquema, incluida la tabla User/Session
python -m scripts.seed_admin # crea el usuario organizador semilla

# Frontend
cd ../frontend
npm install
```

## Ejecutar

```bash
# Terminal 1
cd backend && uvicorn src.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

## Escenarios de validación (mapean a los Acceptance Scenarios de `spec.md`)

1. **Login válido** (Acceptance Scenario 1): `POST /api/v1/auth/login` con las
   credenciales del organizador semilla → `200`, cookie `lf_session` presente
   en la respuesta, `user.role == "organizador"`.
2. **Login inválido** (Acceptance Scenario 2): `POST /api/v1/auth/login` con
   password incorrecta → `401`, `error.message` genérico (no distingue
   "usuario no existe" de "password incorrecta").
3. **Consulta sin sesión** (Acceptance Scenario 3): `GET /api/v1/auth/me` sin
   cookie → `200` con `user: null` (una ruta de consulta nunca exige sesión).
4. **Escritura sin sesión** (Acceptance Scenario 4): `POST /api/v1/users` sin
   cookie → `401`.
5. **Rol insuficiente** (Acceptance Scenario 5): login como `operador`, luego
   `POST /api/v1/users` → `403` (crear usuarios es solo de organizador).
6. **Logout revoca** (Acceptance Scenario 6): `POST /api/v1/auth/logout`,
   luego repetir cualquier escritura con la misma cookie → `401`.
7. **Atribución de autoría** (Acceptance Scenario 7): crear un usuario como
   organizador, verificar en la fila creada que `created_by` corresponde al
   `user.id` de la sesión que hizo la llamada.

## Pruebas automatizadas de referencia

```bash
cd backend && pytest tests/integration/test_auth.py -v
cd frontend && npx vitest run src/features/auth
```

Estos dos comandos son el gate mínimo de esta spec antes de abrir PR
(Quality Gate 2/3 de la constitución).
