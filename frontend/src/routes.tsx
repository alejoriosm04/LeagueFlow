import { Navigate, Route, Routes, Link } from 'react-router-dom';
import { AuditLogPage } from './features/audit/AuditLogPage';
import { LoginPage } from './features/auth/LoginPage';
import { ProtectedRoute } from './features/auth/ProtectedRoute';
import { Portada } from './features/inicio/Portada';
import { CreateLeagueForm } from './features/leagues/CreateLeagueForm';
import { LeagueDetailPage } from './features/leagues/LeagueDetailPage';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { LeaguesPage } from './features/leagues/LeaguesPage';
import { CreateMatchForm } from './features/matches/CreateMatchForm';
import { MatchesPage } from './features/matches/MatchesPage';
import { MatchDetailPage } from './features/matches/MatchDetailPage';
import { CreatePlayerForm } from './features/players/CreatePlayerForm';
import { PlayersPage } from './features/players/PlayersPage';
import { StandingsPage } from './features/standings/StandingsPage';
import { PlayerStatsPage } from './features/statistics/PlayerStatsPage';
import { TopScorersPage } from './features/statistics/TopScorersPage';
import { CreateTeamForm } from './features/teams/CreateTeamForm';
import { TeamsPage } from './features/teams/TeamsPage';
import { GroupsPage } from './features/groups/GroupsPage';
import { GroupForm } from './features/groups/GroupForm';
import { TituloDePantalla } from './components';

function SoloOrganizador() {
  // FR-027: cada pantalla declara su propio título; un <h2> suelto dejaba
  // /admin sin encabezado principal y saltando un nivel de la jerarquía.
  return (
    <>
      <TituloDePantalla>Administración (solo organizador)</TituloDePantalla>
      <Link to="/admin/audit-log">Ver historial de auditoría</Link>
    </>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Portada />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/leagues" element={<LeaguesPage />} />
      <Route path="/leagues/:id" element={<LeagueDetailPage />} />
      <Route path="/leagues/:id/dashboard" element={<DashboardPage />} />
      <Route path="/leagues/:id/teams" element={<TeamsPage />} />
      <Route
        path="/leagues/:id/teams/new"
        element={
          <ProtectedRoute rol="organizador">
            <CreateTeamForm />
          </ProtectedRoute>
        }
      />
      <Route path="/leagues/:id/groups" element={<GroupsPage />} />
      <Route
        path="/leagues/:id/groups/new"
        element={
          <ProtectedRoute rol="organizador">
            <GroupForm />
          </ProtectedRoute>
        }
      />
      <Route path="/leagues/:id/standings" element={<StandingsPage />} />
      <Route path="/leagues/:id/top-scorers" element={<TopScorersPage />} />
      <Route path="/players/:playerId/statistics" element={<PlayerStatsPage />} />
      <Route path="/leagues/:id/matches" element={<MatchesPage />} />
      <Route path="/matches/:matchId" element={<MatchDetailPage />} />
      <Route
        path="/leagues/:id/matches/new"
        element={
          <ProtectedRoute rol="organizador">
            <CreateMatchForm />
          </ProtectedRoute>
        }
      />
      <Route path="/teams/:teamId/players" element={<PlayersPage />} />
      <Route
        path="/teams/:teamId/players/new"
        element={
          <ProtectedRoute rol="organizador">
            <CreatePlayerForm />
          </ProtectedRoute>
        }
      />
      <Route
        path="/leagues/new"
        element={
          <ProtectedRoute rol="organizador">
            <CreateLeagueForm />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute rol="organizador">
            <SoloOrganizador />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/audit-log"
        element={
          <ProtectedRoute rol="organizador">
            <AuditLogPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
