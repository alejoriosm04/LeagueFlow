import { apiClient } from '../../services/apiClient';

function guardar({ blob, filename }: { blob: Blob; filename: string }) {
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = filename;
  enlace.click();
  URL.revokeObjectURL(url);
}

export const exportsApi = {
  descargarClasificacion: async (leagueId: string) => guardar(await apiClient.download(`/leagues/${leagueId}/standings/export?format=csv`)),
  descargarCalendario: async (leagueId: string) => guardar(await apiClient.download(`/leagues/${leagueId}/matches/export?format=csv`)),
};
