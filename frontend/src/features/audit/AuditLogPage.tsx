import { useEffect, useState } from 'react';
import { EstadoCarga, EstadoError, EstadoVacio, Panel, TablaDeDatos, TituloDePantalla } from '../../components';
import type { ColumnaDeTabla } from '../../components';
import { formatearFechaHora } from '../../lib/formato';
import { mensajeDeError } from '../../lib/mensajesDeError';
import { auditApi } from './api';
import type { AuditLogEntry } from './api';

/** FR-004: cuando el actor no es determinable (p. ej. el propio login que crea la sesión). */
const ACTOR_NO_DETERMINABLE = 'Actor no determinable';

const columnas: ReadonlyArray<ColumnaDeTabla<AuditLogEntry>> = [
  { clave: 'Fecha', encabezado: 'Fecha', celda: (f) => formatearFechaHora(f.created_at) },
  { clave: 'Actor', encabezado: 'Actor', celda: (f) => f.actor_username ?? ACTOR_NO_DETERMINABLE },
  { clave: 'Metodo', encabezado: 'Método', celda: (f) => f.method },
  { clave: 'Destino', encabezado: 'Destino', celda: (f) => f.path },
  { clave: 'Resultado', encabezado: 'Resultado', numerica: true, celda: (f) => f.status_code },
];

/** Historial de auditoría — solo organizador (FR-005, FR-006). */
export function AuditLogPage() {
  const [filas, setFilas] = useState<AuditLogEntry[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);
    auditApi
      .listar()
      .then((historial) => {
        if (vigente) setFilas(historial.items);
      })
      .catch((causa) => {
        if (vigente) setError(mensajeDeError(causa));
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });
    return () => {
      vigente = false;
    };
  }, [intento]);

  return (
    <section>
      <TituloDePantalla>Historial de auditoría</TituloDePantalla>
      {cargando && <EstadoCarga recurso="el historial de auditoría" />}
      {error && <EstadoError mensaje={error} onReintentar={() => setIntento((n) => n + 1)} />}
      {!cargando && !error && filas.length === 0 && (
        <EstadoVacio
          titulo="Todavía no hay operaciones registradas."
          descripcion="Cada operación de escritura exitosa (crear una liga, registrar un resultado, etc.) queda aquí automáticamente."
        />
      )}
      {!cargando && !error && filas.length > 0 && (
        <Panel titulo="Operaciones recientes">
          <TablaDeDatos
            columnas={columnas}
            filas={filas}
            claveDeFila={(fila) => fila.id}
            descripcion="Operaciones de escritura exitosas, de la más reciente a la más antigua."
          />
        </Panel>
      )}
    </section>
  );
}
