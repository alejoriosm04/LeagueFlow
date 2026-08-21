/**
 * Estado de sesión en la cabecera — FR-002.
 * Con sesión: nombre de usuario, rol y salida. Sin sesión: acceso a entrar.
 */

import { Link } from 'react-router-dom';
import { useAuth } from '../../features/auth/AuthContext';
import estilos from './EstadoDeSesion.module.css';

export function EstadoDeSesion() {
  const { usuario, logout, cargando } = useAuth();

  if (cargando) return null;

  if (!usuario) {
    return (
      <div className={`${estilos.contenedor} ${estilos.contenedorSinSesion}`}>
        <Link to="/login" className={estilos.entrar}>
          Iniciar sesión
        </Link>
      </div>
    );
  }

  return (
    <div className={estilos.contenedor}>
      {/* Decorativo: el nombre completo ya está en el texto de al lado, así
          que la inicial no aporta nada a un lector de pantalla. */}
      <span className={estilos.avatar} aria-hidden="true">
        {usuario.username.slice(0, 1).toUpperCase()}
      </span>
      <span className={estilos.usuario}>
        <span className={estilos.nombre}>{usuario.username}</span>
        <span className={estilos.rol}>{usuario.role}</span>
      </span>
      <button type="button" className={estilos.salir} onClick={() => void logout()}>
        Cerrar sesión
      </button>
    </div>
  );
}
