/**
 * Cliente HTTP de equipos — specs/003-registrar-equipos/contracts/teams.openapi.yaml.
 *
 * Los tipos se derivan del contrato (Principio III). La sesión y el envelope
 * de error los gestiona services/apiClient.ts.
 */

import { apiClient } from '../../services/apiClient';

export interface Team {
  id: string;
  league_id: string;
  name: string;
  crest_url: string | null;
  colors: string | null;
  status: 'active' | 'inactive';
  created_by: string;
  created_at: string;
}

export interface PaginatedTeams {
  items: Team[];
  page: number;
  page_size: number;
  total: number;
}

export interface CreateTeamInput {
  name: string;
  crest_url?: string | null;
  colors?: string | null;
}

export const teamsApi = {
  listar: (leagueId: string, includeInactive = false, page = 1, pageSize = 20) =>
    apiClient.get<PaginatedTeams>(
      `/leagues/${leagueId}/teams?include_inactive=${includeInactive}&page=${page}&page_size=${pageSize}`,
    ),
  crear: (leagueId: string, datos: CreateTeamInput) =>
    apiClient.post<Team>(`/leagues/${leagueId}/teams`, datos),
  obtener: (teamId: string) => apiClient.get<Team>(`/teams/${teamId}`),
};
