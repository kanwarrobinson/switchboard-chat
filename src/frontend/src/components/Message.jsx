import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Highlight, themes } from 'prism-react-renderer'
import { User, Bot } from 'lucide-react'
import ModelBadge from './ModelBadge'

export default function Message({ message, showMetadata }) {
  const isUser = message.role === 'user'

  const CodeBlock = ({ children, className }) => {
    const match = /language-(\w+)/.exec(className || '')
    const language = match ? match[1] : ''

    if (!language) {
      return <code className="bg-gray-100 text-red-600 px-1 py-0.5 rounded text-sm">{children}</code>
    }

    return (
      <Highlight theme={themes.vsDark} code={String(children).trim()} language={language}>
        {({ className, style, tokens, getLineProps, getTokenProps }) => (
          <pre className={className} style={style}>
            {tokens.map((line, i) => (
              <div key={i} {...getLineProps({ line })}>
                {line.map((token, key) => (
                  <span key={key} {...getTokenProps({ token })} />
                ))}
              </div>
            ))}
          </pre>
        )}
      </Highlight>
    )
  }

  return (
    <div className={`flex gap-3 message-enter ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? 'bg-primary-500' : 'bg-gray-200'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-gray-600" />
        )}
      </div>

      {/* Message bubble */}
      <div className={`flex flex-col max-w-[70%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`px-4 py-3 rounded-2xl ${
          isUser
            ? 'bg-primary-500 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}>
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="text-sm markdown-body">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code: CodeBlock
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Metadata badges for AI messages */}
        {!isUser && (
          <ModelBadge
            model={message.model_used}
            provider={message.provider}
            queryType={message.query_type}
            fallbackTriggered={message.fallback_triggered}
            show={showMetadata}
          />
        )}

        {/* Timestamp */}
        <span className="text-xs text-gray-400 mt-1 px-1">
          {message.timestamp ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
        </span>
      </div>
    </div>
  )
}
