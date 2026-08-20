"""Punto de entrada de la API de LeagueFlow."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.core.config import get_settings
from src.core.errors import registrar_manejadores
from src.leagues.router import router as leagues_router
from src.matches.router import router as matches_router
from src.players.router import router as players_router
from src.statistics.router import router as standings_router
from src.teams.router import router as teams_router

settings = get_settings()

app = FastAPI(
    title="LeagueFlow API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS restringido a una lista explícita — NUNCA "*" (constitución).
# allow_credentials es obligatorio para que la cookie de sesión cross-domain
# viaje entre Vercel y Railway (research.md §4, tasks T038).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origenes_permitidos,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

registrar_manejadores(app)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(leagues_router, prefix="/api/v1")
app.include_router(teams_router, prefix="/api/v1")
app.include_router(players_router, prefix="/api/v1")
app.include_router(matches_router, prefix="/api/v1")
app.include_router(standings_router, prefix="/api/v1")


@app.get("/api/health", tags=["infra"])
async def health() -> dict[str, str]:
    """Sonda de salud para Railway y para el smoke test post-deploy."""
    return {"status": "ok"}
