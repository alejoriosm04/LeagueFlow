/**
 * Cliente HTTP de jugadores — specs/004-registrar-jugadores/contracts/players.openapi.yaml.
 *
 * Los tipos se derivan del contrato (Principio III). La sesión y el envelope
 * de error los gestiona services/apiClient.ts.
 */

import { apiClient } from '../../services/apiClient';

export interface Player {
  id: string;
  team_id: string;
  name: string;
  number: number | null;
  position: string | null;
  status: 'active' | 'inactive';
  created_by: string;
  created_at: string;
}

export interface PaginatedPlayers {
  items: Player[];
  page: number;
  page_size: number;
  total: number;
}

export interface CreatePlayerInput {
  name: string;
  number?: number | null;
  position?: string | null;
}

export const playersApi = {
  listar: (teamId: string, includeInactive = false, page = 1, pageSize = 20) =>
    apiClient.get<PaginatedPlayers>(
      `/teams/${teamId}/players?include_inactive=${includeInactive}&page=${page}&page_size=${pageSize}`,
    ),
  crear: (teamId: string, datos: CreatePlayerInput) =>
    apiClient.post<Player>(`/teams/${teamId}/players`, datos),
  obtener: (playerId: string) => apiClient.get<Player>(`/players/${playerId}`),
};
