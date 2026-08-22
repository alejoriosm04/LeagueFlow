# Phase 1 — Quickstart: validar el bloqueo del inicio de sesión

**Spec**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md) ·
**Contrato**: [contracts/auth-lockout.openapi.yaml](./contracts/auth-lockout.openapi.yaml)

Guía de **verificación**, no de implementación: qué hay que poder demostrar
para dar la HU por terminada. El código vive en `tasks.md` y en la fase de
implementación.

---

## Prerequisitos

Los mismos de
[`specs/001-fundacion-y-autenticacion/quickstart.md`](../001-fundacion-y-autenticacion/quickstart.md)
(PostgreSQL levantado, `.env` completo, dependencias instaladas), más las dos
variables nuevas de esta HU:

```bash
LOGIN_MAX_FAILED_ATTEMPTS=5
LOGIN_LOCKOUT_SECONDS=900
```

Ambas tienen default en `Settings`, así que la app arranca sin ellas. Se
documentan vacías en `.env.example` (FR-007, `research.md` §9).

Aplicar la migración de esta HU:

```bash
cd backend && alembic upgrade head
```

---

## Validación automatizada (la que manda)

Toda regla de negocio de esta HU tiene prueba (Principio II). La suite completa
debe quedar en verde, no solo la de esta spec (Principio IV):

```bash
cd backend && pytest
```

Solo lo de esta HU:

```bash
cd backend && pytest tests/integration/test_bloqueo_login.py tests/contract/test_auth_contract.py -v
```

Frontend (catálogo de mensajes):

```bash
cd frontend && npm test
```

### Escenarios que las pruebas deben cubrir

Trazabilidad uno a uno con los Acceptance Scenarios de la spec.

**Historia 1 — bloquear (P1)**

| # | Escenario | Verificación esperada |
|---|---|---|
| H1-AS1 | Superar el umbral bloquea | 5 POST `/auth/login` con clave incorrecta → los 5 dan `401`; el 6.º da `429` con `code: login_locked` |
| H1-AS2 | Bloqueado rechaza la clave **correcta** | Tras bloquear, un POST con la clave buena da `429`, **no** `200`. Núcleo de FR-003 |
| H1-AS3 | No afecta a nadie más | Con un identificador bloqueado, otro usuario hace login y obtiene `200` + cookie `lf_session` |
| H1-AS4 | No revela existencia | Bloquear un usuario **existente** y uno **inexistente**; ambos devuelven `429` con el mismo cuerpo. FR-006 |
| Edge | Mayúsculas no esquivan el bloqueo | Fallar alternando `Usuario`/`USUARIO`/`usuario` suma al **mismo** contador: al 6.º intento, `429` |
| Edge | Concurrencia | N peticiones fallidas simultáneas (`asyncio.gather`) sobre el mismo identificador no dejan `failed_count` por debajo de lo real ni saltan el bloqueo |
| FR-002 | Cabecera de reintento | La respuesta `429` trae `Retry-After` entero `>= 1` |

**Historia 2 — desbloquear (P2)**

| # | Escenario | Verificación esperada |
|---|---|---|
| H2-AS1 | El bloqueo caduca | Con el bloqueo expirado, el login correcto vuelve a dar `200` |
| H2-AS2 | Acertar antes del umbral reinicia | 3 fallos → 1 acierto → 3 fallos más → sigue en `401`, **no** `429` (el contador se reinició) |
| H2-AS3 | Acertar tras el desbloqueo deja el conteo en cero | Tras el login correcto post-desbloqueo, no queda fila en `login_attempts` para ese identificador |

**Cómo probar la expiración sin esperar 15 minutos**: el desbloqueo es una
comparación de timestamps, no un job (`research.md` §8). El test mueve
`blocked_until` al pasado con un `UPDATE` sobre la fila y vuelve a llamar al
endpoint. Nada de `sleep(900)` ni de relojes falsos.

### No romper lo que ya funciona

`backend/tests/integration/test_auth.py` y
`backend/tests/contract/test_auth_contract.py` **no se modifican**. Siguen en
verde porque cada test hace como mucho 1–2 intentos fallidos por identificador,
muy por debajo del umbral de 5, y `conftest.py` recrea el esquema en cada test
(fixture `base_limpia`), así que ningún contador se arrastra entre pruebas.

Si alguna prueba existente hubiera que tocarla, el Principio IV exige
justificarlo por escrito en el PR — no es el caso aquí.

---

## Validación manual (demo)

Backend en marcha (`uvicorn src.main:app --reload` desde `backend/`) y un
usuario creado por `scripts/seed_admin.py`.

### 1. Bloquear un identificador

Cinco intentos con una contraseña equivocada:

```bash
for i in 1 2 3 4 5; do curl -s -o /dev/null -w "intento $i -> %{http_code}\n" -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{"username":"TU_USUARIO","password":"clave-que-no-es"}'; done
```

Esperado: `intento 1..5 -> 401`.

### 2. Confirmar que ni la contraseña correcta pasa (FR-003)

```bash
curl -i -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{"username":"TU_USUARIO","password":"TU_CLAVE_CORRECTA"}'
```

Esperado: `HTTP/1.1 429`, cabecera `Retry-After: <segundos>` y cuerpo
`{"error":{"code":"login_locked", ...}}`. **Este es el paso que demuestra la
historia**: la contraseña es la buena y aun así se rechaza.

### 3. Confirmar que no revela existencia (FR-006)

Repetir los pasos 1 y 2 con un identificador **inventado**. Debe llegar
igualmente al `429`, con un cuerpo indistinguible del anterior.

### 4. Confirmar que no afecta a nadie más (SC-004)

Con el identificador anterior bloqueado, iniciar sesión con **otro** usuario:
responde `200` y devuelve la cookie `lf_session`. Sin esperas.

### 5. Confirmar el desbloqueo (FR-004)

Para no esperar 15 minutos, bajar la duración y reiniciar el backend:

```bash
LOGIN_LOCKOUT_SECONDS=20 uvicorn src.main:app --reload
```

Bloquear, esperar 20 segundos y volver a entrar con la contraseña correcta:
responde `200`. (`get_settings()` está bajo `@lru_cache`: el cambio exige
reiniciar el proceso — `research.md` §9.)

### 6. Confirmar el mensaje en la interfaz

Con el backend en marcha y el frontend en `npm run dev`: fallar 5 veces en la
pantalla de login y comprobar que el sexto intento muestra el mensaje de
bloqueo del catálogo, **no** el genérico "No fue posible completar la
operación". El mensaje es cualitativo, sin el número exacto de minutos
(`research.md` §10).

---

## Criterios de cierre

- [ ] `pytest` completo en verde, sin `skip` ni `xfail` nuevos (Principio IV).
- [ ] `npm test` en verde en el frontend.
- [ ] Linter sin excepciones silenciosas (Principio VII).
- [ ] La migración corre desde base vacía: `alembic upgrade head` sobre una BD
      nueva, con un solo `head` en el historial (`alembic heads` devuelve uno).
- [ ] `.env.example` documenta las dos llaves nuevas, vacías.
- [ ] Los 7 Acceptance Scenarios de la spec tienen una prueba que los nombra.
- [ ] `docs/metricas/017-bloqueo-login.md` creado desde la plantilla y relleno
      con datos reales (`AGENTS.md` §7) — sin inventar coste de IA ni tiempo.
