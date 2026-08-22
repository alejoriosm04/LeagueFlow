# Research: Exportacion de clasificacion y calendario a CSV

**Feature**: `015-exportacion-csv` · **Date**: 2026-08-22

No quedan `NEEDS CLARIFICATION`: stack/dominio vienen de 001 y la spec fija
formato, fuentes, alcance y acceso.

## 1. Endpoints dedicados en backend

**Decision**: `GET /leagues/{leagueId}/standings/export` y
`GET /leagues/{leagueId}/matches/export`, con `format=csv` por defecto.

**Rationale**: garantiza una fuente comun, `Content-Disposition` y validacion.

**Alternatives considered**: CSV solo en React (duplicaria quoting/paginacion)
y negociacion solo por `Accept` (no expresa el rechazo de FR-006).

## 2. Reutilizar servicios, nunca recalcular

**Decision**: usar `StandingsService.obtener_clasificacion`; para calendario,
`MatchService.listar_partidos` con `scheduled` y `finished`; nombres mediante
`TeamService`, y liga mediante `LeagueService`. El orquestador recorre todas
las paginas de cada estado hasta `total`, respetando `page_size <= 100`.

**Rationale**: conserva reglas/errores de 007/008. `exports` no importa ORM ni
el calculador de standings.

**Alternatives considered**: SQL propio (duplica reglas/cruza dominios) y HTTP
interno al mismo monolito (latencia y fallo artificiales).

## 3. Estructura y orden

**Decision**: dos registros de metadatos (`Liga`, `Generado en` UTC), linea
vacia y tabla. Clasificacion: `Pos,Equipo,PJ,G,E,P,GF,GC,GD,Pts`. Calendario:
`Local,Visitante,Fecha,Estado,Marcador`. Primero `scheduled` ascendente estable;
luego `finished` descendente estable, como la vista general de 007.

**Rationale**: los metadatos no alteran filas/columnas de la tabla fuente; un
vacio conserva metadatos y encabezados. El calendario representa programados
y jugados completos, no el filtro visual (personalizacion fuera de alcance).

**Alternatives considered**: repetir metadatos como columnas (cambia la vista),
ponerlos solo en filename (FR-003 pide incluirlos) y exportar todo el enum
(excede el alcance programados/jugados).

## 4. Compatibilidad y seguridad

**Decision**: `csv.writer`, CRLF, UTF-8 con BOM y quoting automatico. Neutralizar
celdas textuales cuyo primer caracter no blanco sea `=`, `+`, `-` o `@` para
evitar formulas. Normalizar filename y agregar fecha UTC.

**Rationale**: preserva comas, comillas, saltos y tildes sin corrupcion ni
inyeccion de formulas.

**Alternatives considered**: concatenacion manual y dependencia externa,
innecesarias/inseguras; UTF-8 sin BOM, menos compatible con hojas de escritorio.

## 5. Respuesta, errores y memoria

**Decision**: `200 text/csv; charset=utf-8`, attachment; liga inexistente
conserva `league_not_found`; formato no CSV produce `400 validation_error`.
Inyectar reloj para tests y generar el archivo completo en memoria.

**Rationale**: el volumen maximo (190 filas) no justifica streaming y permite
pruebas de bytes deterministas.

**Alternatives considered**: `406`, streaming y URL temporal; anaden semantica,
complejidad o almacenamiento no pedidos.
