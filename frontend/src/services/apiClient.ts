/**
 * Cliente HTTP base.
 *
 * Contrato: specs/001-fundacion-y-autenticacion/contracts/conventions.md
 * - `credentials: 'include'` es obligatorio: la sesión viaja en una cookie
 *   httpOnly cross-domain (Vercel -> Railway), no en un header.
 * - Todo error 4xx/5xx llega con el envelope {error:{code,message,field}}.
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export interface ApiErrorBody {
  code: string;
  message: string;
  field: string | null;
}

export class ApiError extends Error {
  readonly code: string;
  readonly field: string | null;
  readonly status: number;

  constructor(status: number, body: ApiErrorBody) {
    super(body.message);
    this.name = 'ApiError';
    this.status = status;
    this.code = body.code;
    this.field = body.field;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const respuesta = await fetch(`${BASE_URL}/api/v1${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers ?? {}),
    },
  });

  if (respuesta.status === 204) return undefined as T;

  const texto = await respuesta.text();
  const datos = texto ? JSON.parse(texto) : null;

  if (!respuesta.ok) {
    const cuerpo: ApiErrorBody = datos?.error ?? {
      code: 'unknown_error',
      message: 'No fue posible completar la operación.',
      field: null,
    };
    throw new ApiError(respuesta.status, cuerpo);
  }

  return datos as T;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path, { method: 'GET' }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};
