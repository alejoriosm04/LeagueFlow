/**
 * Cliente HTTP de auditoría — specs/016-auditoria/contracts/audit.openapi.yaml.
 *
 * Los tipos se derivan del contrato (Principio III). La sesión y el envelope
 * de error los gestiona services/apiClient.ts.
 */

import { apiClient } from '../../services/apiClient';

export interface AuditLogEntry {
  id: string;
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  path: string;
  status_code: number;
  actor_id: string | null;
  actor_username: string | null;
  created_at: string;
}

export interface PaginatedAuditLog {
  items: AuditLogEntry[];
  page: number;
  page_size: number;
  total: number;
}

export const auditApi = {
  listar: (page = 1, pageSize = 20) =>
    apiClient.get<PaginatedAuditLog>(`/admin/audit-log?page=${page}&page_size=${pageSize}`),
};
