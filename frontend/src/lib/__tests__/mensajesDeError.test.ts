/**
 * Catálogo de mensajes de error — FR-015, SC-003.
 * spec 012-identidad-visual, Historia 3.
 */

import { describe, expect, it } from 'vitest';
import { ApiError } from '../../services/apiClient';
import {
  MENSAJE_GENERICO,
  campoDelError,
  codigosConocidos,
  mensajeDeError,
} from '../mensajesDeError';

function errorConCodigo(code: string, message = 'TEXTO CRUDO DEL SERVIDOR', field: string | null = null) {
  return new ApiError(409, { code, message, field });
}

describe('mensajeDeError', () => {
  it('traduce un código conocido a su mensaje en español', () => {
    expect(mensajeDeError(errorConCodigo('team_name_duplicate'))).toBe(
      'Ya hay un equipo con ese nombre en esta liga.',
    );
  });

  it('el bloqueo de login tiene mensaje propio, distinto del de credenciales (specs/017)', () => {
    // Assumption "Aviso en la interfaz" de specs/017: el usuario legítimo debe
    // entender por qué su contraseña correcta no funciona, así que el mensaje
    // no puede ser ni el genérico ni el de credenciales inválidas.
    const bloqueado = mensajeDeError(errorConCodigo('login_locked'));
    expect(bloqueado).not.toBe(MENSAJE_GENERICO);
    expect(bloqueado).not.toBe(mensajeDeError(errorConCodigo('invalid_credentials')));
    // Cualitativo, sin el número exacto de minutos (research.md §10).
    expect(bloqueado).not.toMatch(/\d/);
  });

  it('usa el genérico con un código desconocido', () => {
    expect(mensajeDeError(errorConCodigo('codigo_que_no_existe'))).toBe(MENSAJE_GENERICO);
  });

  it('usa el genérico con un fallo de red', () => {
    expect(mensajeDeError(new TypeError('Failed to fetch'))).toBe(MENSAJE_GENERICO);
  });

  it('usa el genérico con cualquier cosa que no sea un error de la API', () => {
    expect(mensajeDeError(null)).toBe(MENSAJE_GENERICO);
    expect(mensajeDeError('vaya')).toBe(MENSAJE_GENERICO);
  });

  it('NUNCA devuelve el message del servidor (SC-003)', () => {
    for (const code of [...codigosConocidos, 'codigo_que_no_existe']) {
      const salida = mensajeDeError(errorConCodigo(code));
      expect(salida).not.toContain('TEXTO CRUDO DEL SERVIDOR');
    }
  });

  it('NUNCA devuelve el código crudo (SC-003)', () => {
    for (const code of [...codigosConocidos, 'codigo_que_no_existe']) {
      expect(mensajeDeError(errorConCodigo(code))).not.toContain(code);
    }
  });

  it('todos los mensajes del catálogo están en español y acabados', () => {
    for (const code of codigosConocidos) {
      const salida = mensajeDeError(errorConCodigo(code));
      expect(salida.length).toBeGreaterThan(10);
      expect(salida).toMatch(/[.!?]$/);
      // Sin restos técnicos: nada de snake_case ni de códigos de estado.
      expect(salida).not.toMatch(/_[a-z]/);
    }
  });
});

describe('campoDelError', () => {
  it('devuelve el campo cuando el envelope lo informa', () => {
    expect(campoDelError(errorConCodigo('team_name_duplicate', 'x', 'name'))).toBe('name');
  });

  it('devuelve null cuando no hay campo', () => {
    expect(campoDelError(errorConCodigo('league_not_found'))).toBeNull();
    expect(campoDelError(new Error('x'))).toBeNull();
  });
});
