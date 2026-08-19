import { Navigate, Route, Routes } from 'react-router-dom';
import { LoginPage } from './features/auth/LoginPage';
import { ProtectedRoute } from './features/auth/ProtectedRoute';
import { useAuth } from './features/auth/AuthContext';

function Inicio() {
  const { usuario } = useAuth();
  return (
    <section>
      <h1>LeagueFlow</h1>
      <p>Gestión y analítica de ligas deportivas amateur.</p>
      {usuario ? (
        <p>
          Sesión iniciada como <strong>{usuario.username}</strong>.
        </p>
      ) : (
        <p>Las consultas son públicas; para registrar información hay que iniciar sesión.</p>
      )}
    </section>
  );
}

function SoloOrganizador() {
  return <h2>Administración (solo organizador)</h2>;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Inicio />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute rol="organizador">
            <SoloOrganizador />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
