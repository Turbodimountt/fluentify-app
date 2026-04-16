import { useState, useEffect } from 'react'
import { api } from '../api'
import './History.css'

export default function History() {
  const [sessions, setSessions] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getSessions(20, 0)
      .then(data => { setSessions(data.sessions || []); setTotal(data.total || 0); })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const modeIcons = { libre: '💬', roleplay: '🎭', susurro: '🤫', writing: '✍️' }
  const modeNames = { libre: 'Libre', roleplay: 'Roleplay', susurro: 'Susurro', writing: 'Escritura' }

  const formatDuration = (s) => {
    const m = Math.floor(s / 60)
    return m > 0 ? `${m} min` : `${s}s`
  }

  const formatDate = (d) => {
    return new Date(d).toLocaleDateString('es', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="history animate-fade-in">
      <h1 className="page-title">📚 Historial de Sesiones</h1>
      <p className="page-subtitle">{total} sesiones en total</p>

      {loading ? (
        <div className="loading-state">Cargando historial...</div>
      ) : sessions.length === 0 ? (
        <div className="empty-state glass-card">
          <span className="empty-icon">📭</span>
          <h3>Sin sesiones aún</h3>
          <p>Comienza a practicar para ver tu historial aquí</p>
        </div>
      ) : (
        <div className="sessions-list">
          {sessions.map((s, i) => (
            <div key={s.id || i} className="session-item glass-card" style={{ animationDelay: `${i * 50}ms` }}>
              <div className="session-icon">{modeIcons[s.session_type] || '💬'}</div>
              <div className="session-info">
                <div className="session-top">
                  <span className="session-mode">{modeNames[s.session_type] || s.session_type}</span>
                  {s.scenario_name && <span className="session-scenario">{s.scenario_name}</span>}
                </div>
                <span className="session-date">{formatDate(s.started_at)}</span>
              </div>
              <div className="session-stats">
                <span className="session-stat">💬 {s.messages_count} turnos</span>
                <span className="session-stat">⚡ {s.xp_earned} XP</span>
                <span className="session-stat">⏱️ {formatDuration(s.duration_seconds)}</span>
                {s.errors_detected > 0 && (
                  <span className="session-stat errors">📝 {s.errors_detected} errores</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
