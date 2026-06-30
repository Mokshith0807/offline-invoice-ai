import { useNavigate } from 'react-router-dom'
import { ExternalLink, Trash2, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import type { Invoice } from '../types'
import { api } from '../services/api'
import toast from 'react-hot-toast'

interface InvoiceCardProps {
  invoice: Invoice
  onDelete: () => void
}

const statusIcons = {
  pending: Clock,
  processing: Loader2,
  completed: CheckCircle,
  failed: XCircle,
}

const statusColors = {
  pending: 'text-yellow-400',
  processing: 'text-blue-400',
  completed: 'text-green-400',
  failed: 'text-red-400',
}

export default function InvoiceCard({ invoice, onDelete }: InvoiceCardProps) {
  const navigate = useNavigate()
  const StatusIcon = statusIcons[invoice.status]

  const handleDelete = async () => {
    if (!confirm('Delete this invoice?')) return
    try {
      await api.deleteInvoice(invoice.id)
      toast.success('Invoice deleted')
      onDelete()
    } catch (e) {
      toast.error('Failed to delete')
    }
  }

  const vendor = invoice.structured_json?.vendor || 'Unknown Vendor'
  const total = invoice.structured_json?.grand_total || '—'

  return (
    <div className="bg-dark-800 rounded-xl border border-dark-700 p-5 hover:border-dark-500 transition-all">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-dark-100 truncate">{vendor}</h3>
          <p className="text-sm text-dark-500 truncate mt-0.5">{invoice.filename}</p>
        </div>
        <div className={`flex items-center gap-1.5 text-sm ${statusColors[invoice.status]}`}>
          <StatusIcon className={`w-4 h-4 ${invoice.status === 'processing' ? 'animate-spin' : ''}`} />
          <span className="capitalize">{invoice.status}</span>
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm text-dark-400 mb-4">
        <span>Total: <span className="text-dark-200 font-medium">{total}</span></span>
        {invoice.invoice_number && (
          <span>#{invoice.invoice_number}</span>
        )}
        {invoice.processing_time_ms && (
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {(invoice.processing_time_ms / 1000).toFixed(1)}s
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => navigate(`/invoice/${invoice.id}`)}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-dark-700 hover:bg-dark-600 rounded-lg text-sm text-dark-300 transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          View
        </button>
        <button
          onClick={handleDelete}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-dark-700 hover:bg-red-900/50 rounded-lg text-sm text-dark-400 hover:text-red-400 transition-colors ml-auto"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
