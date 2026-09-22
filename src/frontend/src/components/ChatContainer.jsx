import MessageList from './MessageList'
import InputArea from './InputArea'
import WelcomeScreen from './WelcomeScreen'

export default function ChatContainer({
  messages,
  isTyping,
  showMetadata,
  onSendMessage,
  disabled
}) {
  const hasMessages = messages.length > 0

  return (
    <div className="flex flex-col flex-1 bg-white">
      {hasMessages ? (
        <>
          <MessageList
            messages={messages}
            isTyping={isTyping}
            showMetadata={showMetadata}
          />
          <InputArea
            onSendMessage={onSendMessage}
            disabled={disabled}
          />
        </>
      ) : (
        <>
          <WelcomeScreen onSuggestedQuestion={onSendMessage} />
          <InputArea
            onSendMessage={onSendMessage}
            disabled={disabled}
          />
        </>
      )}
    </div>
  )
}
