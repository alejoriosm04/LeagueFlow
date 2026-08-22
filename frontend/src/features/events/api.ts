/**
 * Cliente HTTP de los eventos de partido.
 *
 * Contrato: specs/009-registrar-goles/contracts/events.openapi.yaml.
 * El equipo no se envía: lo deriva el servidor a partir del jugador.
 */

import { apiClient } from '../../services/apiClient';

export type EventType = 'GOAL' | 'YELLOW_CARD' | 'RED_CARD';

export interface MatchEvent {
  id: string;
  match_id: string;
  type: EventType;
  player_id: string;
  team_id: string;
  minute: number;
  created_by: string;
  created_at: string;
}

/** Advertencia de FR-005: informa, nunca bloquea. */
export interface EventConsistency {
  home_goals_recorded: number;
  away_goals_recorded: number;
  home_score: number | null;
  away_score: number | null;
  /** null cuando el partido aún no tiene marcador contra el que contrastar. */
  matches_official: boolean | null;
}

export interface MatchEvents {
  items: MatchEvent[];
  consistency: EventConsistency;
}

export interface CreateEventInput {
  player_id: string;
  minute: number;
  type?: EventType;
}

export const eventsApi = {
  listar: (matchId: string) => apiClient.get<MatchEvents>(`/matches/${matchId}/events`),
  registrar: (matchId: string, datos: CreateEventInput) =>
    apiClient.post<MatchEvent>(`/matches/${matchId}/events`, datos),
};
