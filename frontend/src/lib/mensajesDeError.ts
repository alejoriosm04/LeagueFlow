/**
 * Catálogo de mensajes de error en español — FR-015, SC-003.
 * Contrato: specs/012-identidad-visual/contracts/ui-contracts.md §4
 *
 * Traduce el `code` del envelope {error:{code,message,field}} definido en
 * specs/001-fundacion-y-autenticacion/contracts/conventions.md.
 *
 * NUNCA se devuelve el `message` del servidor ni el `code` crudo: los códigos
 * desconocidos y los fallos de red caen en el mensaje genérico. Es lo que hace
 * verificable SC-003 ("0 casos con detalles técnicos internos") sin depender
 * de que cada endpoint responda ya traducido, y es coherente con el estándar
 * "sin stack traces al cliente" de la constitución.
 */

import { ApiError } from '../services/apiClient';

export const MENSAJE_GENERICO = 'No fue posible completar la operación. Inténtalo de nuevo.';

const mensajes: Record<string, string> = {
  // Sesión y permisos (specs/001)
  not_authenticated: 'Tu sesión no está activa. Inicia sesión para continuar.',
  invalid_credentials: 'El usuario o la contraseña no son correctos.',
  insufficient_role: 'Tu rol no permite realizar esta acción.',
  username_already_exists: 'Ese nombre de usuario ya está en uso.',

  // Ligas (specs/002)
  league_not_found: 'No encontramos la liga que buscas.',
  league_already_exists: 'Ya existe una liga con ese nombre en esa temporada.',

  // Equipos (specs/003)
  team_not_found: 'No encontramos el equipo que buscas.',
  team_name_duplicate: 'Ya hay un equipo con ese nombre en esta liga.',

  // Jugadores (specs/004)
  player_not_found: 'No encontramos al jugador que buscas.',
  player_number_duplicate: 'Ese dorsal ya está asignado a otro jugador del equipo.',

  // Partidos (specs/005, 006)
  match_not_found: 'No encontramos el partido que buscas.',
  match_same_team: 'Un equipo no puede jugar contra sí mismo.',
  match_not_scheduled: 'El partido no está programado, así que no admite esta operación.',
  match_not_playable: 'Solo un partido en curso o finalizado admite esta operación.',
  match_not_finished: 'El partido todavía no ha finalizado.',
  result_already_recorded: 'Este partido ya tiene un resultado registrado.',

  // Correcciones de resultado (specs/006)
  correction_not_found: 'No encontramos la solicitud de corrección.',
  correction_pending_exists: 'Ya hay una solicitud de corrección pendiente para este partido.',
  correction_self_decision: 'No puedes decidir sobre una corrección que solicitaste tú.',
  correction_already_decided: 'Esta solicitud de corrección ya fue decidida.',

  // Goles y alineaciones (specs/009, 010)
  player_not_in_match: 'El jugador no pertenece a ninguno de los dos equipos del partido.',
  player_not_in_lineup: 'El jugador no figura en la alineación registrada del partido.',

  // Grupos (specs/013)
  group_not_found: 'No encontramos el grupo que buscas.',
  group_name_duplicate: 'Ya hay un grupo con ese nombre en esta liga.',
  team_not_found_in_league: 'El equipo no pertenece a la liga del grupo.',
  team_already_in_group: 'El equipo ya pertenece a un grupo de esta liga.',
  team_inactive: 'El equipo está inactivo y no puede asignarse a un grupo.',

  // Validación genérica
  validation_error: 'Revisa los datos introducidos: hay algún valor que no es válido.',
};

/**
 * Mensaje en español para cualquier error, venga de donde venga.
 * Un `code` desconocido, un fallo de red o un error inesperado devuelven el
 * mensaje genérico: nunca texto del servidor.
 */
export function mensajeDeError(error: unknown): string {
  if (error instanceof ApiError) {
    return mensajes[error.code] ?? MENSAJE_GENERICO;
  }
  return MENSAJE_GENERICO;
}

/**
 * Campo al que apunta el error, cuando el envelope lo informa (FR-017).
 * Permite pintar el mensaje junto al campo afectado en vez de como error
 * general del formulario.
 */
export function campoDelError(error: unknown): string | null {
  return error instanceof ApiError ? error.field : null;
}

/** Códigos con traducción propia. Expuesto para la prueba del catálogo. */
export const codigosConocidos = Object.keys(mensajes);
