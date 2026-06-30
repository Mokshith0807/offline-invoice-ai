import { BarChart3, FileText, Activity, Clock } from 'lucide-react'
import StatCard from '../components/StatCard'
import InvoiceCard from '../components/InvoiceCard'
import UploadZone from '../components/UploadZone'
import { useDashboard } from '../hooks/useData'
import { useHealth } from '../hooks/useData'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { data, loading, error, refresh } = useDashboard()
  const { data: health } = useHealth()

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-dark-100">Dashboard</h1>
          <p className="text-dark-500 mt-1">Offline Invoice Structurer AI</p>
        </div>
        <div className="flex items-center gap-3 text-sm">
          {health && (
            <>
              <span className={`flex items-center gap-1.5 ${health.model_loaded ? 'text-green-400' : 'text-yellow-400'}`}>
                <Activity className="w-4 h-4" />
                {health.model_loaded ? 'Model Ready' : 'No Model'}
              </span>
              <span className={`flex items-center gap-1.5 ${health.ocr_available ? 'text-green-400' : 'text-red-400'}`}>
                <FileText className="w-4 h-4" />
                {health.ocr_available ? 'OCR Ready' : 'OCR Missing'}
              </span>
            </>
          )}
        </div>
      </div>

      <UploadZone onUploadComplete={refresh} />

      {error ? (
        <div className="bg-red-900/20 border border-red-800 rounded-xl p-6 text-center">
          <p className="text-red-400">{error}</p>
          <button onClick={refresh} className="mt-3 text-sm text-blue-400 hover:underline">Retry</button>
        </div>
      ) : loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-dark-800 rounded-xl p-5 border border-dark-700 animate-pulse">
              <div className="h-10 w-10 bg-dark-700 rounded-lg mb-3" />
              <div className="h-4 bg-dark-700 rounded w-20 mb-2" />
              <div className="h-7 bg-dark-700 rounded w-12" />
            </div>
          ))}
        </div>
      ) : data ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard title="Total Invoices" value={data.total_invoices} icon="invoices" />
            <StatCard title="Completed" value={data.completed} icon="completed" />
            <StatCard title="Processing" value={data.processing} icon="processing" />
            <StatCard title="Failed" value={data.failed} icon="failed" />
          </div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-dark-100 flex items-center gap-2">
                <Clock className="w-5 h-5 text-dark-400" />
                Recent Activity
              </h2>
              <Link to="/invoices" className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                View All →
              </Link>
            </div>
            {data.latest_invoices.length === 0 ? (
              <div className="bg-dark-800 rounded-xl p-8 text-center">
                <BarChart3 className="w-12 h-12 mx-auto text-dark-600 mb-3" />
                <p className="text-dark-500">No invoices yet. Upload one to get started.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.latest_invoices.map((inv) => (
                  <InvoiceCard key={inv.id} invoice={inv} onDelete={refresh} />
                ))}
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  )
}
