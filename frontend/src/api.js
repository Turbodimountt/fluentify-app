/**
 * Fluentify — API Client
 * Handles all HTTP communication with the FastAPI backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE;
    this.accessToken = localStorage.getItem('fluentify_access_token');
    this.refreshToken = localStorage.getItem('fluentify_refresh_token');
  }

  setTokens(access, refresh) {
    this.accessToken = access;
    this.refreshToken = refresh;
    localStorage.setItem('fluentify_access_token', access);
    localStorage.setItem('fluentify_refresh_token', refresh);
  }

  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('fluentify_access_token');
    localStorage.removeItem('fluentify_refresh_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.accessToken && { Authorization: `Bearer ${this.accessToken}` }),
      ...options.headers,
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401 && this.refreshToken) {
      const refreshed = await this.tryRefreshToken();
      if (refreshed) {
        headers.Authorization = `Bearer ${this.accessToken}`;
        return fetch(url, { ...options, headers });
      }
    }

    return response;
  }

  async tryRefreshToken() {
    try {
      const res = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });
      if (res.ok) {
        const data = await res.json();
        this.setTokens(data.access_token, data.refresh_token);
        return true;
      }
    } catch { }
    this.clearTokens();
    return false;
  }

  // Auth
  async register(email, password, displayName) {
    const res = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, display_name: displayName }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Registration failed');
    return res.json();
  }

  async login(email, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (res.ok) {
      const data = await res.json();
      this.setTokens(data.access_token, data.refresh_token);
      return data;
    }
    throw new Error((await res.json()).detail || 'Login failed');
  }

  async logout() {
    this.clearTokens();
  }

  // Profile
  async getProfile() {
    const res = await this.request('/users/me/profile');
    if (!res.ok) throw new Error('Profile fetch failed');
    return res.json();
  }

  async updateProfile(data) {
    const res = await this.request('/users/me/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Profile update failed');
    return res.json();
  }

  async completeOnboarding(data) {
    const res = await this.request('/users/me/onboarding', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Onboarding failed');
    return res.json();
  }

  // Contexts & Scenarios
  async getProfessionalContexts() {
    const res = await this.request('/users/professional-contexts');
    if (!res.ok) return [];
    return res.json();
  }

  async getScenarios(contextSlug) {
    const res = await this.request(`/api/v1/scenarios/${contextSlug}`);
    if (!res.ok) return [];
    return res.json();
  }

  // Conversation
  async sendMessage(data) {
    const res = await this.request('/api/v1/conversation', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Message send failed');
    return res.json();
  }

  async endSession(sessionId) {
    const res = await this.request(`/api/v1/sessions/${sessionId}/end`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('End session failed');
    return res.json();
  }

  async getSessions(limit = 20, offset = 0) {
    const res = await this.request(`/api/v1/sessions?limit=${limit}&offset=${offset}`);
    if (!res.ok) return { sessions: [], total: 0 };
    return res.json();
  }

  // Progress
  async getStats() {
    const res = await this.request('/progress/stats');
    if (!res.ok) {
      return {
        total_xp: 0, current_streak: 0, max_streak: 0,
        user_level: 'Explorador', sessions_count: 0,
        nodes_mastered: 0, nodes_pending_review: 0,
        total_practice_minutes: 0, error_rate: 0,
      };
    }
    return res.json();
  }

  async getKnowledgeNodes() {
    const res = await this.request('/progress/nodes');
    if (!res.ok) return { nodes: [], total: 0 };
    return res.json();
  }

  async getAchievements() {
    const res = await this.request('/achievements');
    if (!res.ok) {
      return { unlocked: [], available: [], total_unlocked: 0, total_available: 0 };
    }
    return res.json();
  }

  // Voice
  async transcribeAudio(audioBlob, languageCode = 'en-US') {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('language_code', languageCode);

    const res = await fetch(`${this.baseUrl}/api/v1/voice/stt`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
      },
      body: formData,
    });
    if (!res.ok) throw new Error('STT failed');
    return res.json();
  }

  async textToSpeech(text, language = 'en') {
    const res = await this.request('/api/v1/voice/tts', {
      method: 'POST',
      body: JSON.stringify({ text, language }),
    });
    if (!res.ok) throw new Error('TTS failed');
    return res.json();
  }

  async analyzePronunciation(audioBase64, expectedText, languageCode = 'en-US') {
    const res = await this.request('/api/v1/voice/pronunciation', {
      method: 'POST',
      body: JSON.stringify({
        audio_base64: audioBase64,
        expected_text: expectedText,
        language_code: languageCode,
      }),
    });
    if (!res.ok) throw new Error('Pronunciation analysis failed');
    return res.json();
  }

  // Writing
  async analyzeStrokes(strokes, targetCharacter, writingSystem = 'kanji') {
    const res = await this.request('/api/v1/writing/analyze', {
      method: 'POST',
      body: JSON.stringify({
        strokes,
        target_character: targetCharacter,
        writing_system: writingSystem,
      }),
    });
    if (!res.ok) throw new Error('Stroke analysis failed');
    return res.json();
  }

  async getCharacters(writingSystem, level = 'beginner') {
    const res = await this.request(`/api/v1/writing/characters/${writingSystem}?level=${level}`);
    if (!res.ok) return { characters: [] };
    return res.json();
  }

  // WebSocket
  createConversationWS(config) {
    const wsUrl = this.baseUrl.replace('http', 'ws') + '/ws/conversation';
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => {
      ws.send(JSON.stringify({
        token: this.accessToken,
        ...config,
      }));
    };
    return ws;
  }
}

export const api = new ApiClient();
export default api;
