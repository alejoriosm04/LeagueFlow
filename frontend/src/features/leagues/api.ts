/**
 * Cliente HTTP de ligas — specs/002-crear-liga/contracts/leagues.openapi.yaml.
 *
 * Los tipos se derivan del contrato (Principio III). La sesión y el envelope
 * de error los gestiona services/apiClient.ts.
 */

import { apiClient } from '../../services/apiClient';

export interface League {
  id: string;
  name: string;
  season: string;
  description: string | null;
  created_by: string;
  created_at: string;
}

export interface PaginatedLeagues {
  items: League[];
  page: number;
  page_size: number;
  total: number;
}

export interface CreateLeagueInput {
  name: string;
  season: string;
  description?: string | null;
}

export const leaguesApi = {
  listar: (page = 1, pageSize = 20) =>
    apiClient.get<PaginatedLeagues>(`/leagues?page=${page}&page_size=${pageSize}`),
  crear: (datos: CreateLeagueInput) => apiClient.post<League>('/leagues', datos),
  obtener: (id: string) => apiClient.get<League>(`/leagues/${id}`),
};
