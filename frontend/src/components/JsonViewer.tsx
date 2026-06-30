import { useState } from 'react'
import { ChevronDown, ChevronUp, Copy, Check } from 'lucide-react'

interface JsonViewerProps {
  data: Record<string, unknown> | null
  title?: string
}

export default function JsonViewer({ data, title }: JsonViewerProps) {
  const [collapsed, setCollapsed] = useState(false)
  const [copied, setCopied] = useState(false)

  if (!data) {
    return (
      <div className="bg-dark-800 rounded-xl p-4 text-dark-500 text-sm">
        No data available
      </div>
    )
  }

  const formatted = JSON.stringify(data, null, 2)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(formatted)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-dark-800 rounded-xl overflow-hidden border border-dark-700">
      <div className="flex items-center justify-between px-4 py-3 bg-dark-900/50 border-b border-dark-700">
        <span className="text-sm font-medium text-dark-300">{title || 'JSON View'}</span>
        <div className="flex items-center gap-2">
          <button onClick={handleCopy} className="p-1.5 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-dark-200 transition-colors">
            {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
          </button>
          <button onClick={() => setCollapsed(!collapsed)} className="p-1.5 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-dark-200 transition-colors">
            {collapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>
      {!collapsed && (
        <pre className="p-4 text-sm font-mono text-green-400 overflow-x-auto max-h-96 overflow-y-auto">
          {formatted}
        </pre>
      )}
    </div>
  )
}
