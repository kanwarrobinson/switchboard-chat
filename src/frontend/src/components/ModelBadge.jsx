import { Bot, Zap, AlertTriangle } from 'lucide-react'

export default function ModelBadge({ model, provider, queryType, fallbackTriggered, show }) {
  if (!show) return null

  const getProviderColor = (provider) => {
    switch (provider) {
      case 'openai':
        return 'bg-green-50 text-green-700 border-green-200'
      case 'anthropic':
        return 'bg-purple-50 text-purple-700 border-purple-200'
      case 'self-hosted':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const getQueryTypeColor = (type) => {
    return type === 'escalation'
      ? 'bg-orange-50 text-orange-700 border-orange-200'
      : 'bg-gray-50 text-gray-600 border-gray-200'
  }

  return (
    <div className="flex flex-wrap items-center gap-2 mt-2">
      {model && (
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium border rounded-full ${getProviderColor(provider)}`}>
          <Bot className="w-3 h-3" />
          {model}
        </span>
      )}

      {provider && (
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium border rounded-full ${getProviderColor(provider)}`}>
          {provider}
        </span>
      )}

      {queryType && (
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium border rounded-full ${getQueryTypeColor(queryType)}`}>
          <Zap className="w-3 h-3" />
          {queryType.toUpperCase()}
        </span>
      )}

      {fallbackTriggered && (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-yellow-50 text-yellow-700 border border-yellow-200 rounded-full">
          <AlertTriangle className="w-3 h-3" />
          Failover
        </span>
      )}
    </div>
  )
}
