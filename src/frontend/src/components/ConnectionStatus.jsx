export default function ConnectionStatus({ isConnected }) {
  return (
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
      <span className="text-xs text-gray-600">
        {isConnected ? 'Online' : 'Offline'}
      </span>
    </div>
  )
}
