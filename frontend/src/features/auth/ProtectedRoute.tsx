import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

/**
 * Oculta rutas de escritura a quien no tenga sesión o rol suficiente.
 *
 * Es una guarda de USABILIDAD, no de seguridad: la autorización real la impone
 * el backend en cada endpoint (FR-003, FR-009). Nunca confiar solo en esto.
 */
export function ProtectedRoute({ children, rol }: { children: ReactNode; rol?: string }) {
  const { usuario, cargando } = useAuth();

  if (cargando) return <p>Cargando…</p>;
  if (!usuario) return <Navigate to="/login" replace />;
  if (rol && usuario.role !== rol) return <p role="alert">No tienes permisos para ver esta página.</p>;

  return <>{children}</>;
}
