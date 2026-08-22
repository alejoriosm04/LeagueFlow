/**
 * Cliente HTTP de la ficha disciplinaria — spec 014.
 */

import { apiClient } from '../../services/apiClient';

export interface PlayerDiscipline {
  player_id: string;
  yellow_cards: number;
  red_cards: number;
  suspended: boolean;
}

export const sanctionsApi = {
  ficha: (playerId: string) => apiClient.get<PlayerDiscipline>(`/players/${playerId}/discipline`),
};
