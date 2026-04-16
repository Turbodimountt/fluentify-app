import { useState, useEffect } from 'react'
import { api } from '../api'
import './Achievements.css'

export default function Achievements() {
  const [data, setData] = useState({ unlocked: [], available: [], total_unlocked: 0, total_available: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getAchievements()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const iconMap = {
    star: '⭐', local_fire_department: '🔥', whatshot: '🔥', military_tech: '🎖️',
    verified: '✅', emoji_events: '🏆', workspace_premium: '💎', theater_comedy: '🎭',
    mic: '🎤', auto_awesome: '✨', stars: '🌟', translate: '🌐',
  }

  return (
    <div className="achievements-page animate-fade-in">
      <h1 className="page-title">🏆 Logros</h1>
      <p className="page-subtitle">{data.total_unlocked} desbloqueados de {data.total_unlocked + data.total_available}</p>

      {loading ? (
        <div className="loading-state">Cargando logros...</div>
      ) : (
        <>
          {data.unlocked.length > 0 && (
            <section className="section">
              <h2 className="section-title">✅ Desbloqueados</h2>
              <div className="achievements-grid">
                {data.unlocked.map((a, i) => (
                  <div key={a.id} className="achievement-card glass-card unlocked" style={{ animationDelay: `${i * 80}ms` }}>
                    <div className="ach-icon">{iconMap[a.icon_slug] || '🏅'}</div>
                    <h3 className="ach-name">{a.name}</h3>
                    <p className="ach-desc">{a.description}</p>
                    <div className="ach-reward">+{a.xp_reward} XP</div>
                    {a.earned_at && <span className="ach-date">{new Date(a.earned_at).toLocaleDateString('es', { day: 'numeric', month: 'short' })}</span>}
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="section">
            <h2 className="section-title">🔒 Por desbloquear</h2>
            <div className="achievements-grid">
              {data.available.map((a, i) => (
                <div key={a.id} className="achievement-card glass-card locked" style={{ animationDelay: `${i * 80}ms` }}>
                  <div className="ach-icon locked-icon">{iconMap[a.icon_slug] || '🏅'}</div>
                  <h3 className="ach-name">{a.name}</h3>
                  <p className="ach-desc">{a.description}</p>
                  <div className="ach-reward">+{a.xp_reward} XP</div>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  )
}
