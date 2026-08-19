import { defineConfig } from '@playwright/test';

/**
 * E2E limitado al camino crítico único:
 *   crear liga -> registrar equipo -> registrar partido -> ver clasificación
 *
 * research.md §5: deliberadamente NO una suite extensa. El test todavía no
 * existe porque sus pasos viven en specs/002, 003, 005 y 008, aún sin
 * implementar. Este archivo deja la configuración lista para cuando existan.
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:5173',
    trace: 'on-first-retry',
  },
});
