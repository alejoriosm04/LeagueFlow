# LeagueFlow

**LeagueFlow — Plataforma de gestión y analítica de ligas deportivas amateur**

![Image](https://images.openai.com/static-rsc-4/8KsdQrLT_Peb4L2Kp7pGX8GAjtGizo1Cch-7YRkSxbTWOgDjW-YwrdAAe9cufu4_ClwR2fch9JKcSRyNYddq2zIHsL9LZbCyBOboRqSwF5GxM4FaDd1r-eoh-87eVoEGnKYlEDcO4OKcIbcRgbQ84i1PCJmwmVF5paZDyYy5R5jgXimmRPYmTiFsV_RlM40C?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/Bz3v3VDqsro1Gmu3oZtAVXzodXcX21RR8q0nDlzW9S6GcZFi9AD1pbn46z2Qr5ShV1k1fXSrGLkvVOI81CB5AVM4adlIlxBKw0wo2KkYuaxupUq0qyoiYNUjPhbFerq2gNm5p4XRo4zONND-hx5wm2Gmzx8Ag56i-rRoEZBOMVB2W7cxec_9CmbBFCe284W-?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/yPo80xl2OssVax9CQyRCopcYLfxLLth_U1WUxLZ1-62HJNkDe2EENHu5ygiS6Y0EbmRifxZFIt89ovoPmyTZaDntP2-lavhmpbfmaLiN6w3KeCLnbjkju4NkNyhsmIMBEhzEFYUd6RhdzAapCDUNYEFWKjQHWEKbV3UGJNYiEuAMsY_BlVmehi2tleBRONu9?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/2vxGhVhKmtPuaDdFfcCqgQ1XkaBiVx4YveT4rbWoSpuVaXpGXhHKw9a4P7nqdolEWQqQTZToK-Wew2nWtdurFa8nbM757ZVVvh2dtZ0kMLJiGCHrTOShmPOhIvHRkDi2IMZvxRj-gd5QSBAAQztD7kiu4Z_FD6p74bIkmC_8lt6LKrjR9QakzuqgbsM7kXrA?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/mRY1rET6B4TZworE1JI0eaTOImSlPKLcsAvl-lJO1ijsgldaYhdp5MqWoPdI8C8m2XCq6laSrCcQ4daAGcagXUWV7SJknRC3I935cslW52QEdEtGbtI1FkosLWUIp0-BUZgSoG_-JNhSS-Ex7Bu3aPOJUKH-_93r0lu6LAYEpgEGcWHF7Co3fuftz6eLYlwA?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/pij4e6gbPF7M2u7bimH_2VRy_ljilWsBR_ACtqlUclCTdaY0eVwsH3__AWOCqXikEm_5nt4gGik_j9CJSdp2douF1_qA3LTPHV4EAjzEfwu_MleOlUXZ7OqWs1ncAcUBssDiF4O1K6gQxrKXJd1sRK8DoLbBM9hetS9u730ugYnW8eB5w_gu7nF0f_hgXBYc?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/hGf2rBN5og5Kk30N1S44Her9Z1WufeYJIA1aGRKBgIQvXShhLR0zMNoBCWs7IXVQR0fh5QeEgmdBkrm52pl2coA4c45MsSJbmy_4slm5fw02IiG25yiswh5JpEv2YHuydQeu3h1up5u51_4psuGAreP3d_aDRdArMRy_10HDRTui_0jU26WxnOYt90ykNt1H?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/yA2b2LhWGgUR29BBoCQMRY5O-jf3PRyQwZbSVoYwqOL-jUnppcZsUIJjVtoiBmC3DIna4QsqKQS39ChFm7orVIV1sxm36LHgYFAlpFJaVZbhnOgmhzOM1oK1CzdGbjvKS2cgOXXYh1zDMdBc48NrLgixME7l-36KE-CbCerrY9-KvoHiRf5OhB8jgilvZ99E?purpose=fullsize)

## 1. Problema

Las ligas universitarias y amateur necesitan gestionar información que normalmente termina distribuida entre hojas de cálculo, formularios, chats y registros manuales.

LeagueFlow centraliza:

**Liga → equipos → jugadores → partidos → eventos → resultados → clasificación → estadísticas.**

La propuesta no es competir con [Genius Sports](https://www.geniussports.com/?utm_source=chatgpt.com). Genius Sports sirve como inspiración del dominio: LeagueFlow sería una versión deliberadamente acotada para **ligas universitarias y amateur**.

### Usuario principal

El **organizador/administrador de una liga**.

También pueden existir:

* **Operador:** registra resultados/eventos.
* **Espectador:** consulta información pública.

Para esta entrega, evitaría implementar autenticación compleja si no aporta a las HU principales.

---

# 2. Qué debería hacer el MVP

Al entrar, quiero que ya parezca un producto real.

### Dashboard

```text
┌─────────────────────────────────────────────────────────┐
│ LEAGUEFLOW                         Liga Universitaria ⚽ │
├────────────┬────────────────────────────────────────────┤
│ Dashboard  │                                            │
│ Equipos    │   PARTIDOS RECIENTES                       │
│ Jugadores  │                                            │
│ Partidos   │   EAFIT       3 ─ 1       CES             │
│ Tabla      │   Nacional    2 ─ 2       UPB             │
│ Estadíst.  │                                            │
│            │   PRÓXIMOS PARTIDOS                        │
│            │                                            │
│            │   EAFIT       vs       UPB                 │
│            │                                            │
│            │   LÍDERES                                  │
│            │   🥇 EAFIT            15 pts               │
│            │   🥈 CES              12 pts               │
│            │   🥉 UPB              10 pts               │
└────────────┴────────────────────────────────────────────┘
```

Ya tienen un frontend visualmente interesante sin necesitar una barbaridad de componentes.

---

# 3. Modelo del dominio

Yo definiría desde el principio estas entidades:

```text
League
 ├── Teams
 │    └── Players
 │
 └── Matches
      └── MatchEvents

Match
 ├── HomeTeam
 ├── AwayTeam
 ├── Status
 ├── HomeScore
 ├── AwayScore
 └── Events
```

Y las estadísticas **se derivan de los partidos**, en vez de permitir que alguien modifique directamente una tabla de posiciones.

Eso es importante arquitectónicamente.

Por ejemplo:

```text
MatchResult
     ↓
StandingsCalculator
     ↓
Standings
```

---

# 4. Las ~10 Historias de Usuario de línea base

Aquí está la parte crítica. No hagan 10 HU gigantes.

Yo propondría estas:

| #    | Historia                            | Prioridad |
| ---- | ----------------------------------- | --------- |
| HU01 | Crear una liga                      | Must      |
| HU02 | Registrar equipos                   | Must      |
| HU03 | Registrar jugadores en un equipo    | Must      |
| HU04 | Crear/programar un partido          | Must      |
| HU05 | Registrar resultado de un partido   | Must      |
| HU06 | Consultar partidos                  | Must      |
| HU07 | Consultar tabla de posiciones       | Must      |
| HU08 | Registrar goles de jugadores        | Should    |
| HU09 | Consultar estadísticas de jugadores | Should    |
| HU10 | Consultar dashboard general         | Should    |

Con eso tienen las **10 HU desarrolladas y desplegadas** que pide el profesor.

Y, más importante, están conectadas.

No parecen diez CRUD independientes.

---

# 5. Las reglas de negocio

Aquí está la verdadera carne del proyecto para SDD y pruebas.

Por ejemplo:

### Partido

Un equipo no puede jugar contra sí mismo.

```text
homeTeam != awayTeam
```

Un resultado no puede contener valores negativos.

```text
homeScore >= 0
awayScore >= 0
```

Un partido `FINISHED` no puede modificar su resultado directamente.

---

### Clasificación

Por ejemplo:

```text
Victoria = 3 puntos
Empate   = 1 punto
Derrota  = 0 puntos
```

Orden:

```text
1. Puntos
2. Diferencia de goles
3. Goles a favor
```

Y:

```text
GD = GF - GA
```

Esto es **oro para pruebas automatizadas**.

---

# 6. Un ejemplo de HU con SDD

En vez de decirle a Copilot:

> hazme una tabla de posiciones

La especificación establece el comportamiento.

### HU07 — Consultar clasificación

**Como** espectador
**quiero** consultar la clasificación de una liga
**para** conocer el desempeño de los equipos.

### Acceptance Criteria

**AC01**

```text
Given EAFIT derrotó a CES
When se consulta la clasificación
Then EAFIT recibe 3 puntos
And CES recibe 0 puntos
```

**AC02**

```text
Given EAFIT empató con UPB
Then ambos reciben 1 punto
```

**AC03**

```text
Given dos equipos tienen los mismos puntos
Then el equipo con mayor diferencia de goles aparece primero
```

**AC04**

```text
Given dos equipos tienen los mismos puntos
And tienen la misma diferencia de goles
Then el equipo con más goles a favor aparece primero
```

Ahí la IA ya tiene muchísimo menos espacio para inventarse cosas.

Ese es precisamente el valor que ustedes quieren demostrar con **Spec-Driven Development**.

---

# 7. Spec Kit debería ser protagonista

Como [GitHub Spec Kit](https://github.com/github/spec-kit?utm_source=chatgpt.com) es el preferido del profesor, yo usaría ese.

La idea es que el repositorio tenga una especificación suficientemente sólida del producto antes de empezar a generar indiscriminadamente.

Conceptualmente:

```text
Idea
 ↓
Constitution
 ↓
Specify
 ↓
Plan
 ↓
Tasks
 ↓
Implement
 ↓
Tests
 ↓
PR
 ↓
Deploy
```

Y establecería en la **constitution** reglas que la IA no pueda saltarse:

```text
I. Todo comportamiento debe originarse
   en una especificación.

II. Toda regla de negocio debe tener
    pruebas automatizadas.

III. Backend y frontend deben respetar
     contratos definidos.

IV. Ninguna HU se considera terminada
    si rompe pruebas existentes.

V. Los cambios de esquema requieren
   migraciones.

VI. No almacenar secretos en código.

VII. Todo código generado por IA debe
     cumplir los mismos criterios de calidad.

VIII. Una HU debe poder desplegarse
      independientemente sin romper
      funcionalidades existentes.
```

Esto les va a servir muchísimo en la demostración.

---

# 8. Arquitectura

No cometería el error de meter microservicios por parecer sofisticados.

Para cinco personas y pocos días:

```text
                   ┌───────────────┐
                   │   Frontend    │
                   │ React/Next.js │
                   └───────┬───────┘
                           │
                         HTTPS
                           │
                   ┌───────▼───────┐
                   │     API       │
                   │    Backend    │
                   └───────┬───────┘
                           │
                    ┌──────▼──────┐
                    │ PostgreSQL  │
                    └─────────────┘
```

**Monolito modular.**

Internamente:

```text
League
Team
Player
Match
Statistics
```

Eso es suficiente separación.

---

# 9. Stack

Teniendo en cuenta la velocidad que necesitan, yo usaría algo como:

### Frontend

**React + TypeScript**

o Next.js si el equipo ya lo domina.

### Backend

**FastAPI + Python**

si quieren maximizar velocidad de desarrollo.

Alternativamente Spring Boot si quieren demostrar Java empresarial, pero para una implementación SDD en vivo de **5–10 minutos**, FastAPI les da una ventaja importante.

### Base de datos

**PostgreSQL**

### ORM

SQLAlchemy.

### Testing

Backend:

```text
pytest
```

Frontend:

```text
Vitest
```

E2E, solamente algunos caminos críticos:

```text
Playwright
```

No intentaría tener 150 E2E.

---

# 10. DevOps

Aquí también pueden hacer algo muy bonito.

```text
Developer
    │
    ↓
Feature branch
    │
    ↓
Pull Request
    │
    ↓
┌─────────────────┐
│ CI              │
│                 │
│ Lint            │
│ Unit tests      │
│ Integration     │
│ Security checks │
│ Build           │
└────────┬────────┘
         │
         ✓
         ↓
       Merge
         │
         ↓
      Deploy
```

Eso conecta perfectamente con el requisito del profesor.

Para hosting pueden evaluar [Vercel](https://vercel.com/?utm_source=chatgpt.com) para frontend y [Railway](https://railway.com/?utm_source=chatgpt.com) u otra alternativa con PostgreSQL/backend según los límites gratuitos que encuentren disponibles al momento de desplegar.

---

# 11. Ciberseguridad

No la dejen para poner una diapositiva al final.

Incorpórenla a las especificaciones.

Por ejemplo:

* Validación de payloads.
* Sanitización de entradas.
* Manejo adecuado de errores.
* Variables de entorno para secretos.
* CORS restringido.
* Dependencias escaneadas.
* SQL parametrizado/ORM.
* Autorización para operaciones administrativas si implementan usuarios.
* No devolver stack traces al cliente.
* Rate limiting, solo si tienen tiempo.

Además pueden integrar análisis estático/dependencias en CI.

---

# 12. Lo más importante: prepararse para las 2 HU sorpresa

Esta es probablemente **la parte que más debería influir en su diseño**.

El profesor puede llegar y decir:

> "Ahora quiero registrar tarjetas amarillas y rojas."

Perfecto.

Ya existe:

```text
MatchEvent
```

Añaden:

```text
YELLOW_CARD
RED_CARD
```

Nueva spec → plan → tasks → tests → implementación.

O:

> "Quiero mostrar el goleador de la liga."

Ya existen:

```text
Player
Match
Goal
```

Solo agregan el cálculo.

O:

> "Quiero que una victoria ahora pueda valer una cantidad configurable de puntos."

Si hicieron esto mal:

```python
points += 3
```

por veinte partes del sistema, sufren.

Si especificaron correctamente el dominio:

```text
ScoringRules
 ├── winPoints
 ├── drawPoints
 └── lossPoints
```

el cambio es manejable.

---

# 13. Diseñaría "puntos de extensión"

Sin implementar funcionalidades que nadie pidió, dejen el modelo preparado conceptualmente para crecer.

Por ejemplo:

```text
MatchEvent
 ├── GOAL
 └── ...
```

en vez de hacer una tabla exclusivamente llamada:

```text
Goal
```

Entonces mañana pueden aparecer:

```text
GOAL
YELLOW_CARD
RED_CARD
SUBSTITUTION
```

Esto les ayudará muchísimo durante la demo.

---

# 14. ¿Cómo repartiría cinco personas?

No haría:

> Persona 1 frontend
> Persona 2 backend
> Persona 3 base de datos...

Porque el profesor explícitamente quiere que **cada integrante pueda ejecutar el motor SDD desde su máquina**.

Mejor que todos sepan completar vertical slices.

Por ejemplo:

```text
                    LEAGUEFLOW

       ┌───────────────────────────────┐
       │       Shared foundation       │
       └───────────────────────────────┘

 Persona 1        Persona 2       Persona 3
 League/Teams     Players         Matches

 Persona 4                       Persona 5
 Standings                       Statistics
```

Pero cada uno debe poder tocar:

```text
Spec
 ↓
Backend
 ↓
DB
 ↓
Frontend
 ↓
Tests
```

cuando su historia lo requiera.

Eso los prepara mucho mejor para la asignación aleatoria del profesor.

---

# 15. ¿Dónde entra la IA?

Aquí hay que diferenciar dos cosas.

**IA como desarrollador asistente**

Este debería ser el centro del experimento:

```text
SPEC
 ↓
IA interpreta requisitos
 ↓
genera plan
 ↓
genera tasks
 ↓
implementa
 ↓
ejecuta tests
 ↓
corrige
```

Pueden usar [GitHub Copilot](https://github.com/features/copilot?utm_source=chatgpt.com) como agente junto con Spec Kit.

Y luego medir qué ocurrió.

**IA dentro de LeagueFlow**

Es opcional.

Si quieren una funcionalidad visible de IA, haría solo una:

### Match Insights

Al terminar un partido:

```text
EAFIT 3 - 1 CES

Posesión       58%    42%
Remates        14      8
Al arco         7      3
```

IA:

> EAFIT controló gran parte del encuentro y generó más oportunidades ofensivas...

Pero **no la pondría dentro de las 10 HU fundamentales**. Primero aseguren el SDD.

---

# 16. El experimento SDD

Aquí pueden sacar una presentación final muy buena.

Registren datos desde el primer día.

Para cada HU:

| Métrica                | Registrar |
| ---------------------- | --------- |
| Tiempo especificación  | minutos   |
| Tiempo implementación  | minutos   |
| Tokens/uso IA          | costo     |
| Tests generados        | cantidad  |
| Tests aprobados        | cantidad  |
| Defectos encontrados   | cantidad  |
| Retrabajo              | minutos   |
| Tiempo total           | minutos   |
| Intervenciones humanas | cantidad  |

Y durante la demo:

**HU sorpresa #11**

```text
Spec          1:42
Plan          0:36
Implement     3:21
Tests         1:08
Deploy        1:37
──────────────────
TOTAL         8:24
```

Eso sería una evidencia bastante potente del SDD.

---

# 17. Caso de negocio

No intenten demostrar:

> "SDD es 73% mejor."

si no tienen datos para respaldarlo.

Planteen un **caso sintético con supuestos explícitos**.

Por ejemplo:

### Desarrollo tradicional

```text
Analizar requerimiento
Diseñar
Implementar
Crear tests
Revisar
Corregir
Deploy
```

Supongamos:

**4 horas/HU**

### Prompt-driven

```text
Prompt
Implementación IA
Correcciones
Tests
Deploy
```

Supongamos:

**2 horas/HU**

### SDD

```text
Specify
Plan
Tasks
Implement
Tests
Deploy
```

Supongamos:

**1.25 horas/HU**

````

Luego:

```text
20 HU × costo/hora
````

y comparan.

Pero separen:

**CAPEX / inversión inicial**

Configuración del repositorio, CI/CD, arquitectura, Spec Kit, constitution.

de:

**OPEX**

Desarrollo incremental, infraestructura, IA, mantenimiento.

La hipótesis interesante probablemente será que SDD tiene **mayor costo inicial de estructuración**, pero disminuye el costo marginal de cambios posteriores.

---

# 18. Qué NO construiría

Para que lleguen bien al **22 de agosto**, pondría una frontera muy clara.

No hagan todavía:

❌ apuestas
❌ streaming
❌ chat
❌ aplicación móvil
❌ múltiples deportes
❌ microservicios
❌ notificaciones push
❌ pagos
❌ predicciones con ML
❌ mapas
❌ tracking GPS
❌ WebSockets salvo que realmente sobren horas

Primero:

> **Una liga de fútbol, extremadamente bien hecha.**

---

# 19. La narrativa del proyecto

La presentación no debería empezar:

> "Hicimos una aplicación para gestionar torneos."

Yo la estructuraría alrededor de esta pregunta:

### **¿Podemos construir y evolucionar software de calidad en minutos cuando la IA trabaja a partir de especificaciones rigurosas?**

Y LeagueFlow es **el caso experimental**.

Eso cambia completamente cómo se percibe el trabajo.

El profesor no está evaluando principalmente si hicieron el próximo Genius Sports. Está evaluando si pueden demostrar:

**especificación → generación → implementación → calidad → integración → despliegue → evolución.**

LeagueFlow les da un dominio excelente porque una nueva especificación puede afectar **frontend + backend + base de datos + reglas + tests** y aun así ser suficientemente pequeña para intentar desarrollarla en vivo en 5–10 minutos.

Por eso creo que **la elección que hicieron es bastante adecuada para esta entrega**. Ahora el siguiente paso importante sería **cerrar las 10 HU exactas y diseñar la arquitectura pensando en posibles HU #11 y #12 sorpresa antes de escribir código**. Ahí se pueden ganar o perder la demostración.
