"""Reglas de ficha disciplinaria — spec 014."""

import uuid

from src.sanctions.rules import TarjetaRegistrada, calcular_ficha_disciplinaria

M1 = uuid.uuid4()
M2 = uuid.uuid4()


def ficha(*tarjetas: tuple[str, uuid.UUID]):
    return calcular_ficha_disciplinaria(
        [TarjetaRegistrada(type=tipo, match_id=partido) for tipo, partido in tarjetas]
    )


def test_sin_tarjetas_no_suspende():
    amarillas, rojas, suspendido = ficha()
    assert (amarillas, rojas, suspendido) == (0, 0, False)


def test_una_amarilla_no_suspende():
    amarillas, rojas, suspendido = ficha(("YELLOW_CARD", M1))
    assert (amarillas, rojas, suspendido) == (1, 0, False)


def test_dos_amarillas_mismo_partido_no_suspende():
    amarillas, rojas, suspendido = ficha(
        ("YELLOW_CARD", M1),
        ("YELLOW_CARD", M1),
    )
    assert (amarillas, rojas, suspendido) == (2, 0, False)


def test_dos_amarillas_partidos_distintos_suspende():
    amarillas, rojas, suspendido = ficha(
        ("YELLOW_CARD", M1),
        ("YELLOW_CARD", M2),
    )
    assert (amarillas, rojas, suspendido) == (2, 0, True)


def test_una_roja_suspende():
    amarillas, rojas, suspendido = ficha(("RED_CARD", M1))
    assert (amarillas, rojas, suspendido) == (0, 1, True)
