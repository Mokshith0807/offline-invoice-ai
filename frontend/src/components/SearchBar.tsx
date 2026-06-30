import { useState } from 'react'
import { Search, X } from 'lucide-react'

interface SearchBarProps {
  onSearch: (query: string) => void
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [query, setQuery] = useState('')

  const handleChange = (value: string) => {
    setQuery(value)
    onSearch(value)
  }

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
      <input
        type="text"
        value={query}
        onChange={(e) => handleChange(e.target.value)}
        placeholder="Search invoices by vendor, number, or date..."
        className="w-full pl-10 pr-10 py-3 bg-dark-800 border border-dark-600 rounded-xl text-dark-100 placeholder-dark-500 focus:outline-none focus:border-blue-500 transition-colors"
      />
      {query && (
        <button onClick={() => handleChange('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-dark-500 hover:text-dark-300">
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  )
}
