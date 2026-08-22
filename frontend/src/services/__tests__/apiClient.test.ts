import { beforeEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '../apiClient';

describe('apiClient.download', () => {
  beforeEach(() => vi.restoreAllMocks());

  it('conserva bytes, blob y filename del servidor', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(new Uint8Array([0xef, 0xbb, 0xbf, 65]), {
      status: 200,
      headers: { 'Content-Type': 'text/csv; charset=utf-8', 'Content-Disposition': 'attachment; filename="liga.csv"' },
    })));
    const descarga = await apiClient.download('/archivo');
    expect(descarga.filename).toBe('liga.csv');
    expect(descarga.blob.size).toBe(4);
  });

  it('propaga el envelope JSON en errores', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ error: { code: 'validation_error', message: 'Solo CSV.', field: 'format' } }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    })));
    await expect(apiClient.download('/archivo')).rejects.toMatchObject({ code: 'validation_error', status: 400 });
  });
});
