import { AppRoutes } from './routes';
import { useAuth } from './features/auth/AuthContext';
import { Link } from 'react-router-dom';

export function App() {
  const { usuario, logout, cargando } = useAuth();

  return (
    <div>
      <header
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '1rem',
          borderBottom: '1px solid #ddd',
        }}
      >
        <Link to="/" style={{ fontWeight: 700, textDecoration: 'none' }}>
          LEAGUEFLOW
        </Link>
        <nav>
          {cargando ? null : usuario ? (
            <span>
              {usuario.username} ({usuario.role}){' '}
              <button onClick={() => void logout()}>Cerrar sesión</button>
            </span>
          ) : (
            <Link to="/login">Iniciar sesión</Link>
          )}
        </nav>
      </header>
      <main style={{ padding: '1rem' }}>
        <AppRoutes />
      </main>
    </div>
  );
}
