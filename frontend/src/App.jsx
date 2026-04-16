import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { api } from './api'
import Login from './pages/Login'
import Onboarding from './pages/Onboarding'
import Dashboard from './pages/Dashboard'
import Practice from './pages/Practice'
import Chat from './pages/Chat'
import History from './pages/History'
import Progress from './pages/Progress'
import Achievements from './pages/Achievements'
import Profile from './pages/Profile'
import Voice from './pages/Voice'
import Writing from './pages/Writing'
import Layout from './components/Layout'
import './index.css'

function ProtectedRoute({ children, isAuth }) {
  return isAuth ? children : <Navigate to="/login" replace />
}

export default function App() {
  const [isAuth, setIsAuth] = useState(!!localStorage.getItem('fluentify_access_token'))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isAuth) {
      api.getProfile()
        .then(profile => {
          setUser(profile)
        })
        .catch(() => {
          setIsAuth(false)
          api.clearTokens()
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [isAuth])

  const handleLogin = async (email, password) => {
    await api.login(email, password)
    setIsAuth(true)
  }

  const handleRegister = async (email, password, name) => {
    await api.register(email, password, name)
    await api.login(email, password)
    setIsAuth(true)
  }

  const handleLogout = () => {
    api.logout()
    setIsAuth(false)
    setUser(null)
  }

  const handleOnboardingComplete = (updatedProfile) => {
    // Update profile immediately with data from onboarding
    if (updatedProfile) {
      setUser(updatedProfile)
    } else {
      api.getProfile().then(setUser).catch(() => {})
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div className="loading-state">Cargando Fluentify...</div>
      </div>
    )
  }

  // Check if user needs onboarding (no professional context selected)
  const needsOnboarding = isAuth && user && !user.onboarding_completed

  return (
    <BrowserRouter>
      <div className="bg-orbs">
        <div className="orb" />
        <div className="orb" />
        <div className="orb" />
      </div>
      <Routes>
        <Route path="/login" element={
          isAuth ? <Navigate to={needsOnboarding ? "/onboarding" : "/dashboard"} replace /> :
          <Login onLogin={handleLogin} onRegister={handleRegister} />
        } />
        <Route path="/onboarding" element={
          <ProtectedRoute isAuth={isAuth}>
            <Onboarding user={user} onComplete={handleOnboardingComplete} />
          </ProtectedRoute>
        } />
        <Route path="/" element={
          <ProtectedRoute isAuth={isAuth}>
            {needsOnboarding ? <Navigate to="/onboarding" replace /> : <Layout user={user} onLogout={handleLogout} />}
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard user={user} />} />
          <Route path="practice" element={<Practice user={user} />} />
          <Route path="practice/session" element={<Chat user={user} />} />
          <Route path="history" element={<History />} />
          <Route path="progress" element={<Progress />} />
          <Route path="achievements" element={<Achievements />} />
          <Route path="profile" element={<Profile user={user} setUser={setUser} />} />
          <Route path="voice" element={<Voice />} />
          <Route path="writing" element={<Writing />} />
        </Route>
        <Route path="*" element={<Navigate to={isAuth ? (needsOnboarding ? "/onboarding" : "/dashboard") : "/login"} replace />} />
      </Routes>
    </BrowserRouter>
  )
}
