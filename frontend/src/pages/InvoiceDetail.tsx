import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Download, FileText, FileSpreadsheet, Clock, Cpu, HardDrive, Trash2, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import JsonViewer from '../components/JsonViewer'
import { useInvoice } from '../hooks/useData'
import { api } from '../services/api'

export default function InvoiceDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const invoiceId = id ? parseInt(id) : null
  const { data: invoice, loading, error, refresh } = useInvoice(invoiceId)

  const handleDelete = async () => {
    if (!confirm('Delete this invoice permanently?')) return
    if (!invoiceId) return
    try {
      await api.deleteInvoice(invoiceId)
      toast.success('Invoice deleted')
      navigate('/invoices')
    } catch {
      toast.error('Failed to delete')
    }
  }

  const handleReprocess = async () => {
    if (!invoiceId) return
    try {
      await api.processInvoice(invoiceId)
      toast.success('Reprocessing started')
      refresh()
    } catch {
      toast.error('Failed to reprocess')
    }
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-dark-800 rounded-xl p-8 border border-dark-700 animate-pulse space-y-4">
          <div className="h-8 bg-dark-700 rounded w-48" />
          <div className="h-4 bg-dark-700 rounded w-64" />
          <div className="h-40 bg-dark-700 rounded" />
        </div>
      </div>
    )
  }

  if (error || !invoice) {
    return (
      <div className="max-w-4xl mx-auto text-center">
        <div className="bg-red-900/20 border border-red-800 rounded-xl p-8">
          <p className="text-red-400">{error || 'Invoice not found'}</p>
          <Link to="/invoices" className="inline-block mt-4 text-blue-400 hover:underline">Back to invoices</Link>
        </div>
      </div>
    )
  }

  const sj = invoice.structured_json

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/invoices" className="p-2 rounded-lg hover:bg-dark-800 text-dark-400 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-dark-100">{sj?.vendor || 'Invoice Details'}</h1>
          <p className="text-dark-500 text-sm">{invoice.filename}</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleReprocess} className="flex items-center gap-1.5 px-3 py-1.5 bg-dark-800 hover:bg-dark-700 rounded-lg text-sm text-dark-300 transition-colors border border-dark-700">
            <RefreshCw className="w-4 h-4" />
            Reprocess
          </button>
          <button onClick={handleDelete} className="flex items-center gap-1.5 px-3 py-1.5 bg-dark-800 hover:bg-red-900/50 rounded-lg text-sm text-red-400 transition-colors border border-dark-700">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4 flex-wrap">
        <span className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-sm ${
          invoice.status === 'completed' ? 'bg-green-500/10 text-green-400' :
          invoice.status === 'failed' ? 'bg-red-500/10 text-red-400' :
          invoice.status === 'processing' ? 'bg-blue-500/10 text-blue-400' :
          'bg-yellow-500/10 text-yellow-400'
        }`}>
          {invoice.status}
        </span>
        {invoice.processing_time_ms && (
          <span className="flex items-center gap-1.5 text-sm text-dark-400">
            <Clock className="w-4 h-4" />
            {(invoice.processing_time_ms / 1000).toFixed(1)}s
          </span>
        )}
        {invoice.cpu_usage !== null && (
          <span className="flex items-center gap-1.5 text-sm text-dark-400">
            <Cpu className="w-4 h-4" />
            CPU: {invoice.cpu_usage.toFixed(0)}%
          </span>
        )}
        {invoice.memory_usage !== null && (
          <span className="flex items-center gap-1.5 text-sm text-dark-400">
            <HardDrive className="w-4 h-4" />
            RAM: {invoice.memory_usage.toFixed(0)}%
          </span>
        )}
      </div>

      {invoice.status === 'failed' && invoice.error_message && (
        <div className="bg-red-900/20 border border-red-800 rounded-xl p-4">
          <p className="text-red-400 text-sm">{invoice.error_message}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sj && (
          <div className="bg-dark-800 rounded-xl p-6 border border-dark-700">
            <h3 className="text-lg font-semibold text-dark-100 mb-4">Invoice Data</h3>
            <dl className="space-y-3">
              <div><dt className="text-sm text-dark-500">Vendor</dt><dd className="text-dark-100">{sj.vendor || '—'}</dd></div>
              <div><dt className="text-sm text-dark-500">Invoice #</dt><dd className="text-dark-100">{sj.invoice_number || '—'}</dd></div>
              <div><dt className="text-sm text-dark-500">Date</dt><dd className="text-dark-100">{sj.invoice_date || '—'}</dd></div>
              <div><dt className="text-sm text-dark-500">Subtotal</dt><dd className="text-dark-100">{sj.subtotal || '—'}</dd></div>
              <div><dt className="text-sm text-dark-500">Tax</dt><dd className="text-dark-100">{sj.tax || '—'}</dd></div>
              <div><dt className="text-sm text-dark-500">Grand Total</dt><dd className="text-dark-100 text-lg font-bold">{sj.grand_total || '—'}</dd></div>
              <div><dt className="text-sm text-dark-500">Payment</dt><dd className="text-dark-100">{sj.payment_method || '—'}</dd></div>
            </dl>

            {sj.items && sj.items.length > 0 && (
              <div className="mt-6">
                <h4 className="text-sm font-medium text-dark-400 mb-2">Items ({sj.items.length})</h4>
                <div className="space-y-2">
                  {sj.items.map((item, idx) => (
                    <div key={idx} className="bg-dark-900/50 rounded-lg p-3 text-sm">
                      <div className="font-medium text-dark-200">{item.name || 'Item'}</div>
                      <div className="flex gap-4 mt-1 text-dark-500">
                        <span>Qty: {item.quantity || '—'}</span>
                        <span>Price: {item.unit_price || '—'}</span>
                        <span>Total: {item.total || '—'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="space-y-4">
          <JsonViewer data={sj as Record<string, unknown>} title="Structured JSON" />

          {invoice.original_text && (
            <div className="bg-dark-800 rounded-xl p-4 border border-dark-700">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-medium text-dark-400">OCR Raw Text</h4>
                <span className="text-xs text-dark-500">{invoice.original_text.length} chars</span>
              </div>
              <pre className="text-xs text-dark-400 max-h-32 overflow-y-auto whitespace-pre-wrap font-mono">
                {invoice.original_text.slice(0, 1000)}
                {invoice.original_text.length > 1000 && '\n...'}
              </pre>
            </div>
          )}

          {invoice.logs && invoice.logs.length > 0 && (
            <div className="bg-dark-800 rounded-xl p-4 border border-dark-700">
              <h4 className="text-sm font-medium text-dark-400 mb-2">Processing Logs</h4>
              <div className="space-y-1.5">
                {invoice.logs.map((log) => (
                  <div key={log.id} className="flex items-center gap-2 text-xs">
                    <span className="text-dark-600">{new Date(log.created_at).toLocaleTimeString()}</span>
                    <span className={`px-1.5 py-0.5 rounded text-xs ${
                      log.stage === 'error' ? 'bg-red-500/10 text-red-400' :
                      log.stage === 'complete' ? 'bg-green-500/10 text-green-400' :
                      'bg-blue-500/10 text-blue-400'
                    }`}>{log.stage}</span>
                    <span className="text-dark-400">{log.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {sj && (
        <div className="flex items-center gap-3 flex-wrap">
          <a
            href={api.getExportJsonUrl(invoice.id)}
            download
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
          >
            <FileText className="w-4 h-4" />
            Export JSON
          </a>
          <a
            href={api.getExportCsvUrl(invoice.id)}
            download
            className="flex items-center gap-2 px-4 py-2 bg-dark-700 hover:bg-dark-600 rounded-lg text-sm text-dark-200 transition-colors border border-dark-600"
          >
            <FileSpreadsheet className="w-4 h-4" />
            Export CSV
          </a>
          <a
            href={api.getExportOcrUrl(invoice.id)}
            download
            className="flex items-center gap-2 px-4 py-2 bg-dark-700 hover:bg-dark-600 rounded-lg text-sm text-dark-200 transition-colors border border-dark-600"
          >
            <Download className="w-4 h-4" />
            Download OCR Text
          </a>
        </div>
      )}
    </div>
  )
}
