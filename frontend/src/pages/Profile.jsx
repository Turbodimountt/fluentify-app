import { useState, useEffect } from 'react'
import { api } from '../api'
import './Profile.css'

const LANGUAGES = [
  { code: 'en', name: 'Inglés' },
  { code: 'ja', name: 'Japonés' },
  { code: 'ru', name: 'Ruso' },
  { code: 'fr', name: 'Francés' },
  { code: 'zh', name: 'Mandarín' },
]

const CEFR = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

export default function Profile({ user, setUser }) {
  const [contexts, setContexts] = useState([])
  const [form, setForm] = useState({
    target_language: 'en',
    cefr_level: 'A1',
    correction_level: 'medium',
    whisper_mode_default: false,
    interface_language: 'es',
    professional_context_id: '',
  })
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.getProfessionalContexts().then(setContexts).catch(() => {})
  }, [])

  useEffect(() => {
    if (user) {
      setForm({
        target_language: user.target_language || 'en',
        cefr_level: user.cefr_level || 'A1',
        correction_level: user.correction_level || 'medium',
        whisper_mode_default: user.whisper_mode_default || false,
        interface_language: user.interface_language || 'es',
        professional_context_id: user.professional_context_id || '',
      })
    }
  }, [user])

  const handleSave = async () => {
    setSaving(true)
    try {
      const updated = await api.updateProfile(form)
      setUser(updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch { }
    setSaving(false)
  }

  return (
    <div className="profile-page animate-fade-in">
      <h1 className="page-title">👤 Perfil</h1>
      <p className="page-subtitle">Configura tu experiencia de aprendizaje</p>

      <div className="profile-form glass-card">
        <div className="profile-section">
          <h3>Idioma objetivo</h3>
          <div className="radio-group">
            {LANGUAGES.map(l => (
              <label key={l.code} className={`radio-item ${form.target_language === l.code ? 'selected' : ''}`}>
                <input type="radio" name="language" value={l.code} checked={form.target_language === l.code}
                  onChange={(e) => setForm({ ...form, target_language: e.target.value })} />
                <span>{l.name}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="profile-section">
          <h3>Nivel CEFR</h3>
          <div className="radio-group">
            {CEFR.map(level => (
              <label key={level} className={`radio-item small ${form.cefr_level === level ? 'selected' : ''}`}>
                <input type="radio" name="cefr" value={level} checked={form.cefr_level === level}
                  onChange={(e) => setForm({ ...form, cefr_level: e.target.value })} />
                <span>{level}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="profile-section">
          <h3>Contexto profesional</h3>
          <select className="input"
            value={form.professional_context_id}
            onChange={(e) => setForm({ ...form, professional_context_id: e.target.value })}>
            <option value="">Seleccionar...</option>
            {contexts.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>

        <div className="profile-section">
          <h3>Nivel de correcciones</h3>
          <div className="radio-group">
            {[{ v: 'low', l: '🟢 Bajo' }, { v: 'medium', l: '🟡 Medio' }, { v: 'high', l: '🔴 Alto' }].map(x => (
              <label key={x.v} className={`radio-item ${form.correction_level === x.v ? 'selected' : ''}`}>
                <input type="radio" name="correction" value={x.v} checked={form.correction_level === x.v}
                  onChange={(e) => setForm({ ...form, correction_level: e.target.value })} />
                <span>{x.l}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="profile-section">
          <label className="toggle-item">
            <input type="checkbox" checked={form.whisper_mode_default}
              onChange={(e) => setForm({ ...form, whisper_mode_default: e.target.checked })} />
            <span>🤫 Modo Susurro activado por defecto</span>
          </label>
        </div>

        <div className="profile-section">
          <h3>Idioma de la interfaz</h3>
          <div className="radio-group">
            <label className={`radio-item ${form.interface_language === 'es' ? 'selected' : ''}`}>
              <input type="radio" name="iface" value="es" checked={form.interface_language === 'es'}
                onChange={(e) => setForm({ ...form, interface_language: e.target.value })} />
              <span>🇪🇸 Español</span>
            </label>
            <label className={`radio-item ${form.interface_language === 'en' ? 'selected' : ''}`}>
              <input type="radio" name="iface" value="en" checked={form.interface_language === 'en'}
                onChange={(e) => setForm({ ...form, interface_language: e.target.value })} />
              <span>🇬🇧 English</span>
            </label>
          </div>
        </div>

        <button className="btn btn-primary btn-lg" onClick={handleSave} disabled={saving} style={{ width: '100%' }}>
          {saving ? '⏳ Guardando...' : saved ? '✅ Guardado' : '💾 Guardar cambios'}
        </button>
      </div>
    </div>
  )
}
