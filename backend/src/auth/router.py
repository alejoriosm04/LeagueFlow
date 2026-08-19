"""Endpoints de autenticación — contracts/auth.openapi.yaml."""

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import NOMBRE_COOKIE, requiere_rol, usuario_opcional
from src.auth.models import Usuario
from src.auth.schemas import (
    CreateUserRequest,
    LoginRequest,
    PaginatedUsers,
    SesionActual,
    UserPublic,
)
from src.auth.service import AuthService
from src.core.config import get_settings
from src.core.db import get_db
from src.core.errors import ErrorDeNegocio

router = APIRouter(tags=["auth"])


@router.post("/auth/login")
async def login(
    datos: LoginRequest, respuesta: Response, db: AsyncSession = Depends(get_db)
) -> dict:
    servicio = AuthService(db)
    usuario = await servicio.autenticar(datos.username, datos.password)
    sesion = await servicio.crear_sesion(usuario)
    settings = get_settings()

    # SameSite=none (no lax): frontend y backend viven en dominios distintos
    # (Vercel / Railway) y con lax la cookie no viajaría en fetch cross-site.
    # research.md §4. Exige Secure, que solo se relaja en desarrollo local.
    respuesta.set_cookie(
        key=NOMBRE_COOKIE,
        value=str(sesion.id),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="none" if settings.cookie_secure else "lax",
        max_age=settings.session_ttl_seconds,
        path="/",
    )
    return {"user": UserPublic.model_validate(usuario).model_dump(mode="json")}


@router.post("/auth/logout")
async def logout(request: Request, respuesta: Response, db: AsyncSession = Depends(get_db)) -> dict:
    """Revoca la sesión en el servidor y borra la cookie.

    FR-006: borrar solo la cookie dejaría la sesión viva en la base de datos y
    cualquiera con el token seguiría autenticado. La revocación es la que manda.
    """
    token = request.cookies.get(NOMBRE_COOKIE)
    if not token:
        raise ErrorDeNegocio(
            code="not_authenticated",
            message="No hay una sesión activa.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    servicio = AuthService(db)
    sesion = await servicio.obtener_sesion_valida(token)
    if sesion is None:
        raise ErrorDeNegocio(
            code="not_authenticated",
            message="No hay una sesión activa.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    await servicio.revocar_sesion(sesion)
    respuesta.delete_cookie(NOMBRE_COOKIE, path="/")
    return {"status": "ok"}


@router.get("/auth/me")
async def me(usuario: Usuario | None = Depends(usuario_opcional)) -> SesionActual:
    return SesionActual(user=UserPublic.model_validate(usuario) if usuario else None)


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    datos: CreateUserRequest,
    actor: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    servicio = AuthService(db)
    creado = await servicio.crear_usuario(
        username=datos.username, password=datos.password, role=datos.role, creado_por=actor.id
    )
    return UserPublic.model_validate(creado)


@router.get("/users")
async def listar_usuarios(
    _: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedUsers:
    servicio = AuthService(db)
    usuarios, total = await servicio.listar_usuarios(page, page_size)
    return PaginatedUsers(
        items=[UserPublic.model_validate(u) for u in usuarios],
        page=page,
        page_size=page_size,
        total=total,
    )
