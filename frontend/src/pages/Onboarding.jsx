import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import './Onboarding.css'

const LANGUAGES = [
  { code: 'en', name: 'Inglés', flag: '🇺🇸', native: 'English' },
  { code: 'ja', name: 'Japonés', flag: '🇯🇵', native: '日本語' },
  { code: 'ru', name: 'Ruso', flag: '🇷🇺', native: 'Русский' },
  { code: 'fr', name: 'Francés', flag: '🇫🇷', native: 'Français' },
  { code: 'zh', name: 'Mandarín', flag: '🇨🇳', native: '中文' },
  { code: 'ko', name: 'Coreano', flag: '🇰🇷', native: '한국어' },
]

const LEVELS = [
  { code: 'A1', name: 'Principiante', desc: 'Puedo presentarme y usar frases básicas' },
  { code: 'A2', name: 'Elemental', desc: 'Puedo comunicarme en situaciones sencillas' },
  { code: 'B1', name: 'Intermedio', desc: 'Puedo manejar la mayoría de situaciones de viaje' },
  { code: 'B2', name: 'Intermedio Alto', desc: 'Puedo interactuar con fluidez con hablantes nativos' },
  { code: 'C1', name: 'Avanzado', desc: 'Puedo usar el idioma de forma flexible y eficaz' },
  { code: 'C2', name: 'Maestría', desc: 'Puedo entender prácticamente todo lo que leo o escucho' },
]

const CONTEXT_ICONS = {
  general: '🌍', medicina: '🏥', ingenieria: '💻',
  finanzas: '💰', videojuegos: '🎮', turismo: '✈️',
}

export default function Onboarding({ user, onComplete }) {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [language, setLanguage] = useState('')
  const [level, setLevel] = useState('')
  const [contexts, setContexts] = useState([])
  const [contextId, setContextId] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.getProfessionalContexts()
      .then(setContexts)
      .catch(() => setContexts([]))
  }, [])

  const handleComplete = async () => {
    setLoading(true)
    try {
      const updatedProfile = await api.completeOnboarding({
        target_language: language,
        cefr_level: level,
        professional_context_id: contextId,
      })
      if (onComplete) onComplete(updatedProfile)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      console.error('Onboarding error:', err)
    } finally {
      setLoading(false)
    }
  }

  const canNext = () => {
    if (step === 0) return !!language
    if (step === 1) return !!level
    if (step === 2) return !!contextId
    return false
  }

  return (
    <div className="onboarding animate-fade-in">
      <div className="onboarding-container glass-card">
        {/* Progress indicator */}
        <div className="onboarding-progress">
          {[0, 1, 2].map(i => (
            <div key={i} className={`progress-dot ${i <= step ? 'active' : ''} ${i < step ? 'completed' : ''}`}>
              {i < step ? '✓' : i + 1}
            </div>
          ))}
          <div className="progress-line">
            <div className="progress-line-fill" style={{ width: `${(step / 2) * 100}%` }} />
          </div>
        </div>

        {/* Step 1: Language */}
        {step === 0 && (
          <div className="onboarding-step">
            <h1 className="onboarding-title">¿Qué idioma quieres aprender? 🌍</h1>
            <p className="onboarding-subtitle">Elige el idioma que practicarás con Fluentify</p>
            <div className="options-grid languages-grid">
              {LANGUAGES.map(lang => (
                <button
                  key={lang.code}
                  className={`option-card glass-card ${language === lang.code ? 'selected' : ''}`}
                  onClick={() => setLanguage(lang.code)}
                >
                  <span className="option-icon">{lang.flag}</span>
                  <span className="option-name">{lang.name}</span>
                  <span className="option-native">{lang.native}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Level */}
        {step === 1 && (
          <div className="onboarding-step">
            <h1 className="onboarding-title">¿Cuál es tu nivel actual? 📊</h1>
            <p className="onboarding-subtitle">Esto nos ayudará a personalizar tu experiencia</p>
            <div className="options-grid levels-grid">
              {LEVELS.map(lv => (
                <button
                  key={lv.code}
                  className={`option-card level-card glass-card ${level === lv.code ? 'selected' : ''}`}
                  onClick={() => setLevel(lv.code)}
                >
                  <span className="level-code">{lv.code}</span>
                  <div className="level-text">
                    <span className="option-name">{lv.name}</span>
                    <span className="option-desc">{lv.desc}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Professional Context */}
        {step === 2 && (
          <div className="onboarding-step">
            <h1 className="onboarding-title">¿Cuál es tu contexto profesional? 💼</h1>
            <p className="onboarding-subtitle">Adaptaremos el vocabulario y los escenarios a tu área</p>
            <div className="options-grid contexts-grid">
              {contexts.map(ctx => (
                <button
                  key={ctx.id}
                  className={`option-card glass-card ${contextId === ctx.id ? 'selected' : ''}`}
                  onClick={() => setContextId(ctx.id)}
                >
                  <span className="option-icon">{CONTEXT_ICONS[ctx.slug] || '📚'}</span>
                  <span className="option-name">{ctx.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="onboarding-nav">
          {step > 0 && (
            <button className="btn-secondary" onClick={() => setStep(step - 1)}>
              ← Anterior
            </button>
          )}
          <div className="nav-spacer" />
          {step < 2 ? (
            <button
              className="btn-primary"
              disabled={!canNext()}
              onClick={() => setStep(step + 1)}
            >
              Siguiente →
            </button>
          ) : (
            <button
              className="btn-primary"
              disabled={!canNext() || loading}
              onClick={handleComplete}
            >
              {loading ? 'Configurando...' : '¡Empezar! 🚀'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
