import SessionItem from './SessionItem'

export default function SessionList({ sessions, currentSessionId, onSelectSession, onDeleteSession }) {
  if (sessions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-32 text-center">
        <p className="text-sm text-gray-500">No conversations yet</p>
        <p className="text-xs text-gray-400">Start chatting to see history</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {sessions.map((session) => (
        <SessionItem
          key={session.session_id}
          session={session}
          isActive={session.session_id === currentSessionId}
          onClick={() => onSelectSession(session.session_id)}
          onDelete={onDeleteSession}
        />
      ))}
    </div>
  )
}
