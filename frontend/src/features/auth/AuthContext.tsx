import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { apiClient } from '../../services/apiClient';

export interface Usuario {
  id: string;
  username: string;
  role: 'organizador' | 'operador';
  status: string;
}

interface AuthContextValue {
  usuario: Usuario | null;
  cargando: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [cargando, setCargando] = useState(true);

  // La sesión vive en una cookie httpOnly: el frontend no puede leerla, así
  // que pregunta al servidor quién es al arrancar.
  useEffect(() => {
    apiClient
      .get<{ user: Usuario | null }>('/auth/me')
      .then((r) => setUsuario(r.user))
      .catch(() => setUsuario(null))
      .finally(() => setCargando(false));
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const r = await apiClient.post<{ user: Usuario }>('/auth/login', { username, password });
    setUsuario(r.user);
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      setUsuario(null);
    }
  }, []);

  const valor = useMemo(
    () => ({ usuario, cargando, login, logout }),
    [usuario, cargando, login, logout],
  );

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth debe usarse dentro de <AuthProvider>');
  return ctx;
}
