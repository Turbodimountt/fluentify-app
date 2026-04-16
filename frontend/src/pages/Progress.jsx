import { useState, useEffect } from 'react'
import { api } from '../api'
import './Progress.css'

export default function Progress() {
  const [nodes, setNodes] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getKnowledgeNodes(), api.getStats()])
      .then(([nodesData, statsData]) => {
        setNodes(nodesData.nodes || [])
        setStats(statsData)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const getMasteryLabel = (score) => {
    if (score >= 0.8) return { label: 'Dominado', color: '#00B894' }
    if (score >= 0.5) return { label: 'En progreso', color: '#FDCB6E' }
    return { label: 'Nuevo', color: '#74B9FF' }
  }

  return (
    <div className="progress-page animate-fade-in">
      <h1 className="page-title">🌟 Constelación de Conocimiento</h1>
      <p className="page-subtitle">Tu mapa de habilidades lingüísticas</p>

      {stats && (
        <div className="progress-stats-row">
          <div className="ps-item glass-card">
            <span className="ps-value">{stats.nodes_mastered}</span>
            <span className="ps-label">Dominados</span>
          </div>
          <div className="ps-item glass-card">
            <span className="ps-value">{stats.nodes_pending_review}</span>
            <span className="ps-label">Pendientes</span>
          </div>
          <div className="ps-item glass-card">
            <span className="ps-value">{(stats.error_rate * 100).toFixed(0)}%</span>
            <span className="ps-label">Tasa de error</span>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading-state">Cargando nodos...</div>
      ) : nodes.length === 0 ? (
        <div className="empty-state glass-card">
          <span className="empty-icon">✨</span>
          <h3>Tu constelación está vacía</h3>
          <p>Los nodos aparecerán a medida que practiques y aprendas nuevos conceptos</p>
        </div>
      ) : (
        <div className="nodes-constellation">
          {nodes.map((node, i) => {
            const mastery = getMasteryLabel(node.mastery_score)
            return (
              <div
                key={node.id}
                className="node-card glass-card"
                style={{
                  animationDelay: `${i * 60}ms`,
                  borderLeftColor: node.color_hex || mastery.color,
                }}
              >
                <div className="node-header">
                  <span className="node-label">{node.display_label}</span>
                  <span className="node-mastery" style={{ color: mastery.color }}>{mastery.label}</span>
                </div>
                <div className="node-bar">
                  <div className="node-bar-fill" style={{ width: `${node.mastery_score * 100}%`, background: mastery.color }} />
                </div>
                <div className="node-meta">
                  {node.category_name && <span className="node-cat">{node.category_name}</span>}
                  <span className="node-review">Repaso: {new Date(node.next_review_at).toLocaleDateString('es', { day: 'numeric', month: 'short' })}</span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
