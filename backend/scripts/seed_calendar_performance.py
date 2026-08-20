"""Genera de forma idempotente 20 equipos y 190 partidos para medir SC-001."""

import asyncio
import sys
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from src.auth.models import Usuario
from src.core.config import get_settings
from src.core.db import SessionLocal
from src.leagues.models import League
from src.matches.models import Match
from src.teams.models import Team

NOMBRE_LIGA = "Calendario rendimiento"
TEMPORADA = "SC-001"


async def main() -> int:
    settings = get_settings()
    username = settings.seed_admin_username.strip()
    if not username:
        print(
            "ERROR: define SEED_ADMIN_USERNAME y ejecuta primero scripts.seed_admin.",
            file=sys.stderr,
        )
        return 1

    async with SessionLocal() as db:
        actor = await db.scalar(
            select(Usuario).where(func.lower(Usuario.username) == username.lower())
        )
        if actor is None or actor.role != "organizador" or actor.status != "active":
            print(
                "ERROR: el organizador semilla configurado no existe o no está activo.",
                file=sys.stderr,
            )
            return 1
        liga = await db.scalar(
            select(League).where(League.name == NOMBRE_LIGA, League.season == TEMPORADA)
        )
        if liga is None:
            liga = League(
                name=NOMBRE_LIGA,
                season=TEMPORADA,
                description="Escenario local de rendimiento",
                created_by=actor.id,
            )
            db.add(liga)
            await db.flush()
        equipos = list(
            (
                await db.scalars(select(Team).where(Team.league_id == liga.id).order_by(Team.name))
            ).all()
        )
        for indice in range(len(equipos), 20):
            equipo = Team(
                league_id=liga.id, name=f"Equipo rendimiento {indice + 1:02}", created_by=actor.id
            )
            db.add(equipo)
            equipos.append(equipo)
        await db.flush()
        existentes = {
            (p.home_team_id, p.away_team_id)
            for p in (await db.scalars(select(Match).where(Match.league_id == liga.id))).all()
        }
        base = datetime(2027, 1, 1, 18, tzinfo=UTC)
        indice = 0
        for local in range(20):
            for visitante in range(local + 1, 20):
                par = (equipos[local].id, equipos[visitante].id)
                if par not in existentes:
                    finalizado = indice % 2 == 0
                    db.add(
                        Match(
                            league_id=liga.id,
                            home_team_id=par[0],
                            away_team_id=par[1],
                            scheduled_at=base + timedelta(hours=indice),
                            status="finished" if finalizado else "scheduled",
                            home_score=indice % 5 if finalizado else None,
                            away_score=indice % 3 if finalizado else None,
                            created_by=actor.id,
                        )
                    )
                indice += 1
        await db.commit()
        total = await db.scalar(
            select(func.count()).select_from(Match).where(Match.league_id == liga.id)
        )
    print(f"Calendario listo: /leagues/{liga.id}/matches ({total} partidos).")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
