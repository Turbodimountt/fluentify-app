import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import './Dashboard.css'

const MODES = [
  { id: 'libre', icon: '💬', title: 'Modo Libre', desc: 'Conversación abierta con IA', color: '#6C5CE7' },
  { id: 'roleplay', icon: '🎭', title: 'Roleplay', desc: 'Escenarios profesionales inmersivos', color: '#00CEC9' },
  { id: 'susurro', icon: '🤫', title: 'Modo Susurro', desc: 'Práctica de pronunciación sin presión', color: '#FD79A8' },
]

export default function Dashboard({ user }) {
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getStats()
      .then(setStats)
      .catch(() => setStats({
        total_xp: 0, current_streak: 0, max_streak: 0,
        user_level: 'Explorador', sessions_count: 0,
        nodes_mastered: 0, nodes_pending_review: 0,
        total_practice_minutes: 0, error_rate: 0,
      }))
      .finally(() => setLoading(false))
  }, [])

  const startPractice = (mode) => {
    navigate('/practice', { state: { mode } })
  }

  return (
    <div className="dashboard animate-fade-in">
      <header className="dashboard-header">
        <div>
          <h1 className="page-title">
            ¡Hola, {user?.display_name || 'Estudiante'}! 👋
          </h1>
          <p className="page-subtitle">
            {stats?.current_streak > 0
              ? `🔥 Racha de ${stats.current_streak} días — ¡Sigue así!`
              : '¡Comienza tu práctica diaria!'}
          </p>
        </div>
      </header>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card glass-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #6C5CE7, #A29BFE)' }}>⚡</div>
          <div className="stat-content">
            <span className="stat-value">{stats?.total_xp?.toLocaleString() || 0}</span>
            <span className="stat-label">XP Total</span>
          </div>
        </div>
        <div className="stat-card glass-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #FF6B6B, #FD79A8)' }}>🔥</div>
          <div className="stat-content">
            <span className="stat-value">{stats?.current_streak || 0}</span>
            <span className="stat-label">Días de racha</span>
          </div>
        </div>
        <div className="stat-card glass-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #00CEC9, #55EFC4)' }}>🌟</div>
          <div className="stat-content">
            <span className="stat-value">{stats?.nodes_mastered || 0}</span>
            <span className="stat-label">Nodos dominados</span>
          </div>
        </div>
        <div className="stat-card glass-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #FDCB6E, #E17055)' }}>⏱️</div>
          <div className="stat-content">
            <span className="stat-value">{stats?.total_practice_minutes || 0}</span>
            <span className="stat-label">Minutos practicados</span>
          </div>
        </div>
      </div>

      {/* Quick Practice */}
      <section className="section">
        <h2 className="section-title">Comenzar a practicar</h2>
        <div className="modes-grid">
          {MODES.map((mode, i) => (
            <button
              key={mode.id}
              className="mode-card glass-card"
              onClick={() => startPractice(mode.id)}
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="mode-icon-bg" style={{ background: `linear-gradient(135deg, ${mode.color}, ${mode.color}88)` }}>
                <span className="mode-icon">{mode.icon}</span>
              </div>
              <h3 className="mode-title">{mode.title}</h3>
              <p className="mode-desc">{mode.desc}</p>
              <div className="mode-arrow">→</div>
            </button>
          ))}
        </div>
      </section>

      {/* Level Progress */}
      {stats && (
        <section className="section">
          <h2 className="section-title">Tu nivel</h2>
          <div className="level-card glass-card">
            <div className="level-info">
              <span className="level-badge">{stats.user_level}</span>
              <span className="level-xp">{stats.total_xp?.toLocaleString()} XP</span>
            </div>
            <div className="level-bar-container">
              <div className="level-bar">
                <div
                  className="level-bar-fill"
                  style={{ width: `${Math.min((stats.total_xp % 5000) / 50, 100)}%` }}
                />
              </div>
            </div>
            {stats.nodes_pending_review > 0 && (
              <div className="review-reminder">
                📝 Tienes <strong>{stats.nodes_pending_review}</strong> nodos pendientes de repaso
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  )
}
