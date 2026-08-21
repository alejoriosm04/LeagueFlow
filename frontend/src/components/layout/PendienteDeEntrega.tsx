/**
 * Sección declarada en el mockup pero aún no entregada — FR-006.
 *
 * No es una pantalla de negocio nueva: no consulta datos ni introduce reglas.
 * Existe para que Dashboard y Estadísticas no conduzcan a un destino roto.
 */

import estilos from './PendienteDeEntrega.module.css';

interface PendienteDeEntregaProps {
  seccion: string;
  spec: string;
}

export function PendienteDeEntrega({ seccion, spec }: PendienteDeEntregaProps) {
  return (
    <section className={estilos.contenedor}>
      <h1 className={estilos.titulo}>{seccion}</h1>
      <p className={estilos.texto}>
        Esta sección aún no está disponible. Llegará con la historia{' '}
        <strong>{spec}</strong>. Mientras tanto puedes usar el resto de secciones
        desde la navegación.
      </p>
    </section>
  );
}
