/**
 * Cliente HTTP de la clasificación.
 *
 * Contrato: specs/008-consultar-clasificacion/contracts/standings.openapi.yaml.
 * Los tipos se derivan del contrato (Principio III). Es un recurso de solo
 * lectura: no existe operación de escritura que exponer (FR-002).
 */

import { apiClient } from '../../services/apiClient';

export interface StandingsRow {
  position: number;
  team_id: string;
  team_name: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
}

export interface Standings {
  league_id: string;
  items: StandingsRow[];
}

export const standingsApi = {
  obtener: (leagueId: string) => apiClient.get<Standings>(`/leagues/${leagueId}/standings`),
};
