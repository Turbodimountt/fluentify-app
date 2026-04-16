import { useState } from 'react'
import './Login.css'

export default function Login({ onLogin, onRegister }) {
  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isRegister) {
        await onRegister(email, password, name)
      } else {
        await onLogin(email, password)
      }
    } catch (err) {
      setError(err.message || 'Error de autenticación')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-hero">
        <div className="hero-content animate-slide-up">
          <div className="hero-logo">🌍</div>
          <h1 className="hero-title">Fluentify</h1>
          <p className="hero-subtitle">Aprende idiomas con inteligencia artificial</p>
          <div className="hero-features">
            <div className="hero-feature">
              <span className="feature-icon">💬</span>
              <span>Conversaciones con IA</span>
            </div>
            <div className="hero-feature">
              <span className="feature-icon">🎭</span>
              <span>Roleplay Profesional</span>
            </div>
            <div className="hero-feature">
              <span className="feature-icon">🤫</span>
              <span>Modo Susurro</span>
            </div>
            <div className="hero-feature">
              <span className="feature-icon">✍️</span>
              <span>Escritura Manual</span>
            </div>
          </div>
        </div>
      </div>

      <div className="login-form-container">
        <form className="login-form glass-card animate-fade-in" onSubmit={handleSubmit}>
          <h2 className="form-title">
            {isRegister ? '🚀 Crear Cuenta' : '👋 Bienvenido de nuevo'}
          </h2>
          <p className="form-subtitle">
            {isRegister ? 'Comienza tu viaje lingüístico' : 'Continúa tu aprendizaje'}
          </p>

          {error && <div className="form-error">{error}</div>}

          {isRegister && (
            <div className="input-group">
              <label htmlFor="name">Nombre</label>
              <input
                id="name"
                className="input"
                type="text"
                placeholder="Tu nombre"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
          )}

          <div className="input-group">
            <label htmlFor="email">Correo electrónico</label>
            <input
              id="email"
              className="input"
              type="email"
              placeholder="tu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
          </div>

          <button className="btn btn-primary btn-lg" type="submit" disabled={loading} style={{ width: '100%' }}>
            {loading ? '⏳ Cargando...' : isRegister ? '🚀 Registrarse' : '🔑 Iniciar Sesión'}
          </button>

          <div className="form-switch">
            <span>{isRegister ? '¿Ya tienes cuenta?' : '¿No tienes cuenta?'}</span>
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => { setIsRegister(!isRegister); setError(''); }}>
              {isRegister ? 'Iniciar Sesión' : 'Registrarse'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
