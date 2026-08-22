# Phase 1 — Data Model: Bloqueo tras intentos fallidos de inicio de sesión

**Spec**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md) · **Research**: [research.md](./research.md)

El modelo de dominio completo del proyecto (`User`, `Session`, `League`, `Team`,
`Player`, `Match`, `MatchEvent`…) está en
[`specs/001-fundacion-y-autenticacion/data-model.md`](../001-fundacion-y-autenticacion/data-model.md)
y **no se redefine aquí** (`AGENTS.md` §5).

Esta HU **añade una entidad** y **no modifica ninguna existente**: `users` y
`sessions` quedan exactamente como están.

---

## Entidad nueva: `LoginAttempt`

Corresponde a *"Intento de inicio de sesión"* en las **Key Entities** de la
spec. Modelo SQLAlchemy `IntentoDeLogin`, tabla `login_attempts`, en
`backend/src/auth/models.py` junto a `Usuario` y `Sesion`.

Una fila por **identificador normalizado** que haya fallado al menos una vez.
No es un log: se sobrescribe en cada intento y se **borra** al iniciar sesión
correctamente.

### Campos

| Campo | Tipo | Restricciones | Origen |
|---|---|---|---|
| `id` | `UUID` | PK, default `uuid4` | Convención del proyecto (`UUIDPrimaryKey`) |
| `username_normalizado` | `String(60)` | **NOT NULL**, **UNIQUE**, indexado | FR-001, clarificación 2026-08-21 |
| `failed_count` | `Integer` | NOT NULL, default `0`, `>= 0` | FR-001 |
| `blocked_until` | `DateTime(timezone=True)` | NULL cuando no hay bloqueo activo | FR-002, FR-004 |
| `last_attempt_at` | `DateTime(timezone=True)` | NOT NULL, `server_default=now()` | Key Entities ("su última actualización") |
| `created_at` | `DateTime(timezone=True)` | NOT NULL, `server_default=now()` | Mixin `TimestampCreated` |

**Mixins**: `Base`, `UUIDPrimaryKey`, `TimestampCreated` — los mismos que
`Usuario` y `Sesion` (`src/core/models_base.py`).

### Decisiones de modelado

- **Sin clave foránea a `users`.** Deliberado, no un olvido: FR-001 obliga a
  contar intentos contra identificadores **que no existen**. Una FK haría
  imposible registrar justamente el caso que la spec exige
  (`research.md` §1). Es también lo que impide que la fila revele si el
  identificador está registrado.
- **`username_normalizado`, no `username`.** Se almacena ya en minúsculas
  (`username.lower()`), la misma expresión con la que `AuthService.autenticar`
  busca al usuario. El bloqueo no se esquiva alternando mayúsculas
  (`research.md` §2).
- **`UNIQUE` sobre `username_normalizado`.** No es solo una restricción de
  integridad: es el `ON CONFLICT target` del UPSERT atómico que hace el conteo
  consistente ante intentos simultáneos (`research.md` §6).
- **Índice sobre una columna, no funcional.** A diferencia de
  `ix_leagues_unique_name_season`, este índice es sobre una columna ya
  normalizada, no sobre `lower(trim(...))`. `alembic --autogenerate` no lo verá
  cambiar espuriamente en specs futuras (`AGENTS.md`, nota de índices
  funcionales).
- **`blocked_until` nullable.** `NULL` = nunca ha estado bloqueado, o el
  bloqueo ya caducó y aún no se ha vuelto a fallar. Un timestamp en el pasado
  también significa "no bloqueado": el desbloqueo es implícito, por comparación
  (`research.md` §8).
- **No expone existencia.** La entidad no tiene ningún campo que distinga un
  identificador registrado de uno inventado (FR-006).

### Índice

| Nombre | Definición | Para qué |
|---|---|---|
| `ix_login_attempts_username_normalizado` | `UNIQUE (username_normalizado)` | Lookup en cada login + `ON CONFLICT` del UPSERT |

---

## Estados y transiciones

Un identificador está en uno de tres estados. El estado **no se almacena**: se
deriva de `failed_count` y `blocked_until` en el momento de la comprobación.

```
                   fallo (count+1 < umbral)
                  ┌───────────────────────┐
                  │                       │
                  v                       │
   [ LIMPIO ] ──────────────────────> [ CONTANDO ]
   sin fila                            1 <= failed_count < umbral
   o count=0                           blocked_until nulo/pasado
       ^                                    │
       │                                    │ fallo que alcanza el umbral
       │ login correcto                     │ (count = umbral)
       │ (se borra la fila)                 v
       │                              [ BLOQUEADO ]
       └──────────────────────────    blocked_until > now()
              login correcto          failed_count = 0
              tras caducar
                                            │
                                            │ transcurre el tiempo
                                            v  (sin ninguna acción)
                                       [ LIMPIO ]
                                       blocked_until en el pasado
```

| Transición | Disparador | Efecto | Requisito |
|---|---|---|---|
| LIMPIO → CONTANDO | Intento fallido | `failed_count = 1`, se crea la fila | FR-001 |
| CONTANDO → CONTANDO | Intento fallido bajo el umbral | `failed_count += 1` (atómico) | FR-001 |
| CONTANDO → BLOQUEADO | El incremento alcanza `LOGIN_MAX_FAILED_ATTEMPTS` | `blocked_until = now() + LOGIN_LOCKOUT_SECONDS`, `failed_count = 0` | FR-002 |
| BLOQUEADO → BLOQUEADO | Cualquier intento, **con contraseña correcta o incorrecta** | Ninguno: se rechaza sin verificar la contraseña y **sin extender** el bloqueo | FR-003 |
| BLOQUEADO → LIMPIO | Transcurre el tiempo | Ninguno: `blocked_until` queda en el pasado | FR-004 |
| CONTANDO → LIMPIO | Login correcto | Se **borra** la fila | FR-005 |
| LIMPIO (tras caducar) → LIMPIO | Login correcto | Se **borra** la fila | FR-005, Historia 2 AS3 |

**El bloqueo no se auto-extiende**: un intento durante el bloqueo se rechaza en
el paso previo a contar, así que no incrementa nada ni empuja `blocked_until`
hacia adelante. De lo contrario un atacante persistente mantendría al usuario
legítimo bloqueado para siempre, y FR-004 dejaría de cumplirse.

---

## Reglas de validación

| Regla | Dónde se aplica |
|---|---|
| `username_normalizado` siempre en minúsculas, máx. 60 caracteres | Servicio, al normalizar; el largo lo topa ya `LoginRequest.username` (`max_length=60`) |
| `failed_count >= 0` | Nunca decrece: solo se incrementa, se pone a 0 al bloquear, o la fila se borra |
| `blocked_until` siempre timezone-aware (UTC) | `DateTime(timezone=True)`, igual que `Sesion.expires_at` |
| Una sola fila por identificador | `UNIQUE` + UPSERT |

---

## Efecto sobre entidades existentes

**Ninguno.** `users` y `sessions` no cambian de esquema, ni de columnas, ni de
índices. La migración de esta HU contiene exclusivamente `create_table` de
`login_attempts` y su índice único (`research.md` §11).
