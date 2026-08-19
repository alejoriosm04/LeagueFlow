# Tests end-to-end

Vacío a propósito. El único camino crítico definido (`research.md` §5) es
**crear liga → registrar equipo → registrar partido → ver clasificación**, y
sus pasos dependen de `specs/002`, `003`, `005` y `008`, todavía sin
implementar.

Cuando esas specs estén en `main`, el test va aquí como `camino-critico.spec.ts`.
Escribirlo antes obligaría a mockear justamente lo que debe verificar.
