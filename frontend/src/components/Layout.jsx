import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import './Layout.css'

const NAV_ITEMS = [
  { path: '/dashboard', icon: '🏠', label: 'Dashboard' },
  { path: '/practice', icon: '💬', label: 'Practicar' },
  { path: '/voice', icon: '🎤', label: 'Voz' },
  { path: '/writing', icon: '✍️', label: 'Escritura' },
  { path: '/progress', icon: '🌟', label: 'Progreso' },
  { path: '/history', icon: '📚', label: 'Historial' },
  { path: '/achievements', icon: '🏆', label: 'Logros' },
  { path: '/profile', icon: '👤', label: 'Perfil' },
]

export default function Layout({ user, onLogout }) {
  const navigate = useNavigate()
  
  return (
    <div className="layout">
      <aside className="sidebar glass">
        <div className="sidebar-logo" onClick={() => navigate('/dashboard')}>
          <div className="logo-icon">🌍</div>
          <span className="logo-text">Fluentify</span>
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          {user && (
            <div className="user-badge glass-card">
              <div className="user-avatar">{user.display_name?.[0]?.toUpperCase() || '?'}</div>
              <div className="user-info">
                <span className="user-name">{user.display_name || 'Usuario'}</span>
                <span className="user-level">{user.user_level || 'Explorador'}</span>
              </div>
            </div>
          )}
          <button className="btn btn-ghost btn-sm" onClick={onLogout} style={{ width: '100%' }}>
            🚪 Cerrar Sesión
          </button>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
