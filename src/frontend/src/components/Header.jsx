import { MessageSquare, Eye, EyeOff, Menu } from 'lucide-react'
import ConnectionStatus from './ConnectionStatus'

export default function Header({ isConnected, showMetadata, onToggleMetadata, onToggleSidebar }) {
  return (
    <div className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 text-gray-600 transition-colors rounded-lg hover:bg-gray-100 md:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <MessageSquare className="w-6 h-6 text-primary-600" />
          <div>
            <h1 className="text-lg font-bold text-gray-800">Switchboard Chat</h1>
            <p className="text-xs text-gray-500">AI-Powered Support</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={onToggleMetadata}
          className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-gray-600 transition-colors border border-gray-200 rounded-lg hover:bg-gray-50"
          title={showMetadata ? 'Hide model info' : 'Show model info'}
        >
          {showMetadata ? (
            <>
              <Eye className="w-4 h-4" />
              <span className="hidden sm:inline">Metadata</span>
            </>
          ) : (
            <>
              <EyeOff className="w-4 h-4" />
              <span className="hidden sm:inline">Metadata</span>
            </>
          )}
        </button>

        <ConnectionStatus isConnected={isConnected} />
      </div>
    </div>
  )
}
