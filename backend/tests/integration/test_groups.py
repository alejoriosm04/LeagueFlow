"""Integration tests — Acceptance Scenarios de spec.md (US1, US2, US3).

Cada test nombra el escenario que verifica. Principio II: toda regla de negocio
tiene una prueba que la afirma.
"""

import uuid

import pytest
from sqlalchemy import select
from src.core.db import SessionLocal
from src.teams.models import Team

pytestmark = pytest.mark.asyncio


async def crear_liga(cliente_organizador, nombre="Interfacultades", temporada="2026-1") -> str:
    r = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": nombre, "season": temporada}
    )
    assert r.status_code == 201
    return r.json()["id"]


async def crear_equipo(cliente_organizador, liga_id, nombre) -> str:
    r = await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/teams", json={"name": nombre})
    assert r.status_code == 201
    return r.json()["id"]


async def crear_grupo(cliente_organizador, liga_id, nombre) -> str:
    r = await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/groups", json={"name": nombre})
    assert r.status_code == 201
    return r.json()["id"]


async def _marcar_inactivo(team_id: str) -> None:
    async with SessionLocal() as s:
        res = await s.execute(select(Team).where(Team.id == uuid.UUID(team_id)))
        res.scalar_one().status = "inactive"
        await s.commit()


# --- US1: crear, renombrar y eliminar grupos ---------------------------------


async def test_crear_grupo_queda_listado(cliente, cliente_organizador):
    """US1 AS1: crear un grupo -> aparece en el listado de la liga."""
    liga_id = await crear_liga(cliente_organizador)
    await crear_grupo(cliente_organizador, liga_id, "Grupo A")

    r = await cliente.get(f"/api/v1/leagues/{liga_id}/groups")
    assert r.status_code == 200
    assert [g["name"] for g in r.json()["items"]] == ["Grupo A"]


async def test_renombrar_grupo(cliente_organizador):
    """US1 AS4: renombrar cambia el nombre."""
    liga_id = await crear_liga(cliente_organizador)
    gid = await crear_grupo(cliente_organizador, liga_id, "Grupo A")

    r = await cliente_organizador.patch(f"/api/v1/groups/{gid}", json={"name": "Grupo B"})
    assert r.status_code == 200
    assert r.json()["name"] == "Grupo B"


async def test_eliminar_grupo_borra_membresias_no_equipos(cliente, cliente_organizador):
    """US1 AS5 + FR-004: borrar el grupo deja el equipo intacto."""
    liga_id = await crear_liga(cliente_organizador)
    gid = await crear_grupo(cliente_organizador, liga_id, "Grupo A")
    tid = await crear_equipo(cliente_organizador, liga_id, "Equipo X")
    assert (
        await cliente_organizador.post(f"/api/v1/groups/{gid}/teams", json={"team_id": tid})
    ).status_code == 201

    assert (await cliente_organizador.delete(f"/api/v1/groups/{gid}")).status_code == 204

    # El grupo ya no existe y el equipo sigue accesible.
    assert (
        await cliente_organizador.patch(f"/api/v1/groups/{gid}", json={"name": "X"})
    ).status_code == 404
    assert (await cliente.get(f"/api/v1/teams/{tid}")).status_code == 200


async def test_nombre_duplicado_insensible_a_mayusculas(cliente_organizador):
    """US1 AS2: unicidad por liga, insensible a mayúsculas y espacios."""
    liga_id = await crear_liga(cliente_organizador)
    assert (
        await cliente_organizador.post(
            f"/api/v1/leagues/{liga_id}/groups", json={"name": "Grupo A"}
        )
    ).status_code == 201

    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/groups", json={"name": "  GRUPO   A  "}
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "group_name_duplicate"


async def test_mismo_nombre_en_ligas_distintas_es_valido(cliente_organizador):
    """US1 AS3: el mismo nombre es válido en ligas distintas."""
    liga_a = await crear_liga(cliente_organizador, nombre="Liga A", temporada="2026-1")
    liga_b = await crear_liga(cliente_organizador, nombre="Liga B", temporada="2026-2")

    for liga in (liga_a, liga_b):
        assert (
            await cliente_organizador.post(
                f"/api/v1/leagues/{liga}/groups", json={"name": "Grupo A"}
            )
        ).status_code == 201


# --- US2: asignar y desasignar equipos --------------------------------------


async def test_asignar_y_desasignar_equipo(cliente, cliente_organizador):
    """US2 AS1/AS4: asignar refleja el equipo; desasignar lo quita."""
    liga_id = await crear_liga(cliente_organizador)
    gid = await crear_grupo(cliente_organizador, liga_id, "Grupo A")
    tid = await crear_equipo(cliente_organizador, liga_id, "Equipo X")

    assert (
        await cliente_organizador.post(f"/api/v1/groups/{gid}/teams", json={"team_id": tid})
    ).status_code == 201

    lista = await cliente.get(f"/api/v1/leagues/{liga_id}/groups")
    assert [t["name"] for t in lista.json()["items"][0]["teams"]] == ["Equipo X"]

    assert (
        await cliente_organizador.delete(f"/api/v1/groups/{gid}/teams", params={"team_id": tid})
    ).status_code == 204

    lista2 = await cliente.get(f"/api/v1/leagues/{liga_id}/groups")
    assert lista2.json()["items"][0]["teams"] == []


async def test_equipo_ya_en_otro_grupo_se_rechaza(cliente_organizador):
    """US2 AS2 / FR-007: a lo sumo un grupo por liga."""
    liga_id = await crear_liga(cliente_organizador)
    g1 = await crear_grupo(cliente_organizador, liga_id, "Grupo A")
    g2 = await crear_grupo(cliente_organizador, liga_id, "Grupo B")
    tid = await crear_equipo(cliente_organizador, liga_id, "Equipo X")

    assert (
        await cliente_organizador.post(f"/api/v1/groups/{g1}/teams", json={"team_id": tid})
    ).status_code == 201

    r = await cliente_organizador.post(f"/api/v1/groups/{g2}/teams", json={"team_id": tid})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "team_already_in_group"


async def test_equipo_de_otra_liga_se_rechaza(cliente_organizador):
    """US2 AS3 / FR-008: el equipo debe ser de la liga del grupo."""
    liga_a = await crear_liga(cliente_organizador, nombre="Liga A", temporada="2026-1")
    liga_b = await crear_liga(cliente_organizador, nombre="Liga B", temporada="2026-2")
    gid = await crear_grupo(cliente_organizador, liga_a, "Grupo A")
    tid = await crear_equipo(cliente_organizador, liga_b, "Equipo B")

    r = await cliente_organizador.post(f"/api/v1/groups/{gid}/teams", json={"team_id": tid})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "team_not_found_in_league"


async def test_equipo_inactivo_se_rechaza(cliente_organizador):
    """FR-011: solo equipos activos son asignables."""
    liga_id = await crear_liga(cliente_organizador)
    gid = await crear_grupo(cliente_organizador, liga_id, "Grupo A")
    tid = await crear_equipo(cliente_organizador, liga_id, "Equipo X")
    await _marcar_inactivo(tid)

    r = await cliente_organizador.post(f"/api/v1/groups/{gid}/teams", json={"team_id": tid})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "team_inactive"


# --- US3: consultar la composición ------------------------------------------


async def test_composicion_incluye_inactivo_miembro(cliente, cliente_organizador):
    """FR-012: un equipo inactivo que ya es miembro sigue en la composición."""
    liga_id = await crear_liga(cliente_organizador)
    gid = await crear_grupo(cliente_organizador, liga_id, "Grupo A")
    tid = await crear_equipo(cliente_organizador, liga_id, "Equipo X")
    assert (
        await cliente_organizador.post(f"/api/v1/groups/{gid}/teams", json={"team_id": tid})
    ).status_code == 201
    await _marcar_inactivo(tid)

    lista = await cliente.get(f"/api/v1/leagues/{liga_id}/groups")
    equipos = lista.json()["items"][0]["teams"]
    assert len(equipos) == 1
    assert equipos[0]["status"] == "inactive"


async def test_liga_sin_grupos_devuelve_lista_vacia(cliente, cliente_organizador):
    """US3 AS2: sin grupos, la consulta responde lista vacía sin errores."""
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente.get(f"/api/v1/leagues/{liga_id}/groups")
    assert r.status_code == 200
    assert r.json()["items"] == []
