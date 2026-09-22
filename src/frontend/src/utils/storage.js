// LocalStorage utilities for session management

const STORAGE_KEYS = {
  CURRENT_SESSION: 'switchboard_current_session',
  SESSIONS: 'switchboard_sessions',
  SHOW_METADATA: 'switchboard_show_metadata'
}

export const storage = {
  getCurrentSession: () => {
    return localStorage.getItem(STORAGE_KEYS.CURRENT_SESSION)
  },

  setCurrentSession: (sessionId) => {
    localStorage.setItem(STORAGE_KEYS.CURRENT_SESSION, sessionId)
  },

  clearCurrentSession: () => {
    localStorage.removeItem(STORAGE_KEYS.CURRENT_SESSION)
  },

  getSessions: () => {
    const sessions = localStorage.getItem(STORAGE_KEYS.SESSIONS)
    return sessions ? JSON.parse(sessions) : []
  },

  saveSession: (session) => {
    const sessions = storage.getSessions()
    const existingIndex = sessions.findIndex(s => s.session_id === session.session_id)

    if (existingIndex >= 0) {
      sessions[existingIndex] = session
    } else {
      sessions.unshift(session)
    }

    // Keep only last 50 sessions
    const trimmed = sessions.slice(0, 50)
    localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(trimmed))
  },

  deleteSession: (sessionId) => {
    const sessions = storage.getSessions()
    const filtered = sessions.filter(s => s.session_id !== sessionId)
    localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(filtered))
  },

  getShowMetadata: () => {
    const value = localStorage.getItem(STORAGE_KEYS.SHOW_METADATA)
    return value === null ? true : value === 'true'
  },

  setShowMetadata: (show) => {
    localStorage.setItem(STORAGE_KEYS.SHOW_METADATA, show.toString())
  }
}
