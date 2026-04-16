import { useState, useRef, useEffect } from 'react'
import './Voice.css'

export default function Voice() {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [ttsText, setTtsText] = useState('')
  const [pronunciationResult, setPronunciationResult] = useState(null)
  const [practiceText, setPracticeText] = useState('')
  const [loading, setLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState(null)
  const [mode, setMode] = useState(null) // 'listen', 'speak', 'pronounce'
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const audioRef = useRef(null)

  const SAMPLE_SENTENCES = {
    en: [
      "The weather is beautiful today.",
      "Could you recommend a good restaurant?",
      "I would like to schedule an appointment.",
      "How much does this product cost?",
      "Thank you for your help, I appreciate it.",
    ],
    ja: [
      "今日はいい天気ですね。",
      "おすすめのレストランはありますか？",
      "予約をしたいのですが。",
    ],
    fr: [
      "Bonjour, comment allez-vous aujourd'hui?",
      "Je voudrais réserver une table pour deux.",
      "Pourriez-vous m'aider, s'il vous plaît?",
    ],
  }

  const getRandomSentence = (lang = 'en') => {
    const sentences = SAMPLE_SENTENCES[lang] || SAMPLE_SENTENCES.en
    return sentences[Math.floor(Math.random() * sentences.length)]
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' })
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        stream.getTracks().forEach(track => track.stop())

        if (mode === 'speak') {
          await sendSTT(blob)
        } else if (mode === 'pronounce') {
          await sendPronunciation(blob)
        }
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch {
      alert('No se pudo acceder al micrófono. Verifica los permisos del navegador.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const sendSTT = async (blob) => {
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('audio', blob, 'recording.webm')
      formData.append('language_code', 'en-US')

      const res = await fetch('http://localhost:8000/api/v1/voice/stt', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('fluentify_access_token')}` },
        body: formData,
      })
      const data = await res.json()
      setTranscript(data.text || '')
    } catch {
      setTranscript('Error de conexión')
    }
    setLoading(false)
  }

  const sendTTS = async () => {
    if (!ttsText.trim()) return
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/v1/voice/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('fluentify_access_token')}`,
        },
        body: JSON.stringify({ text: ttsText, language: 'en' }),
      })
      const data = await res.json()
      if (data.audio_base64) {
        const audioBlob = new Blob(
          [Uint8Array.from(atob(data.audio_base64), c => c.charCodeAt(0))],
          { type: data.content_type || 'audio/wav' }
        )
        const url = URL.createObjectURL(audioBlob)
        setAudioUrl(url)
        if (audioRef.current) {
          audioRef.current.src = url
          audioRef.current.play()
        }
      }
    } catch {
      alert('Error al generar audio')
    }
    setLoading(false)
  }

  const sendPronunciation = async (blob) => {
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('audio', blob, 'recording.webm')
      
      // Read file as base64
      const reader = new FileReader()
      reader.readAsDataURL(blob)
      reader.onloadend = async () => {
        const base64 = reader.result.split(',')[1]
        const res = await fetch('http://localhost:8000/api/v1/voice/pronunciation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('fluentify_access_token')}`,
          },
          body: JSON.stringify({
            audio_base64: base64,
            expected_text: practiceText,
            language_code: 'en-US',
          }),
        })
        const data = await res.json()
        setPronunciationResult(data)
        setLoading(false)
      }
    } catch {
      setLoading(false)
    }
  }

  // Mode selection
  if (!mode) {
    return (
      <div className="voice-page animate-fade-in">
        <h1 className="page-title">🎤 Práctica de Voz</h1>
        <p className="page-subtitle">Mejora tu pronunciación y comprensión auditiva</p>
        <div className="voice-modes-grid">
          <button className="voice-mode-card glass-card" onClick={() => setMode('listen')}>
            <span className="vm-icon">🔊</span>
            <h3>Escuchar</h3>
            <p>Escucha pronunciaciones nativas (TTS)</p>
          </button>
          <button className="voice-mode-card glass-card" onClick={() => setMode('speak')}>
            <span className="vm-icon">🎙️</span>
            <h3>Hablar</h3>
            <p>Graba tu voz y obtén transcripción (STT)</p>
          </button>
          <button className="voice-mode-card glass-card" onClick={() => { setMode('pronounce'); setPracticeText(getRandomSentence()); }}>
            <span className="vm-icon">📊</span>
            <h3>Pronunciación</h3>
            <p>Analiza la calidad de tu pronunciación</p>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="voice-page animate-fade-in">
      <button className="btn btn-ghost btn-sm" onClick={() => { setMode(null); setTranscript(''); setPronunciationResult(null); }}>
        ← Cambiar modo
      </button>

      {/* Listen Mode (TTS) */}
      {mode === 'listen' && (
        <div className="voice-section">
          <h2>🔊 Escuchar pronunciación</h2>
          <p className="page-subtitle">Escribe un texto y escucha la pronunciación nativa</p>
          <textarea
            className="input voice-textarea"
            placeholder="Escribe un texto para escuchar..."
            value={ttsText}
            onChange={(e) => setTtsText(e.target.value)}
            rows={3}
          />
          <div className="voice-actions">
            <button className="btn btn-primary" onClick={sendTTS} disabled={!ttsText.trim() || loading}>
              {loading ? '⏳ Generando...' : '🔊 Escuchar'}
            </button>
            <button className="btn btn-ghost" onClick={() => setTtsText(getRandomSentence())}>
              🎲 Frase aleatoria
            </button>
          </div>
          {audioUrl && (
            <div className="audio-player glass-card">
              <audio ref={audioRef} controls src={audioUrl} style={{ width: '100%' }} />
            </div>
          )}
        </div>
      )}

      {/* Speak Mode (STT) */}
      {mode === 'speak' && (
        <div className="voice-section">
          <h2>🎙️ Dictado por voz</h2>
          <p className="page-subtitle">Graba tu voz — la IA transcribirá lo que dices</p>
          <div className="recording-area">
            <button
              className={`record-btn ${isRecording ? 'recording' : ''}`}
              onClick={isRecording ? stopRecording : startRecording}
            >
              <span className="record-icon">{isRecording ? '⏹️' : '🎙️'}</span>
              <span>{isRecording ? 'Detener' : 'Grabar'}</span>
            </button>
            {isRecording && <div className="recording-indicator animate-pulse">🔴 Grabando...</div>}
          </div>
          {loading && <div className="loading-state">Transcribiendo...</div>}
          {transcript && (
            <div className="transcript-result glass-card">
              <h3>Transcripción:</h3>
              <p className="transcript-text">{transcript}</p>
            </div>
          )}
        </div>
      )}

      {/* Pronunciation Mode */}
      {mode === 'pronounce' && (
        <div className="voice-section">
          <h2>📊 Análisis de pronunciación</h2>
          <p className="page-subtitle">Lee la frase en voz alta y analiza tu pronunciación</p>
          <div className="practice-sentence glass-card">
            <span className="practice-label">Frase a practicar:</span>
            <p className="practice-text">{practiceText}</p>
            <button className="btn btn-ghost btn-sm" onClick={() => setPracticeText(getRandomSentence())}>
              🎲 Otra frase
            </button>
          </div>
          <div className="recording-area">
            <button
              className={`record-btn ${isRecording ? 'recording' : ''}`}
              onClick={isRecording ? stopRecording : startRecording}
            >
              <span className="record-icon">{isRecording ? '⏹️' : '🎙️'}</span>
              <span>{isRecording ? 'Detener' : 'Grabar'}</span>
            </button>
            {isRecording && <div className="recording-indicator animate-pulse">🔴 Grabando...</div>}
          </div>
          {loading && <div className="loading-state">Analizando pronunciación...</div>}
          {pronunciationResult && (
            <div className="pronunciation-result glass-card animate-slide-up">
              <div className="pron-score">
                <div className={`score-ring ${pronunciationResult.score >= 0.8 ? 'excellent' : pronunciationResult.score >= 0.5 ? 'good' : 'needs-work'}`}>
                  <span className="score-number">{Math.round(pronunciationResult.score * 100)}%</span>
                </div>
              </div>
              {pronunciationResult.transcript && (
                <div className="pron-transcript">
                  <span className="pron-label">Lo que dijiste:</span>
                  <p>{pronunciationResult.transcript}</p>
                </div>
              )}
              {pronunciationResult.issues?.length > 0 && (
                <div className="pron-issues">
                  <span className="pron-label">Puntos a mejorar:</span>
                  {pronunciationResult.issues.map((issue, i) => (
                    <div key={i} className="pron-issue">
                      <span className="pron-expected">{issue.expected}</span>
                      <span className="arrow">→</span>
                      <span className="pron-heard">{issue.heard}</span>
                      <span className="pron-tip">{issue.tip}</span>
                    </div>
                  ))}
                </div>
              )}
              {pronunciationResult.tips?.filter(t => t).map((tip, i) => (
                <div key={i} className="pron-tip-item">💡 {tip}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
