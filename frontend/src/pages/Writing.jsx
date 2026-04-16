import { useState, useRef, useEffect, useCallback } from 'react'
import { api } from '../api'
import './Writing.css'

const WRITING_SYSTEMS = [
  { id: 'kanji', name: 'Kanji', flag: '🇯🇵', desc: '漢字' },
  { id: 'cyrillic', name: 'Cirílico', flag: '🇷🇺', desc: 'Кириллица' },
  { id: 'hangul', name: 'Hangul', flag: '🇰🇷', desc: '한글' },
]

export default function Writing() {
  const canvasRef = useRef(null)
  const [writingSystem, setWritingSystem] = useState(null)
  const [characters, setCharacters] = useState([])
  const [currentCharIdx, setCurrentCharIdx] = useState(0)
  const [strokes, setStrokes] = useState([])
  const [currentStroke, setCurrentStroke] = useState([])
  const [isDrawing, setIsDrawing] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [score, setScore] = useState(null)
  const [loading, setLoading] = useState(false)
  const [totalScore, setTotalScore] = useState(0)
  const [practiced, setPracticed] = useState(0)

  const currentChar = characters[currentCharIdx]

  useEffect(() => {
    if (writingSystem) {
      fetch(`http://localhost:8000/api/v1/writing/characters/${writingSystem}?level=beginner`)
        .then(r => r.json())
        .then(data => { setCharacters(data.characters || []); setCurrentCharIdx(0); })
        .catch(() => setCharacters([]))
    }
  }, [writingSystem])

  // Canvas setup
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const dpr = window.devicePixelRatio || 1
    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx.scale(dpr, dpr)
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    redrawCanvas()
  }, [strokes, currentStroke, currentChar])

  const redrawCanvas = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const rect = canvas.getBoundingClientRect()
    ctx.clearRect(0, 0, rect.width, rect.height)

    // Draw grid lines
    ctx.strokeStyle = 'rgba(108, 92, 231, 0.08)'
    ctx.lineWidth = 1
    ctx.setLineDash([5, 5])
    ctx.beginPath()
    ctx.moveTo(rect.width / 2, 0)
    ctx.lineTo(rect.width / 2, rect.height)
    ctx.moveTo(0, rect.height / 2)
    ctx.lineTo(rect.width, rect.height / 2)
    ctx.stroke()
    ctx.setLineDash([])

    // Draw target character (ghost)
    if (currentChar) {
      ctx.fillStyle = 'rgba(108, 92, 231, 0.08)'
      ctx.font = `${rect.width * 0.7}px serif`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(currentChar.char, rect.width / 2, rect.height / 2)
    }

    // Draw completed strokes
    strokes.forEach((stroke, i) => {
      if (stroke.length < 2) return
      ctx.strokeStyle = `hsl(${200 + i * 30}, 80%, 60%)`
      ctx.lineWidth = 4
      ctx.beginPath()
      ctx.moveTo(stroke[0].x, stroke[0].y)
      stroke.forEach(p => ctx.lineTo(p.x, p.y))
      ctx.stroke()
    })

    // Draw current stroke
    if (currentStroke.length > 1) {
      ctx.strokeStyle = '#00CEC9'
      ctx.lineWidth = 4
      ctx.beginPath()
      ctx.moveTo(currentStroke[0].x, currentStroke[0].y)
      currentStroke.forEach(p => ctx.lineTo(p.x, p.y))
      ctx.stroke()
    }
  }, [strokes, currentStroke, currentChar])

  const getPos = (e) => {
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const clientX = e.touches ? e.touches[0].clientX : e.clientX
    const clientY = e.touches ? e.touches[0].clientY : e.clientY
    return { x: clientX - rect.left, y: clientY - rect.top, t: Date.now() }
  }

  const startStroke = (e) => {
    e.preventDefault()
    setIsDrawing(true)
    setCurrentStroke([getPos(e)])
  }

  const moveStroke = (e) => {
    if (!isDrawing) return
    e.preventDefault()
    setCurrentStroke(prev => [...prev, getPos(e)])
  }

  const endStroke = (e) => {
    if (!isDrawing) return
    e.preventDefault()
    setIsDrawing(false)
    if (currentStroke.length > 1) {
      setStrokes(prev => [...prev, currentStroke])
    }
    setCurrentStroke([])
  }

  const clearCanvas = () => {
    setStrokes([])
    setCurrentStroke([])
    setFeedback(null)
    setScore(null)
  }

  const undoStroke = () => {
    setStrokes(prev => prev.slice(0, -1))
    setFeedback(null)
    setScore(null)
  }

  const analyzeStrokes = async () => {
    if (strokes.length === 0 || !currentChar) return
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/v1/writing/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('fluentify_access_token')}`,
        },
        body: JSON.stringify({
          strokes,
          target_character: currentChar.char,
          writing_system: writingSystem,
        }),
      })
      const data = await res.json()
      setScore(data.accuracy_score)
      setFeedback(data.feedback || [])
      setTotalScore(prev => prev + data.accuracy_score)
      setPracticed(prev => prev + 1)
    } catch {
      setFeedback([{ type: 'error', message: 'Error de conexión. Intente de nuevo.' }])
    }
    setLoading(false)
  }

  const nextCharacter = () => {
    clearCanvas()
    setCurrentCharIdx(prev => (prev + 1) % characters.length)
  }

  // System selection
  if (!writingSystem) {
    return (
      <div className="writing-page animate-fade-in">
        <h1 className="page-title">✍️ Escritura Manual</h1>
        <p className="page-subtitle">Practica la escritura de caracteres con reconocimiento de trazos</p>
        <div className="system-grid">
          {WRITING_SYSTEMS.map(sys => (
            <button key={sys.id} className="system-card glass-card" onClick={() => setWritingSystem(sys.id)}>
              <span className="system-flag">{sys.flag}</span>
              <h3>{sys.name}</h3>
              <p className="system-native">{sys.desc}</p>
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="writing-page animate-fade-in">
      <div className="writing-header">
        <button className="btn btn-ghost btn-sm" onClick={() => { setWritingSystem(null); clearCanvas(); setCharacters([]); }}>
          ← Cambiar sistema
        </button>
        <div className="writing-stats">
          <span className="ws-item">✍️ {practiced} practicados</span>
          {practiced > 0 && <span className="ws-item">📊 {Math.round(totalScore / practiced * 100)}% promedio</span>}
        </div>
      </div>

      <div className="writing-workspace">
        {/* Character info */}
        <div className="char-info glass-card">
          <div className="char-target">{currentChar?.char || '?'}</div>
          <div className="char-details">
            <span className="char-meaning">{currentChar?.meaning}</span>
            <span className="char-reading">{currentChar?.reading}</span>
            <span className="char-strokes">Trazos: {currentChar?.strokes}</span>
          </div>
          <div className="char-nav">
            <button className="btn btn-ghost btn-sm" onClick={() => setCurrentCharIdx(Math.max(0, currentCharIdx - 1))} disabled={currentCharIdx === 0}>
              ◀ Anterior
            </button>
            <span>{currentCharIdx + 1}/{characters.length}</span>
            <button className="btn btn-ghost btn-sm" onClick={nextCharacter}>
              Siguiente ▶
            </button>
          </div>
        </div>

        {/* Canvas */}
        <div className="canvas-container">
          <canvas
            ref={canvasRef}
            className="writing-canvas"
            onMouseDown={startStroke}
            onMouseMove={moveStroke}
            onMouseUp={endStroke}
            onMouseLeave={endStroke}
            onTouchStart={startStroke}
            onTouchMove={moveStroke}
            onTouchEnd={endStroke}
          />
          <div className="canvas-controls">
            <button className="btn btn-ghost btn-sm" onClick={undoStroke} disabled={strokes.length === 0}>
              ↩ Deshacer
            </button>
            <button className="btn btn-ghost btn-sm" onClick={clearCanvas} disabled={strokes.length === 0}>
              🗑️ Borrar
            </button>
            <button className="btn btn-primary" onClick={analyzeStrokes} disabled={strokes.length === 0 || loading}>
              {loading ? '⏳ Analizando...' : '✅ Verificar'}
            </button>
          </div>
        </div>

        {/* Feedback */}
        {score !== null && (
          <div className="feedback-panel glass-card animate-slide-up">
            <div className="score-display">
              <div className={`score-ring ${score >= 0.8 ? 'excellent' : score >= 0.5 ? 'good' : 'needs-work'}`}>
                <span className="score-number">{Math.round(score * 100)}%</span>
              </div>
              <span className="score-label">
                {score >= 0.9 ? '¡Perfecto! 🌟' : score >= 0.7 ? '¡Bien! 💪' : score >= 0.5 ? 'Sigue practicando ✍️' : 'Inténtalo de nuevo 📝'}
              </span>
            </div>
            {feedback?.map((f, i) => (
              <div key={i} className={`feedback-item ${f.type}`}>
                {f.type === 'praise' && '🌟'}
                {f.type === 'encouragement' && '💪'}
                {f.type === 'suggestion' && '💡'}
                {f.type === 'guidance' && '📝'}
                {f.type === 'tip' && '📖'}
                {f.type === 'stroke_count' && '🔢'}
                {f.type === 'direction' && '↗️'}
                {' '}{f.message}
              </div>
            ))}
            <button className="btn btn-accent" onClick={nextCharacter} style={{ width: '100%', marginTop: '12px' }}>
              Siguiente carácter →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
