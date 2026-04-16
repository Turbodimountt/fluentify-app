import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { api } from '../api'
import './Practice.css'

const MODES = {
  libre: { icon: '💬', title: 'Modo Libre', color: '#6C5CE7', desc: 'Conversación abierta con la IA sobre cualquier tema' },
  roleplay: { icon: '🎭', title: 'Roleplay Profesional', color: '#00CEC9', desc: 'Escenarios inmersivos para tu contexto profesional' },
  susurro: { icon: '🤫', title: 'Modo Susurro', color: '#FD79A8', desc: 'Práctica de pronunciación sin presión — máximo 2 correcciones por turno' },
}

const LANGUAGES = [
  { code: 'en', name: 'Inglés', flag: '🇬🇧' },
  { code: 'ja', name: 'Japonés', flag: '🇯🇵' },
  { code: 'ru', name: 'Ruso', flag: '🇷🇺' },
  { code: 'fr', name: 'Francés', flag: '🇫🇷' },
  { code: 'zh', name: 'Mandarín', flag: '🇨🇳' },
]

export default function Practice({ user }) {
  const navigate = useNavigate()
  const location = useLocation()
  const [mode, setMode] = useState(location.state?.mode || null)
  const [language, setLanguage] = useState(user?.target_language || 'en')
  const [contexts, setContexts] = useState([])
  const [selectedContext, setSelectedContext] = useState(null)
  const [scenarios, setScenarios] = useState([])
  const [selectedScenario, setSelectedScenario] = useState(null)

  useEffect(() => {
    api.getProfessionalContexts().then(setContexts).catch(() => {})
  }, [])

  useEffect(() => {
    if (selectedContext && mode === 'roleplay') {
      api.getScenarios(selectedContext.slug).then(setScenarios).catch(() => setScenarios([]))
    }
  }, [selectedContext, mode])

  const startSession = () => {
    navigate('/practice/session', {
      state: {
        mode,
        language,
        context: selectedContext?.slug,
        scenario: selectedScenario?.name,
      },
    })
  }

  if (!mode) {
    return (
      <div className="practice animate-fade-in">
        <h1 className="page-title">Selecciona un modo</h1>
        <p className="page-subtitle">Elige cómo quieres practicar hoy</p>
        <div className="mode-select-grid">
          {Object.entries(MODES).map(([key, m]) => (
            <button key={key} className="mode-select-card glass-card" onClick={() => setMode(key)}>
              <div className="msc-icon" style={{ background: `linear-gradient(135deg, ${m.color}, ${m.color}66)` }}>
                {m.icon}
              </div>
              <h3>{m.title}</h3>
              <p>{m.desc}</p>
            </button>
          ))}
        </div>
      </div>
    )
  }

  const currentMode = MODES[mode]

  return (
    <div className="practice animate-fade-in">
      <button className="btn btn-ghost btn-sm" onClick={() => setMode(null)}>← Cambiar modo</button>
      <div className="practice-header" style={{ borderColor: currentMode.color + '40' }}>
        <span className="practice-mode-icon">{currentMode.icon}</span>
        <div>
          <h1 className="page-title">{currentMode.title}</h1>
          <p className="page-subtitle">{currentMode.desc}</p>
        </div>
      </div>

      <div className="practice-setup">
        {/* Language Selection */}
        <div className="setup-section">
          <h3>Idioma objetivo</h3>
          <div className="lang-grid">
            {LANGUAGES.map(l => (
              <button
                key={l.code}
                className={`lang-btn glass-card ${language === l.code ? 'selected' : ''}`}
                onClick={() => setLanguage(l.code)}
              >
                <span className="lang-flag">{l.flag}</span>
                <span>{l.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Context Selection (for roleplay) */}
        {mode === 'roleplay' && (
          <div className="setup-section">
            <h3>Contexto profesional</h3>
            <div className="context-grid">
              {contexts.map(ctx => (
                <button
                  key={ctx.id}
                  className={`context-btn glass-card ${selectedContext?.id === ctx.id ? 'selected' : ''}`}
                  onClick={() => { setSelectedContext(ctx); setSelectedScenario(null); }}
                >
                  <span className="ctx-name">{ctx.name}</span>
                  <span className="ctx-tags">{ctx.vocabulary_tags?.slice(0, 3).join(' · ')}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Scenario Selection (for roleplay) */}
        {mode === 'roleplay' && selectedContext && scenarios.length > 0 && (
          <div className="setup-section">
            <h3>Escenario</h3>
            <div className="scenario-grid">
              {scenarios.map((s, i) => (
                <button
                  key={i}
                  className={`scenario-btn glass-card ${selectedScenario?.name === s.name ? 'selected' : ''}`}
                  onClick={() => setSelectedScenario(s)}
                >
                  <div className="scenario-header">
                    <span className="scenario-name">{s.name}</span>
                    <span className="scenario-diff">{s.difficulty}</span>
                  </div>
                  <p className="scenario-desc">{s.description}</p>
                  <p className="scenario-role">IA: {s.ai_role}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        <button
          className="btn btn-primary btn-lg"
          onClick={startSession}
          disabled={mode === 'roleplay' && !selectedScenario}
          style={{ width: '100%', marginTop: '16px' }}
        >
          🚀 Comenzar sesión
        </button>
      </div>
    </div>
  )
}
