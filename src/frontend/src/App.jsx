import { useState, useEffect } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import ChatContainer from './components/ChatContainer'
import { chatApi } from './api/chat'
import { storage } from './utils/storage'
import { generateId } from './utils/generateId'

export default function App() {
  // State
  const [messages, setMessages] = useState([])
  const [sessions, setSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [isTyping, setIsTyping] = useState(false)
  const [isConnected, setIsConnected] = useState(true)
  const [showMetadata, setShowMetadata] = useState(storage.getShowMetadata())
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [error, setError] = useState(null)

  // Initialize: Load saved session on mount
  useEffect(() => {
    const savedSessionId = storage.getCurrentSession()
    const savedSessions = storage.getSessions()
    setSessions(savedSessions)

    if (savedSessionId) {
      const savedSession = savedSessions.find(s => s.session_id === savedSessionId)
      if (savedSession) {
        setCurrentSessionId(savedSessionId)
        setMessages(savedSession.messages || [])
      }
    }

    // Check backend health
    checkHealth()
  }, [])

  // Check backend health
  const checkHealth = async () => {
    try {
      await chatApi.health()
      setIsConnected(true)
    } catch (err) {
      setIsConnected(false)
      console.error('Health check failed:', err)
    }
  }

  // Send message to backend
  const handleSendMessage = async (messageText) => {
    if (!messageText.trim()) return

    // Create user message
    const userMessage = {
      message_id: generateId(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
      query_type: null,
      model_used: null
    }

    // Add user message to UI immediately
    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)
    setError(null)

    try {
      // Send to backend
      const response = await chatApi.sendMessage(messageText, currentSessionId)

      // Create assistant message from response
      const assistantMessage = {
        message_id: generateId(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        model_used: response.model_used,
        provider: response.provider,
        query_type: response.query_type,
        fallback_triggered: response.fallback_triggered || false
      }

      // Update session ID if this was a new conversation
      const newSessionId = response.session_id || currentSessionId
      if (!currentSessionId) {
        setCurrentSessionId(newSessionId)
        storage.setCurrentSession(newSessionId)
      }

      // Update messages
      const newMessages = [...messages, userMessage, assistantMessage]
      setMessages(newMessages)

      // Save session to localStorage
      const sessionData = {
        session_id: newSessionId,
        messages: newMessages,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: newMessages.length
      }
      storage.saveSession(sessionData)

      // Update sessions list
      setSessions(prev => {
        const filtered = prev.filter(s => s.session_id !== newSessionId)
        return [sessionData, ...filtered]
      })

      setIsConnected(true)
    } catch (err) {
      console.error('Failed to send message:', err)
      setError(err.message || 'Failed to send message. Please try again.')
      setIsConnected(false)

      // Remove the user message on error
      setMessages(prev => prev.filter(m => m.message_id !== userMessage.message_id))
    } finally {
      setIsTyping(false)
    }
  }

  // Start a new chat
  const handleNewChat = () => {
    setCurrentSessionId(null)
    setMessages([])
    storage.clearCurrentSession()
    setError(null)
  }

  // Select an existing session
  const handleSelectSession = (sessionId) => {
    const session = sessions.find(s => s.session_id === sessionId)
    if (session) {
      setCurrentSessionId(sessionId)
      setMessages(session.messages || [])
      storage.setCurrentSession(sessionId)
      setError(null)
    }
  }

  // Delete a session
  const handleDeleteSession = (sessionId) => {
    storage.deleteSession(sessionId)
    setSessions(prev => prev.filter(s => s.session_id !== sessionId))

    // If deleting current session, start new chat
    if (sessionId === currentSessionId) {
      handleNewChat()
    }
  }

  // Toggle metadata visibility
  const handleToggleMetadata = () => {
    const newValue = !showMetadata
    setShowMetadata(newValue)
    storage.setShowMetadata(newValue)
  }

  // Toggle sidebar (mobile)
  const handleToggleSidebar = () => {
    setIsSidebarOpen(prev => !prev)
  }

  const handleCloseSidebar = () => {
    setIsSidebarOpen(false)
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        onNewChat={handleNewChat}
        isOpen={isSidebarOpen}
        onClose={handleCloseSidebar}
      />

      {/* Main Content */}
      <div className="flex flex-col flex-1">
        <Header
          isConnected={isConnected}
          showMetadata={showMetadata}
          onToggleMetadata={handleToggleMetadata}
          onToggleSidebar={handleToggleSidebar}
        />

        {error && (
          <div className="px-4 py-3 mx-4 mt-4 text-sm text-red-700 bg-red-100 border border-red-300 rounded-lg">
            {error}
          </div>
        )}

        <ChatContainer
          messages={messages}
          isTyping={isTyping}
          showMetadata={showMetadata}
          onSendMessage={handleSendMessage}
          disabled={isTyping}
        />
      </div>
    </div>
  )
}
