/**
 * Cliente HTTP de partidos — specs/005-programar-partido/contracts/matches.openapi.yaml.
 */

import { apiClient } from '../../services/apiClient';

export type MatchStatus = 'scheduled' | 'in_progress' | 'finished' | 'cancelled';

export interface Match {
  id: string;
  league_id: string;
  home_team_id: string;
  away_team_id: string;
  scheduled_at: string;
  status: MatchStatus;
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

export interface ScoreInput {
  home_score: number;
  away_score: number;
}

export interface CreateCorrectionInput extends ScoreInput {
  reason: string;
}

export interface DecisionInput {
  decision: 'approved' | 'rejected';
  decision_reason?: string;
}

export interface ResultCorrection {
  id: string;
  match_id: string;
  proposed_home_score: number;
  proposed_away_score: number;
  previous_home_score: number;
  previous_away_score: number;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  requested_by: string;
  decided_by: string | null;
  decision_reason: string | null;
  created_at: string;
  decided_at: string | null;
}

export interface PaginatedCorrections {
  items: ResultCorrection[];
  page: number;
  page_size: number;
  total: number;
}

export const matchesApi = {
  listar: (leagueId: string, page = 1, pageSize = 20, status?: MatchStatus) =>
    apiClient.get<PaginatedMatches>(
      `/leagues/${leagueId}/matches?page=${page}&page_size=${pageSize}${status ? `&status=${status}` : ''}`,
    ),
  listarTodos: async (leagueId: string, status: MatchStatus): Promise<Match[]> => {
    const pageSize = 100;
    const primera = await apiClient.get<PaginatedMatches>(
      `/leagues/${leagueId}/matches?page=1&page_size=${pageSize}&status=${status}`,
    );
    const paginas = Math.ceil(primera.total / pageSize);
    if (paginas <= 1) return primera.items;
    const restantes = await Promise.all(
      Array.from({ length: paginas - 1 }, (_, index) =>
        apiClient.get<PaginatedMatches>(
          `/leagues/${leagueId}/matches?page=${index + 2}&page_size=${pageSize}&status=${status}`,
        ),
      ),
    );
    return [primera, ...restantes].flatMap((pagina) => pagina.items);
  },
  crear: (leagueId: string, datos: CreateMatchInput) =>
    apiClient.post<Match>(`/leagues/${leagueId}/matches`, datos),
  obtener: (matchId: string) => apiClient.get<Match>(`/matches/${matchId}`),
  registrarResultado: (matchId: string, datos: ScoreInput) =>
    apiClient.put<Match>(`/matches/${matchId}/result`, datos),
  solicitarCorreccion: (matchId: string, datos: CreateCorrectionInput) =>
    apiClient.post<ResultCorrection>(`/matches/${matchId}/result-corrections`, datos),
  listarCorrecciones: (matchId: string, page = 1, pageSize = 20) =>
    apiClient.get<PaginatedCorrections>(
      `/matches/${matchId}/result-corrections?page=${page}&page_size=${pageSize}`,
    ),
  decidirCorreccion: (correctionId: string, datos: DecisionInput) =>
    apiClient.post<ResultCorrection>(`/result-corrections/${correctionId}/decision`, datos),
};
