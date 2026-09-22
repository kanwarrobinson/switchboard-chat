import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'

export default function InputArea({ onSendMessage, disabled }) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="p-4 border-t border-gray-200 bg-white">
      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={disabled}
          rows={1}
          className="flex-1 px-4 py-3 text-sm bg-gray-50 border border-gray-200 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed max-h-32 overflow-y-auto scrollbar-thin"
        />

        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="flex items-center justify-center flex-shrink-0 w-12 h-12 text-white transition-colors rounded-full bg-primary-500 hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>

      <p className="mt-2 text-xs text-center text-gray-400">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  )
}
