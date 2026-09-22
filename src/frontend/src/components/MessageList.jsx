import { useEffect, useRef } from 'react'
import Message from './Message'
import TypingIndicator from './TypingIndicator'

export default function MessageList({ messages, isTyping, showMetadata }) {
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin">
      <div className="px-4 py-6 space-y-6">
        {messages.map((message, index) => (
          <Message
            key={message.message_id || index}
            message={message}
            showMetadata={showMetadata}
          />
        ))}

        {isTyping && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 w-8 h-8" />
            <TypingIndicator />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}
