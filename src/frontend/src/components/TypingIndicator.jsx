export default function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 px-4 py-3 bg-gray-100 rounded-2xl w-fit">
      <div className="flex gap-1">
        <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
      </div>
      <span className="text-sm text-gray-500">AI is thinking...</span>
    </div>
  )
}
