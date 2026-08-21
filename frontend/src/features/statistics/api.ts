/**
 * Cliente HTTP de estadísticas de jugador.
 *
 * Contrato: specs/010-alineaciones-estadisticas/contracts/lineups-statistics.openapi.yaml.
 * Recurso de solo lectura: no existe operación de escritura que exponer (FR-008).
 */

import { apiClient } from '../../services/apiClient';

export interface PlayerStatistics {
  player_id: string;
  player_name: string;
  team_id: string;
  team_name: string;
  goals: number;
  matches_played: number;
}

export interface TopScorerRow extends PlayerStatistics {
  rank: number;
  is_top_scorer: boolean;
}

export interface TopScorers {
  items: TopScorerRow[];
}

export const statisticsApi = {
  ficha: (playerId: string) => apiClient.get<PlayerStatistics>(`/players/${playerId}/statistics`),
  topScorers: (leagueId: string) =>
    apiClient.get<TopScorers>(`/leagues/${leagueId}/top-scorers`),
};
