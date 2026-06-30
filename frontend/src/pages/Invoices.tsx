import { useState, useEffect } from 'react'
import { Search, RefreshCw } from 'lucide-react'
import SearchBar from '../components/SearchBar'
import InvoiceCard from '../components/InvoiceCard'
import { useInvoices } from '../hooks/useData'

export default function Invoices() {
  const [search, setSearch] = useState('')
  const { data, loading, error, refresh } = useInvoices(search)

  useEffect(() => {
    const timer = setTimeout(refresh, 100)
    return () => clearTimeout(timer)
  }, [search, refresh])

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-dark-100">Invoices</h1>
          <p className="text-dark-500 mt-1">{data ? `${data.total} invoice${data.total !== 1 ? 's' : ''} found` : 'Loading...'}</p>
        </div>
        <button
          onClick={refresh}
          className="flex items-center gap-2 px-4 py-2 bg-dark-800 hover:bg-dark-700 rounded-lg text-sm text-dark-300 transition-colors border border-dark-700"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      <SearchBar onSearch={setSearch} />

      {error ? (
        <div className="bg-red-900/20 border border-red-800 rounded-xl p-6 text-center">
          <p className="text-red-400">{error}</p>
        </div>
      ) : loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-dark-800 rounded-xl p-5 border border-dark-700 animate-pulse">
              <div className="h-5 bg-dark-700 rounded w-40 mb-2" />
              <div className="h-4 bg-dark-700 rounded w-60 mb-4" />
              <div className="h-4 bg-dark-700 rounded w-24" />
            </div>
          ))}
        </div>
      ) : data && data.invoices.length === 0 ? (
        <div className="bg-dark-800 rounded-xl p-12 text-center border border-dark-700">
          <Search className="w-16 h-16 mx-auto text-dark-600 mb-4" />
          <h3 className="text-xl font-medium text-dark-400 mb-2">No invoices found</h3>
          <p className="text-dark-600">
            {search ? 'Try a different search term' : 'Upload your first invoice from the dashboard'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data?.invoices.map((inv) => (
            <InvoiceCard key={inv.id} invoice={inv} onDelete={refresh} />
          ))}
        </div>
      )}
    </div>
  )
}
