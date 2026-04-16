import { useState, useRef, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { api } from '../api'
import './Chat.css'

export default function Chat({ user }) {
  const location = useLocation()
  const navigate = useNavigate()
  const { mode = 'libre', language = 'en', context, scenario } = location.state || {}
  
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [corrections, setCorrections] = useState([])
  const [showCorrections, setShowCorrections] = useState(false)
  const [totalXp, setTotalXp] = useState(0)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const modeLabels = { libre: '💬 Modo Libre', roleplay: '🎭 Roleplay', susurro: '🤫 Susurro' }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    // Welcome message
    const welcomeMessages = {
      libre: `¡Hola! Soy tu tutor de idiomas. Comencemos a conversar en ${language === 'en' ? 'inglés' : language}. Escribe lo que quieras y te ayudaré a mejorar. 🌟`,
      roleplay: `¡Bienvenido al escenario "${scenario}"! Entraré en personaje ahora. Recuerda que solo usaré [Coach:] para darte feedback pedagógico. ¡Empecemos! 🎭`,
      susurro: `Bienvenido al Modo Susurro 🤫 Este es un espacio seguro y sin presión. Practica a tu ritmo — máximo 2 correcciones por turno, sin puntuaciones. ¡Tú puedes! 💜`,
    }
    setMessages([{ role: 'ai', content: welcomeMessages[mode] || welcomeMessages.libre }])
  }, [])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    
    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await api.sendMessage({
        session_id: sessionId,
        message: userMessage,
        mode,
        target_language: language,
        scenario_name: scenario,
        professional_context: context,
      })

      setSessionId(response.session_id)
      setMessages(prev => [...prev, {
        role: 'ai',
        content: response.ai_response,
        corrections: response.corrections,
        vocabulary: response.highlighted_vocabulary,
        suggestion: response.suggestion,
      }])
      
      if (response.corrections?.length > 0) {
        setCorrections(response.corrections)
        setShowCorrections(true)
      }
      setTotalXp(prev => prev + (response.xp_earned || 0))
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: '⚠️ Error de conexión. Intenta de nuevo.', isError: true }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const endSession = async () => {
    if (sessionId) {
      try {
        const result = await api.endSession(sessionId)
        setTotalXp(result.xp_earned || totalXp)
      } catch {}
    }
    navigate('/dashboard')
  }

  return (
    <div className="chat-page">
      {/* Header */}
      <div className="chat-header glass">
        <div className="chat-header-left">
          <button className="btn btn-ghost btn-sm" onClick={endSession}>← Terminar</button>
          <span className="chat-mode-label">{modeLabels[mode]}</span>
        </div>
        <div className="chat-header-right">
          <span className="xp-counter">⚡ {totalXp} XP</span>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role} ${msg.isError ? 'error' : ''} animate-fade-in`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🌍'}
            </div>
            <div className="message-content">
              <div className="message-bubble">
                {msg.content}
              </div>
              {msg.vocabulary?.length > 0 && (
                <div className="vocab-highlight">
                  {msg.vocabulary.map((v, j) => (
                    <div key={j} className="vocab-item">
                      <strong>{v.term}</strong> — {v.translation}
                      <span className="vocab-example">{v.example}</span>
                    </div>
                  ))}
                </div>
              )}
              {msg.suggestion && (
                <button
                  className="suggestion-btn"
                  onClick={() => { setInput(msg.suggestion); inputRef.current?.focus(); }}
                >
                  💡 {msg.suggestion}
                </button>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message ai animate-fade-in">
            <div className="message-avatar">🌍</div>
            <div className="message-content">
              <div className="message-bubble typing">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Corrections Panel */}
      {showCorrections && corrections.length > 0 && (
        <div className="corrections-panel glass animate-slide-up">
          <div className="corrections-header">
            <span>📝 Correcciones ({corrections.length})</span>
            <button className="btn btn-ghost btn-sm" onClick={() => setShowCorrections(false)}>✕</button>
          </div>
          {corrections.map((c, i) => (
            <div key={i} className={`correction-item severity-${c.severity}`}>
              <div className="correction-change">
                <span className="original">{c.original_text}</span>
                <span className="arrow">→</span>
                <span className="corrected">{c.corrected_text}</span>
              </div>
              <p className="correction-explanation">{c.explanation}</p>
            </div>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="chat-input-area glass">
        <input
          ref={inputRef}
          className="chat-input"
          type="text"
          placeholder={mode === 'susurro' ? 'Escribe con confianza... 💜' : 'Escribe tu mensaje...'}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          disabled={loading}
        />
        <button className="btn btn-primary send-btn" onClick={sendMessage} disabled={!input.trim() || loading}>
          {loading ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  )
}
