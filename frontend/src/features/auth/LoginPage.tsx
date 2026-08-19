import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApiError } from '../../services/apiClient';
import { useAuth } from './AuthContext';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      // El mensaje viene del envelope del backend; es genérico a propósito y
      // no revela si el usuario existe (FR-010).
      setError(err instanceof ApiError ? err.message : 'No fue posible iniciar sesión.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={onSubmit} style={{ maxWidth: 360 }}>
      <h1>Iniciar sesión</h1>
      <label htmlFor="username">Usuario</label>
      <input
        id="username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        autoComplete="username"
        required
      />
      <label htmlFor="password">Contraseña</label>
      <input
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        autoComplete="current-password"
        required
      />
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={enviando}>
        {enviando ? 'Entrando…' : 'Entrar'}
      </button>
    </form>
  );
}
