import { MessageSquare } from 'lucide-react'

export default function WelcomeScreen({ onSuggestedQuestion }) {
  const suggestedQuestions = [
    "How do I reset my password?",
    "What are your support hours?",
    "I need help with billing",
    "How do I contact a human agent?"
  ]

  return (
    <div className="flex flex-col items-center justify-center h-full px-4 py-12">
      <div className="flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-primary-100">
        <MessageSquare className="w-8 h-8 text-primary-600" />
      </div>

      <h2 className="mb-2 text-2xl font-bold text-gray-800">
        Welcome to Switchboard Chat
      </h2>

      <p className="mb-8 text-center text-gray-600">
        AI-powered customer support. Ask me anything!
      </p>

      <div className="w-full max-w-md">
        <p className="mb-3 text-sm font-medium text-gray-700">Suggested questions:</p>
        <div className="grid gap-2">
          {suggestedQuestions.map((question, index) => (
            <button
              key={index}
              onClick={() => onSuggestedQuestion(question)}
              className="px-4 py-3 text-sm text-left transition-colors border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300"
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
