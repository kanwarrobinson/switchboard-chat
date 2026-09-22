import { PlusCircle, X } from 'lucide-react'
import SessionList from './SessionList'

export default function Sidebar({
  sessions,
  currentSessionId,
  onSelectSession,
  onDeleteSession,
  onNewChat,
  isOpen,
  onClose
}) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed md:relative inset-y-0 left-0 z-50 w-80 bg-white border-r border-gray-200 flex flex-col transition-transform duration-300 md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-800">Conversations</h2>

          <button
            onClick={onClose}
            className="p-1 text-gray-400 transition-colors rounded hover:bg-gray-100 md:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="px-4 py-3 border-b border-gray-200">
          <button
            onClick={() => {
              onNewChat()
              onClose()
            }}
            className="flex items-center justify-center w-full gap-2 px-4 py-2 text-sm font-medium text-white transition-colors rounded-lg bg-primary-500 hover:bg-primary-600"
          >
            <PlusCircle className="w-4 h-4" />
            New Chat
          </button>
        </div>

        {/* Session List */}
        <div className="flex-1 px-4 py-4 overflow-y-auto scrollbar-thin">
          <SessionList
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSelectSession={(sessionId) => {
              onSelectSession(sessionId)
              onClose()
            }}
            onDeleteSession={onDeleteSession}
          />
        </div>

        {/* Footer */}
        <div className="px-4 py-3 text-xs text-center text-gray-500 border-t border-gray-200">
          Powered by Switchboard
        </div>
      </div>
    </>
  )
}
