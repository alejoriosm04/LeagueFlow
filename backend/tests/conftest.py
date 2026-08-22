"""Fixtures compartidas: app, base de datos limpia y clientes HTTP."""

import os
import secrets
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://leagueflow@localhost:5432/leagueflow_test"
)
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:5173")
os.environ.setdefault("COOKIE_SECURE", "false")

from src.core.db import engine  # noqa: E402
from src.core.models_base import Base  # noqa: E402
from src.main import app  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def base_limpia():
    """Cada test corre contra un esquema recién creado."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # pytest-asyncio crea un event loop por test; el pool del engine queda
    # atado al loop anterior y al cerrarse produce "Event loop is closed".
    # Liberarlo aquí hace que el siguiente test abra conexiones en su loop.
    await engine.dispose()


@pytest_asyncio.fixture
async def cliente() -> AsyncClient:
    """Cliente sin sesión (visitante anónimo)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# Contraseñas de prueba generadas en tiempo de ejecución. No son secretos, pero
# el Principio VI prohíbe credenciales literales "tampoco en ejemplos, tests o
# comentarios", y generarlas evita además que un escáner las marque.
CLAVE_VALIDA = secrets.token_urlsafe(16)
CLAVE_ALTERNATIVA = secrets.token_urlsafe(16)
CLAVE_INCORRECTA = secrets.token_urlsafe(16)
CLAVE_CORTA = secrets.token_hex(2)  # 4 caracteres: por debajo del mínimo de 10
CLAVE_ORGANIZADOR_ALTERNATIVO = secrets.token_urlsafe(16)

# Los identificadores también se generan: además de no dejar ningún par
# usuario/contraseña literal, hace que dos corridas nunca colisionen.
USUARIO_ORGANIZADOR = f"org-{secrets.token_hex(4)}"
USUARIO_OPERADOR = f"ope-{secrets.token_hex(4)}"
USUARIO_INEXISTENTE = f"nadie-{secrets.token_hex(4)}"
USUARIO_NUEVO = f"nuevo-{secrets.token_hex(4)}"
USUARIO_ORGANIZADOR_ALTERNATIVO = f"org2-{secrets.token_hex(4)}"


@pytest.fixture
def credenciales_organizador() -> dict[str, str]:
    return {"username": USUARIO_ORGANIZADOR, "password": CLAVE_VALIDA}


@pytest.fixture
def credenciales_operador() -> dict[str, str]:
    return {"username": USUARIO_OPERADOR, "password": CLAVE_ALTERNATIVA}


@pytest.fixture
def credenciales_organizador_alternativo() -> dict[str, str]:
    return {
        "username": USUARIO_ORGANIZADOR_ALTERNATIVO,
        "password": CLAVE_ORGANIZADOR_ALTERNATIVO,
    }


@pytest_asyncio.fixture
async def organizador_creado(credenciales_organizador):
    """Crea el organizador semilla directamente en la BD."""
    from sqlalchemy import select
    from src.auth.models import Usuario
    from src.auth.security import hashear_password
    from src.core.db import SessionLocal

    async with SessionLocal() as s:
        u = Usuario(
            username=credenciales_organizador["username"],
            password_hash=hashear_password(credenciales_organizador["password"]),
            role="organizador",
        )
        s.add(u)
        await s.commit()
        res = await s.execute(select(Usuario).where(Usuario.username == u.username))
        return res.scalar_one()


@pytest_asyncio.fixture
async def cliente_organizador(cliente, organizador_creado, credenciales_organizador):
    """Cliente con sesión de organizador ya iniciada."""
    await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    return cliente


async def _crear_usuario_prueba(credenciales: dict[str, str], role: str):
    from sqlalchemy import select
    from src.auth.models import Usuario
    from src.auth.security import hashear_password
    from src.core.db import SessionLocal

    async with SessionLocal() as s:
        usuario = Usuario(
            username=credenciales["username"],
            password_hash=hashear_password(credenciales["password"]),
            role=role,
        )
        s.add(usuario)
        await s.commit()
        res = await s.execute(select(Usuario).where(Usuario.username == usuario.username))
        return res.scalar_one()


@pytest_asyncio.fixture
async def operador_creado(credenciales_operador):
    return await _crear_usuario_prueba(credenciales_operador, "operador")


@pytest_asyncio.fixture
async def organizador_alternativo_creado(credenciales_organizador_alternativo):
    return await _crear_usuario_prueba(credenciales_organizador_alternativo, "organizador")


@pytest_asyncio.fixture
async def cliente_operador(operador_creado, credenciales_operador):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.post("/api/v1/auth/login", json=credenciales_operador)
        yield c


@pytest_asyncio.fixture
async def cliente_organizador_alternativo(
    organizador_alternativo_creado, credenciales_organizador_alternativo
):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.post("/api/v1/auth/login", json=credenciales_organizador_alternativo)
        yield c


@pytest_asyncio.fixture
async def partido_programado(cliente_organizador):
    liga = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Liga fixture", "season": "2026"}
    )
    liga_id = liga.json()["id"]
    local = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams", json={"name": "Local fixture"}
    )
    visitante = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams", json={"name": "Visitante fixture"}
    )
    partido = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/matches",
        json={
            "home_team_id": local.json()["id"],
            "away_team_id": visitante.json()["id"],
            "scheduled_at": "2026-09-01T18:00:00Z",
        },
    )
    assert partido.status_code == 201
    return partido.json()


@pytest_asyncio.fixture
async def calendario_mixto(organizador_creado):
    """Liga con fechas/estados controlados para filtros y orden del calendario."""
    from src.core.db import SessionLocal
    from src.leagues.models import League
    from src.matches.models import Match
    from src.teams.models import Team

    async with SessionLocal() as s:
        liga = League(
            name="Liga calendario fixture",
            season="2026",
            description=None,
            created_by=organizador_creado.id,
        )
        s.add(liga)
        await s.flush()
        equipos = [
            Team(league_id=liga.id, name=f"Equipo calendario {i}", created_by=organizador_creado.id)
            for i in range(1, 5)
        ]
        s.add_all(equipos)
        await s.flush()
        base = datetime(2026, 9, 1, 18, tzinfo=UTC)
        partidos = [
            Match(
                league_id=liga.id,
                home_team_id=equipos[0].id,
                away_team_id=equipos[1].id,
                scheduled_at=base,
                status="scheduled",
                created_by=organizador_creado.id,
            ),
            Match(
                league_id=liga.id,
                home_team_id=equipos[2].id,
                away_team_id=equipos[3].id,
                scheduled_at=base + timedelta(days=1),
                status="scheduled",
                created_by=organizador_creado.id,
            ),
            Match(
                league_id=liga.id,
                home_team_id=equipos[0].id,
                away_team_id=equipos[2].id,
                scheduled_at=base - timedelta(days=2),
                status="finished",
                home_score=3,
                away_score=1,
                created_by=organizador_creado.id,
            ),
            Match(
                league_id=liga.id,
                home_team_id=equipos[1].id,
                away_team_id=equipos[3].id,
                scheduled_at=base - timedelta(days=1),
                status="finished",
                home_score=0,
                away_score=0,
                created_by=organizador_creado.id,
            ),
            Match(
                league_id=liga.id,
                home_team_id=equipos[0].id,
                away_team_id=equipos[3].id,
                scheduled_at=base,
                status="in_progress",
                created_by=organizador_creado.id,
            ),
            Match(
                league_id=liga.id,
                home_team_id=equipos[1].id,
                away_team_id=equipos[2].id,
                scheduled_at=base,
                status="cancelled",
                created_by=organizador_creado.id,
            ),
        ]
        s.add_all(partidos)
        await s.commit()
        return {"league_id": str(liga.id), "teams": equipos, "matches": partidos}


@pytest_asyncio.fixture
async def calendario_190(organizador_creado):
    """Round-robin de 20 equipos: 190 partidos persistidos para paginación."""
    from src.core.db import SessionLocal
    from src.leagues.models import League
    from src.matches.models import Match
    from src.teams.models import Team

    async with SessionLocal() as s:
        liga = League(name="Liga volumen fixture", season="2026", created_by=organizador_creado.id)
        s.add(liga)
        await s.flush()
        equipos = [
            Team(league_id=liga.id, name=f"Equipo volumen {i:02}", created_by=organizador_creado.id)
            for i in range(20)
        ]
        s.add_all(equipos)
        await s.flush()
        base = datetime(2027, 1, 1, 18, tzinfo=UTC)
        partidos = []
        for local in range(20):
            for visitante in range(local + 1, 20):
                partidos.append(
                    Match(
                        league_id=liga.id,
                        home_team_id=equipos[local].id,
                        away_team_id=equipos[visitante].id,
                        scheduled_at=base + timedelta(hours=len(partidos)),
                        status="scheduled",
                        created_by=organizador_creado.id,
                    )
                )
        s.add_all(partidos)
        await s.commit()
        return {"league_id": str(liga.id), "total": len(partidos)}


@pytest_asyncio.fixture
async def partido_con_plantillas(organizador_creado):
    """Escenario de eventos de gol (spec 009).

    Un partido finalizado 3-1 entre dos equipos con jugadores, un tercer equipo
    de la misma liga cuyo jugador es ajeno al partido (FR-002), un jugador dado
    de baja lógica en el equipo local (Assumption "Jugadores dados de baja") y
    los partidos `scheduled` y `cancelled` que no admiten goles.
    """
    from src.core.db import SessionLocal
    from src.leagues.models import League
    from src.matches.models import Match
    from src.players.models import Player
    from src.teams.models import Team

    autor = organizador_creado.id
    async with SessionLocal() as s:
        liga = League(name="Liga goles fixture", season="2026", created_by=autor)
        s.add(liga)
        await s.flush()

        local, visitante, ajeno = (
            Team(league_id=liga.id, name=nombre, created_by=autor)
            for nombre in ("Local Goles", "Visitante Goles", "Ajeno Goles")
        )
        s.add_all([local, visitante, ajeno])
        await s.flush()

        jugador_local = Player(team_id=local.id, name="Delantero Local", number=9, created_by=autor)
        jugador_visitante = Player(
            team_id=visitante.id, name="Delantero Visitante", number=9, created_by=autor
        )
        jugador_ajeno = Player(team_id=ajeno.id, name="Jugador Ajeno", number=9, created_by=autor)
        jugador_inactivo = Player(
            team_id=local.id,
            name="Retirado Local",
            number=15,
            status="inactive",
            created_by=autor,
        )
        s.add_all([jugador_local, jugador_visitante, jugador_ajeno, jugador_inactivo])
        await s.flush()

        base = datetime(2026, 9, 1, 18, tzinfo=UTC)
        finalizado = Match(
            league_id=liga.id,
            home_team_id=local.id,
            away_team_id=visitante.id,
            scheduled_at=base - timedelta(days=1),
            status="finished",
            home_score=3,
            away_score=1,
            created_by=autor,
        )
        programado = Match(
            league_id=liga.id,
            home_team_id=local.id,
            away_team_id=ajeno.id,
            scheduled_at=base + timedelta(days=1),
            status="scheduled",
            created_by=autor,
        )
        cancelado = Match(
            league_id=liga.id,
            home_team_id=visitante.id,
            away_team_id=ajeno.id,
            scheduled_at=base + timedelta(days=2),
            status="cancelled",
            created_by=autor,
        )
        s.add_all([finalizado, programado, cancelado])
        await s.commit()

        return {
            "league_id": str(liga.id),
            "match_id": str(finalizado.id),
            "scheduled_match_id": str(programado.id),
            "cancelled_match_id": str(cancelado.id),
            "home_team_id": str(local.id),
            "away_team_id": str(visitante.id),
            "home_player_id": str(jugador_local.id),
            "away_player_id": str(jugador_visitante.id),
            "foreign_player_id": str(jugador_ajeno.id),
            "inactive_player_id": str(jugador_inactivo.id),
        }


@pytest_asyncio.fixture
async def escenario_tarjetas(organizador_creado):
    """Escenario de tarjetas y sanciones (spec 014).

    Partido finalizado con alineación, partido en curso sin alineación, segundo
    partido finalizado para acumulación entre partidos, y partidos no jugables.
    """
    from src.core.db import SessionLocal
    from src.leagues.models import League
    from src.matches.models import Match, MatchLineup
    from src.players.models import Player
    from src.teams.models import Team

    autor = organizador_creado.id
    async with SessionLocal() as s:
        liga = League(name="Liga tarjetas fixture", season="2026", created_by=autor)
        s.add(liga)
        await s.flush()

        local, visitante, ajeno = (
            Team(league_id=liga.id, name=nombre, created_by=autor)
            for nombre in ("Local Tarjetas", "Visitante Tarjetas", "Ajeno Tarjetas")
        )
        s.add_all([local, visitante, ajeno])
        await s.flush()

        jugador_local = Player(team_id=local.id, name="Medio Local", number=8, created_by=autor)
        jugador_visitante = Player(
            team_id=visitante.id, name="Medio Visitante", number=6, created_by=autor
        )
        jugador_ajeno = Player(team_id=ajeno.id, name="Jugador Ajeno", number=11, created_by=autor)
        jugador_sin_lineup = Player(
            team_id=local.id, name="Suplente Local", number=22, created_by=autor
        )
        s.add_all([jugador_local, jugador_visitante, jugador_ajeno, jugador_sin_lineup])
        await s.flush()

        base = datetime(2026, 10, 1, 18, tzinfo=UTC)
        finalizado = Match(
            league_id=liga.id,
            home_team_id=local.id,
            away_team_id=visitante.id,
            scheduled_at=base - timedelta(days=2),
            status="finished",
            home_score=1,
            away_score=0,
            created_by=autor,
        )
        finalizado_2 = Match(
            league_id=liga.id,
            home_team_id=visitante.id,
            away_team_id=local.id,
            scheduled_at=base - timedelta(days=1),
            status="finished",
            home_score=0,
            away_score=0,
            created_by=autor,
        )
        en_curso = Match(
            league_id=liga.id,
            home_team_id=local.id,
            away_team_id=visitante.id,
            scheduled_at=base,
            status="in_progress",
            created_by=autor,
        )
        programado = Match(
            league_id=liga.id,
            home_team_id=local.id,
            away_team_id=ajeno.id,
            scheduled_at=base + timedelta(days=1),
            status="scheduled",
            created_by=autor,
        )
        cancelado = Match(
            league_id=liga.id,
            home_team_id=visitante.id,
            away_team_id=ajeno.id,
            scheduled_at=base + timedelta(days=2),
            status="cancelled",
            created_by=autor,
        )
        s.add_all([finalizado, finalizado_2, en_curso, programado, cancelado])
        await s.flush()

        s.add_all(
            [
                MatchLineup(
                    match_id=finalizado.id,
                    team_id=local.id,
                    player_id=jugador_local.id,
                    created_by=autor,
                ),
                MatchLineup(
                    match_id=finalizado.id,
                    team_id=visitante.id,
                    player_id=jugador_visitante.id,
                    created_by=autor,
                ),
            ]
        )
        await s.commit()

        return {
            "league_id": str(liga.id),
            "match_id": str(finalizado.id),
            "match_id_2": str(finalizado_2.id),
            "in_progress_match_id": str(en_curso.id),
            "scheduled_match_id": str(programado.id),
            "cancelled_match_id": str(cancelado.id),
            "home_team_id": str(local.id),
            "away_team_id": str(visitante.id),
            "home_player_id": str(jugador_local.id),
            "away_player_id": str(jugador_visitante.id),
            "foreign_player_id": str(jugador_ajeno.id),
            "player_not_in_lineup_id": str(jugador_sin_lineup.id),
        }


async def _crear_liga_con_equipos(sesion, autor_id, nombre_liga, equipos):
    """Crea una liga con sus equipos. `equipos` es [(nombre, status), ...]."""
    from src.leagues.models import League
    from src.teams.models import Team

    liga = League(name=nombre_liga, season="2026", created_by=autor_id)
    sesion.add(liga)
    await sesion.flush()
    creados = {}
    for nombre, estado in equipos:
        equipo = Team(league_id=liga.id, name=nombre, status=estado, created_by=autor_id)
        sesion.add(equipo)
        creados[nombre] = equipo
    await sesion.flush()
    return liga, creados


def _partido(liga_id, local, visitante, autor_id, cuando, estado, marcador=None):
    from src.matches.models import Match

    return Match(
        league_id=liga_id,
        home_team_id=local.id,
        away_team_id=visitante.id,
        scheduled_at=cuando,
        status=estado,
        home_score=None if marcador is None else marcador[0],
        away_score=None if marcador is None else marcador[1],
        created_by=autor_id,
    )


@pytest_asyncio.fixture
async def clasificacion_liga(organizador_creado):
    """Liga con marcadores controlados para la clasificación (spec 008).

    Tabla esperada, calculada a mano desde los cuatro partidos finalizados:

        1. Alfa            PJ2 G2 E0 P0 GF5 GC1 GD+4 Pts6
        2. Delta           PJ2 G1 E1 P0 GF3 GC1 GD+2 Pts4
        3. Charlie         PJ2 G0 E1 P1 GF2 GC4 GD-2 Pts1
        4. Sin Partidos    PJ0 G0 E0 P0 GF0 GC0 GD 0 Pts0
        5. Bravo           PJ1 G0 E0 P1 GF0 GC2 GD-2 Pts0
        6. Retirado        PJ1 G0 E0 P1 GF0 GC2 GD-2 Pts0

    "Sin Partidos" queda por delante de Bravo con los mismos 0 puntos porque su
    GD es 0 y la de ellos -2 (FR-005). Bravo precede a Retirado por desempate
    alfabético (FR-006). "Fantasma" está inactivo y sin historial: no aparece.
    """
    from src.core.db import SessionLocal

    async with SessionLocal() as s:
        liga, equipos = await _crear_liga_con_equipos(
            s,
            organizador_creado.id,
            "Liga clasificacion fixture",
            [
                ("Alfa", "active"),
                ("Bravo", "active"),
                ("Charlie", "active"),
                ("Delta", "active"),
                ("Sin Partidos", "active"),
                ("Retirado", "inactive"),
                ("Fantasma", "inactive"),
            ],
        )
        base = datetime(2026, 9, 1, 18, tzinfo=UTC)
        partidos = [
            # Finalizados: única fuente de la tabla (FR-001).
            _partido(
                liga.id,
                equipos["Alfa"],
                equipos["Bravo"],
                organizador_creado.id,
                base - timedelta(days=4),
                "finished",
                (2, 0),
            ),
            _partido(
                liga.id,
                equipos["Charlie"],
                equipos["Delta"],
                organizador_creado.id,
                base - timedelta(days=3),
                "finished",
                (1, 1),
            ),
            _partido(
                liga.id,
                equipos["Alfa"],
                equipos["Charlie"],
                organizador_creado.id,
                base - timedelta(days=2),
                "finished",
                (3, 1),
            ),
            _partido(
                liga.id,
                equipos["Retirado"],
                equipos["Delta"],
                organizador_creado.id,
                base - timedelta(days=1),
                "finished",
                (0, 2),
            ),
            # No finalizados: no contribuyen (FR-001, FR-007).
            _partido(
                liga.id,
                equipos["Bravo"],
                equipos["Delta"],
                organizador_creado.id,
                base,
                "scheduled",
            ),
            _partido(
                liga.id,
                equipos["Alfa"],
                equipos["Delta"],
                organizador_creado.id,
                base + timedelta(days=1),
                "in_progress",
            ),
            _partido(
                liga.id,
                equipos["Bravo"],
                equipos["Charlie"],
                organizador_creado.id,
                base + timedelta(days=2),
                "cancelled",
            ),
        ]
        s.add_all(partidos)
        await s.commit()
        return {
            "league_id": str(liga.id),
            "teams": {nombre: str(e.id) for nombre, e in equipos.items()},
            "orden_esperado": ["Alfa", "Delta", "Charlie", "Sin Partidos", "Bravo", "Retirado"],
            "programado_id": str(partidos[4].id),
            "cancelado_id": str(partidos[6].id),
            "finalizado_id": str(partidos[0].id),
        }


@pytest_asyncio.fixture
async def clasificacion_empates(organizador_creado):
    """Tres ligas, una por nivel de desempate de FR-005/FR-006.

    - `gd`: mismos puntos, distinta diferencia de goles.
    - `gf`: mismos puntos y GD, distintos goles a favor.
    - `total`: mismos puntos, GD y GF -> desempate alfabético. Yankee se
      inserta antes que Xray para que el orden no pueda salir de la inserción.
    """
    from src.core.db import SessionLocal

    escenarios = {
        "gd": (
            "Liga empate gd",
            ["Gd Mayor", "Gd Menor", "Perdedor Goleado", "Perdedor Ajustado"],
            [("Gd Mayor", "Perdedor Goleado", (3, 0)), ("Gd Menor", "Perdedor Ajustado", (1, 0))],
            ["Gd Mayor", "Gd Menor", "Perdedor Ajustado", "Perdedor Goleado"],
        ),
        "gf": (
            "Liga empate gf",
            ["Gf Mayor", "Gf Menor", "Rival Uno", "Rival Dos"],
            [("Gf Mayor", "Rival Uno", (2, 1)), ("Gf Menor", "Rival Dos", (1, 0))],
            ["Gf Mayor", "Gf Menor", "Rival Uno", "Rival Dos"],
        ),
        "total": (
            "Liga empate total",
            ["Yankee", "Xray", "Victima Y", "Victima X"],
            [("Yankee", "Victima Y", (1, 0)), ("Xray", "Victima X", (1, 0))],
            ["Xray", "Yankee", "Victima X", "Victima Y"],
        ),
    }

    resultado = {}
    async with SessionLocal() as s:
        for clave, (nombre_liga, nombres, enfrentamientos, esperado) in escenarios.items():
            liga, equipos = await _crear_liga_con_equipos(
                s, organizador_creado.id, nombre_liga, [(n, "active") for n in nombres]
            )
            base = datetime(2026, 9, 1, 18, tzinfo=UTC)
            for indice, (local, visitante, marcador) in enumerate(enfrentamientos):
                s.add(
                    _partido(
                        liga.id,
                        equipos[local],
                        equipos[visitante],
                        organizador_creado.id,
                        base + timedelta(hours=indice),
                        "finished",
                        marcador,
                    )
                )
            resultado[clave] = {"league_id": str(liga.id), "orden_esperado": esperado}
        await s.commit()
    return resultado


@pytest_asyncio.fixture
async def dashboard_resumen(organizador_creado):
    """Liga con más de 5 elementos en cada bloque del dashboard (spec 011).

    7 equipos, 7 partidos `finished` y 7 `scheduled`, con fechas escalonadas
    e insertados en un orden que NO coincide con el orden esperado de ningún
    bloque — así, un dashboard que usara el orden de inserción en vez del
    `scheduled_at` heredado de 007 (o el cálculo heredado de 008) fallaría
    la prueba. Ninguna fixture existente cubre los tres bloques a la vez con
    más de 5 elementos cada uno (`calendario_mixto` tiene 2+2,
    `calendario_190` no tiene `finished`, `clasificacion_liga` tiene 5 filas).
    """
    from src.core.db import SessionLocal

    async with SessionLocal() as s:
        nombres = [f"Equipo dashboard {i}" for i in range(1, 8)]
        liga, equipos = await _crear_liga_con_equipos(
            s,
            organizador_creado.id,
            "Liga dashboard fixture",
            [(n, "active") for n in nombres],
        )
        e1, e2, e3, e4, e5, e6, e7 = (equipos[n] for n in nombres)

        # Partidos finalizados: offset en días desde `base_fin`, insertados
        # fuera de orden. Marcadores elegidos para que el top 5 de la
        # clasificación resultante no tenga empates (ver `clasificacion_esperada`).
        base_fin = datetime(2026, 6, 1, 18, tzinfo=UTC)
        finalizados = [
            (e1, e2, 0, (2, 0)),
            (e3, e4, 6, (1, 1)),
            (e5, e6, 2, (3, 1)),
            (e7, e1, 9, (0, 2)),
            (e2, e3, 1, (1, 0)),
            (e4, e5, 8, (2, 2)),
            (e6, e7, 4, (1, 0)),
        ]
        por_offset_fin = {}
        for local, visitante, offset, marcador in finalizados:
            partido = _partido(
                liga.id,
                local,
                visitante,
                organizador_creado.id,
                base_fin + timedelta(days=offset),
                "finished",
                marcador,
            )
            s.add(partido)
            por_offset_fin[offset] = partido

        # Partidos programados: mismo patrón, offsets futuros fuera de orden.
        base_prox = datetime(2027, 1, 1, 18, tzinfo=UTC)
        programados = [
            (e1, e3, 5),
            (e2, e4, 1),
            (e5, e7, 8),
            (e6, e1, 3),
            (e3, e5, 9),
            (e4, e6, 2),
            (e7, e2, 6),
        ]
        por_offset_prox = {}
        for local, visitante, offset in programados:
            partido = _partido(
                liga.id,
                local,
                visitante,
                organizador_creado.id,
                base_prox + timedelta(days=offset),
                "scheduled",
            )
            s.add(partido)
            por_offset_prox[offset] = partido

        await s.commit()

        return {
            "league_id": str(liga.id),
            "teams": {n: str(e.id) for n, e in equipos.items()},
            # Los 5 finalizados más recientes (offset mayor = fecha más
            # reciente), de más a menos reciente.
            "recientes_esperados": [str(por_offset_fin[o].id) for o in (9, 8, 6, 4, 2)],
            # Los 5 programados más próximos (offset menor = fecha más
            # cercana), del más cercano en adelante.
            "proximos_esperados": [str(por_offset_prox[o].id) for o in (1, 2, 3, 5, 6)],
            # Top 5 de la clasificación calculada a mano desde `finalizados`:
            # dashboard 1: PJ2 G2 E0 P0 GF4 GC0 GD+4 Pts6
            # dashboard 5: PJ2 G1 E1 P0 GF5 GC3 GD+2 Pts4
            # dashboard 6: PJ2 G1 E0 P1 GF2 GC3 GD-1 Pts3 (GF 2 > dashboard 2)
            # dashboard 2: PJ2 G1 E0 P1 GF1 GC2 GD-1 Pts3
            # dashboard 4: PJ2 E2 E0 P0 GF3 GC3 GD 0 Pts2
            # (fuera del top 5: dashboard 3 con 1pt, dashboard 7 con 0pts)
            "clasificacion_esperada": [
                "Equipo dashboard 1",
                "Equipo dashboard 5",
                "Equipo dashboard 6",
                "Equipo dashboard 2",
                "Equipo dashboard 4",
            ],
        }
