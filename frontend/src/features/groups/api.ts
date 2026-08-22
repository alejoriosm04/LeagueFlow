/**
 * Cliente HTTP de grupos — specs/013-grupos-divisiones/contracts/groups.openapi.yaml.
 *
 * Los tipos se derivan del contrato (Principio III).
 */

import { apiClient } from '../../services/apiClient';

export interface TeamInGroup {
  team_id: string;
  name: string;
  status: 'active' | 'inactive';
}

export interface Group {
  id: string;
  league_id: string;
  name: string;
  position: number | null;
  created_at: string;
}

export interface GroupWithTeams extends Group {
  teams: TeamInGroup[];
}

export interface GroupList {
  items: GroupWithTeams[];
}

export interface CreateGroupInput {
  name: string;
  position?: number | null;
}

export const groupsApi = {
  listar: (leagueId: string) =>
    apiClient.get<GroupList>(`/leagues/${leagueId}/groups`),
  crear: (leagueId: string, datos: CreateGroupInput) =>
    apiClient.post<Group>(`/leagues/${leagueId}/groups`, datos),
  renombrar: (groupId: string, name: string) =>
    apiClient.patch<Group>(`/groups/${groupId}`, { name }),
  eliminar: (groupId: string) => apiClient.delete<void>(`/groups/${groupId}`),
  asignar: (groupId: string, teamId: string) =>
    apiClient.post<void>(`/groups/${groupId}/teams`, { team_id: teamId }),
  desasignar: (groupId: string, teamId: string) =>
    apiClient.delete<void>(`/groups/${groupId}/teams?team_id=${teamId}`),
};
