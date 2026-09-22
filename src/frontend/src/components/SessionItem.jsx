import { MessageSquare, Trash2 } from 'lucide-react'

export default function SessionItem({ session, isActive, onClick, onDelete }) {
  const getPreviewText = () => {
    if (session.messages && session.messages.length > 0) {
      const lastMessage = session.messages[session.messages.length - 1]
      return lastMessage.content.substring(0, 50) + (lastMessage.content.length > 50 ? '...' : '')
    }
    return 'New conversation'
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div
      className={`group flex items-start gap-3 px-3 py-3 rounded-lg cursor-pointer transition-colors ${
        isActive ? 'bg-primary-50 border border-primary-200' : 'hover:bg-gray-50'
      }`}
      onClick={onClick}
    >
      <MessageSquare className={`w-4 h-4 flex-shrink-0 mt-0.5 ${isActive ? 'text-primary-600' : 'text-gray-400'}`} />

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-800 truncate">
          {getPreviewText()}
        </p>
        <p className="text-xs text-gray-500">
          {formatDate(session.created_at || session.updated_at)}
          {session.message_count && ` • ${session.message_count} messages`}
        </p>
      </div>

      <button
        onClick={(e) => {
          e.stopPropagation()
          onDelete(session.session_id)
        }}
        className="flex-shrink-0 p-1 text-gray-400 transition-colors opacity-0 hover:text-red-600 group-hover:opacity-100"
        title="Delete session"
      >
        <Trash2 className="w-4 h-4" />
      </button>
    </div>
  )
}
