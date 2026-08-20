/**
 * Cliente HTTP de partidos — specs/005-programar-partido/contracts/matches.openapi.yaml.
 */

import { apiClient } from '../../services/apiClient';

export interface Match {
  id: string;
  league_id: string;
  home_team_id: string;
  away_team_id: string;
  scheduled_at: string;
  status: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
  home_score: number | null;
  away_score: number | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedMatches {
  items: Match[];
  page: number;
  page_size: number;
  total: number;
}

export interface CreateMatchInput {
  home_team_id: string;
  away_team_id: string;
  scheduled_at: string;
}

export const matchesApi = {
  listar: (leagueId: string, page = 1, pageSize = 20) =>
    apiClient.get<PaginatedMatches>(
      `/leagues/${leagueId}/matches?page=${page}&page_size=${pageSize}`,
    ),
  crear: (leagueId: string, datos: CreateMatchInput) =>
    apiClient.post<Match>(`/leagues/${leagueId}/matches`, datos),
  obtener: (matchId: string) => apiClient.get<Match>(`/matches/${matchId}`),
};
