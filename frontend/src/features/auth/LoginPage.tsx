import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Boton, CampoDeFormulario, EstadoError, TituloDePantalla } from '../../components';
import { campoDelError, mensajeDeError } from '../../lib/mensajesDeError';
import { useAuth } from './AuthContext';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fallo, setFallo] = useState<unknown>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFallo(null);
    setEnviando(true);
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      // El mensaje sale del catálogo en español (FR-015): sigue siendo
      // genérico a propósito y no revela si el usuario existe.
      setFallo(err);
    } finally {
      // Pase lo que pase, el formulario vuelve a estar disponible: el usuario
      // nunca queda atrapado tras un error (FR-018).
      setEnviando(false);
    }
  }

  const mensaje = fallo ? mensajeDeError(fallo) : null;
  const campo = campoDelError(fallo);

  return (
    <form onSubmit={onSubmit} className="lf-formulario">
      <TituloDePantalla>Iniciar sesión</TituloDePantalla>

      <CampoDeFormulario
        id="username"
        etiqueta="Usuario"
        requerido
        error={campo === 'username' ? mensaje : null}
      >
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          required
        />
      </CampoDeFormulario>

      <CampoDeFormulario
        id="password"
        etiqueta="Contraseña"
        requerido
        error={campo === 'password' ? mensaje : null}
      >
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
      </CampoDeFormulario>

      {mensaje && !campo && <EstadoError mensaje={mensaje} />}

      <div className="lf-acciones-formulario">
        <Boton type="submit" enviando={enviando}>
          Entrar
        </Boton>
      </div>
    </form>
  );
}
