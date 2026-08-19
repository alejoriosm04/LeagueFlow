# LeagueFlow — Frontend

SPA en React + TypeScript + Vite. Consume la API por HTTPS/JSON según
`specs/001-fundacion-y-autenticacion/contracts/conventions.md`.

## Puesta en marcha

```bash
npm install
cp .env.example .env.local   # VITE_API_URL=http://localhost:8000
npm run dev
```

App en `http://localhost:5173`. Ese origen debe estar en `ALLOWED_ORIGINS` del
backend o el navegador bloqueará las peticiones por CORS.

## Comandos

```bash
npm run test    # Vitest
npm run lint    # ESLint
npm run build   # tsc + vite build
```

## Sesión

La sesión vive en una cookie `httpOnly`, así que el JavaScript **no puede
leerla**: `AuthContext` pregunta al backend (`GET /auth/me`) quién es el usuario
al montar. Todas las peticiones van con `credentials: 'include'`.

`ProtectedRoute` es una guarda de usabilidad, no de seguridad: la autorización
real la impone el backend en cada endpoint.
