/**
 * Cliente HTTP del dashboard general de la liga.
 *
 * Contrato: specs/011-dashboard-liga/contracts/dashboard.openapi.yaml.
 * `Match` y `StandingsRow` se reutilizan tal cual de matches/standings
 * (Principio III): este dashboard no reimplementa esos schemas, solo los
 * compone en una sola respuesta.
 */

import { apiClient } from '../../services/apiClient';
import type { Match } from '../matches/api';
import type { StandingsRow } from '../standings/api';

export interface DashboardSummary {
  league_id: string;
  recent_matches: Match[];
  upcoming_matches: Match[];
  top_standings: StandingsRow[];
}

export const dashboardApi = {
  obtener: (leagueId: string) =>
    apiClient.get<DashboardSummary>(`/leagues/${leagueId}/dashboard`),
};
