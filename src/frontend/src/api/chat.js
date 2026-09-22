import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const chatApi = {
  // Send a chat message
  sendMessage: async (message, sessionId = null) => {
    const response = await api.post('/chat', {
      message,
      session_id: sessionId
    })
    return response.data
  },

  // Get all sessions
  getSessions: async () => {
    const response = await api.get('/sessions')
    return response.data
  },

  // Get a specific session with full message history
  getSession: async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}`)
    return response.data
  },

  // Health check
  health: async () => {
    const response = await api.get('/health')
    return response.data
  }
}

export default chatApi
