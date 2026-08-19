"""Hash y verificación de contraseñas.

FR-005: la contraseña nunca se almacena de forma que permita recuperarla en
texto claro. bcrypt vía passlib.
"""

from passlib.context import CryptContext

_contexto = CryptContext(schemes=["bcrypt"], deprecated="auto")

# research.md §10
LONGITUD_MINIMA = 10
LONGITUD_MAXIMA = 128


def hashear_password(password: str) -> str:
    # bcrypt trunca a 72 bytes; el corte evita que passlib lance por longitud.
    return _contexto.hash(password[:72])


def verificar_password(password: str, hash_guardado: str) -> bool:
    return _contexto.verify(password[:72], hash_guardado)
