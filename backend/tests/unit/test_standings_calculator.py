"""Reglas de puntuación, orden y desempate de la clasificación — spec 008.

La clasificación es una función pura de sus entradas
(`MatchResult -> StandingsCalculator -> Standings`, constitución), así que sus
reglas se prueban aquí sin base de datos ni HTTP.
"""

import uuid

from src.statistics.calculator import EquipoEnTabla, PartidoParaTabla, calcular_clasificacion


def equipo(nombre: str, activo: bool = True) -> EquipoEnTabla:
    return EquipoEnTabla(id=uuid.uuid4(), name=nombre, activo=activo)


def jugado(local, visitante, goles_local, goles_visitante) -> PartidoParaTabla:
    return PartidoParaTabla(
        home_team_id=local.id,
        away_team_id=visitante.id,
        home_score=goles_local,
        away_score=goles_visitante,
        status="finished",
    )


def sin_jugar(local, visitante, estado) -> PartidoParaTabla:
    return PartidoParaTabla(
        home_team_id=local.id,
        away_team_id=visitante.id,
        home_score=None,
        away_score=None,
        status=estado,
    )


def por_nombre(tabla) -> dict:
    return {fila.team_name: fila for fila in tabla}


def test_victoria_da_tres_puntos_y_derrota_cero():
    """AS1 / FR-003."""
    a, b = equipo("A"), equipo("B")
    tabla = por_nombre(calcular_clasificacion([a, b], [jugado(a, b, 2, 0)]))
    assert (tabla["A"].points, tabla["A"].won, tabla["A"].lost) == (3, 1, 0)
    assert (tabla["B"].points, tabla["B"].won, tabla["B"].lost) == (0, 0, 1)


def test_empate_da_un_punto_a_cada_equipo():
    """AS2 / FR-003."""
    a, b = equipo("A"), equipo("B")
    tabla = por_nombre(calcular_clasificacion([a, b], [jugado(a, b, 1, 1)]))
    assert [tabla["A"].points, tabla["B"].points] == [1, 1]
    assert [tabla["A"].drawn, tabla["B"].drawn] == [1, 1]


def test_visitante_tambien_suma_como_local():
    """La puntuación no depende de en qué columna juega el equipo."""
    a, b = equipo("A"), equipo("B")
    tabla = por_nombre(calcular_clasificacion([a, b], [jugado(a, b, 0, 4)]))
    assert tabla["B"].points == 3
    assert (tabla["B"].goals_for, tabla["B"].goals_against) == (4, 0)


def test_ordena_por_puntos_descendente():
    """FR-005 criterio 1."""
    lider, medio, ultimo = equipo("Lider"), equipo("Medio"), equipo("Ultimo")
    tabla = calcular_clasificacion(
        [ultimo, medio, lider],
        [jugado(lider, ultimo, 1, 0), jugado(lider, medio, 1, 0), jugado(medio, ultimo, 1, 1)],
    )
    assert [fila.team_name for fila in tabla] == ["Lider", "Medio", "Ultimo"]
    assert [fila.position for fila in tabla] == [1, 2, 3]


def test_desempata_por_diferencia_de_goles():
    """AS3 / FR-005 criterio 2."""
    mayor, menor, v1, v2 = equipo("Mayor"), equipo("Menor"), equipo("V1"), equipo("V2")
    tabla = calcular_clasificacion(
        [menor, mayor, v1, v2], [jugado(mayor, v1, 3, 0), jugado(menor, v2, 1, 0)]
    )
    assert [fila.team_name for fila in tabla][:2] == ["Mayor", "Menor"]
    assert (tabla[0].goal_difference, tabla[1].goal_difference) == (3, 1)


def test_desempata_por_goles_a_favor_con_misma_diferencia():
    """AS4 / FR-005 criterio 3."""
    mayor, menor, v1, v2 = equipo("Mayor"), equipo("Menor"), equipo("V1"), equipo("V2")
    tabla = calcular_clasificacion(
        [menor, mayor, v1, v2], [jugado(mayor, v1, 2, 1), jugado(menor, v2, 1, 0)]
    )
    assert [fila.team_name for fila in tabla][:2] == ["Mayor", "Menor"]
    assert tabla[0].goal_difference == tabla[1].goal_difference == 1
    assert (tabla[0].goals_for, tabla[1].goals_for) == (2, 1)


def test_empate_absoluto_se_resuelve_alfabeticamente_y_es_estable():
    """FR-006: mismos puntos, GD y GF. El orden no depende de la entrada."""
    yankee, xray = equipo("Yankee"), equipo("Xray")
    vy, vx = equipo("Victima Y"), equipo("Victima X")
    partidos = [jugado(yankee, vy, 1, 0), jugado(xray, vx, 1, 0)]
    esperado = ["Xray", "Yankee", "Victima X", "Victima Y"]
    for entrada in ([yankee, xray, vy, vx], [vx, vy, xray, yankee], [xray, vy, yankee, vx]):
        tabla = calcular_clasificacion(entrada, partidos)
        assert [fila.team_name for fila in tabla] == esperado


def test_desempate_alfabetico_ignora_mayusculas_y_espacios():
    """FR-006 sobre el nombre normalizado, como la unicidad de nombre de 003."""
    beta, alfa = equipo("  beta"), equipo("ALFA")
    tabla = calcular_clasificacion([beta, alfa], [])
    assert [fila.team_name for fila in tabla] == ["ALFA", "  beta"]


def test_solo_los_partidos_finalizados_contribuyen():
    """AS5 / FR-001 / FR-007: programado, en curso y cancelado no suman."""
    a, b = equipo("A"), equipo("B")
    partidos = [
        jugado(a, b, 2, 0),
        sin_jugar(a, b, "scheduled"),
        sin_jugar(a, b, "in_progress"),
        sin_jugar(b, a, "cancelled"),
    ]
    tabla = por_nombre(calcular_clasificacion([a, b], partidos))
    assert tabla["A"].played == tabla["B"].played == 1
    assert (tabla["A"].points, tabla["B"].points) == (3, 0)


def test_equipo_sin_partidos_aparece_en_ceros():
    a, b, nuevo = equipo("A"), equipo("B"), equipo("Nuevo")
    tabla = por_nombre(calcular_clasificacion([a, b, nuevo], [jugado(a, b, 1, 0)]))
    fila = tabla["Nuevo"]
    assert (fila.played, fila.won, fila.drawn, fila.lost) == (0, 0, 0, 0)
    assert (fila.goals_for, fila.goals_against, fila.goal_difference, fila.points) == (0, 0, 0, 0)


def test_inactivo_con_historial_aparece_e_inactivo_sin_historial_no():
    """Assumption de la spec: la tabla no puede perder los puntos de los rivales."""
    activo = equipo("Activo")
    retirado = equipo("Retirado", activo=False)
    fantasma = equipo("Fantasma", activo=False)
    tabla = calcular_clasificacion([activo, retirado, fantasma], [jugado(activo, retirado, 2, 0)])
    nombres = [fila.team_name for fila in tabla]
    assert nombres == ["Activo", "Retirado"]
    assert "Fantasma" not in nombres


def test_posiciones_son_consecutivas_desde_uno():
    equipos = [equipo(f"Equipo {i}") for i in range(5)]
    tabla = calcular_clasificacion(equipos, [jugado(equipos[0], equipos[1], 1, 0)])
    assert [fila.position for fila in tabla] == [1, 2, 3, 4, 5]


def test_invariantes_aritmeticas_de_la_tabla():
    """played = G+E+P, points = 3G+E, GD = GF-GC y la suma global GF = GC."""
    a, b, c = equipo("A"), equipo("B"), equipo("C")
    tabla = calcular_clasificacion(
        [a, b, c], [jugado(a, b, 2, 0), jugado(b, c, 1, 1), jugado(c, a, 3, 2)]
    )
    for fila in tabla:
        assert fila.played == fila.won + fila.drawn + fila.lost
        assert fila.points == fila.won * 3 + fila.drawn
        assert fila.goal_difference == fila.goals_for - fila.goals_against
    assert sum(f.goals_for for f in tabla) == sum(f.goals_against for f in tabla)


def test_liga_sin_equipos_devuelve_tabla_vacia():
    assert calcular_clasificacion([], []) == []
