import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Home, FileText, Menu, X, WifiOff } from 'lucide-react'
import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Invoices from './pages/Invoices'
import InvoiceDetail from './pages/InvoiceDetail'

function Navbar() {
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const links = [
    { to: '/', label: 'Dashboard', icon: Home },
    { to: '/invoices', label: 'Invoices', icon: FileText },
  ]

  return (
    <nav className="border-b border-dark-800 bg-dark-950/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <WifiOff className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-dark-100 hidden sm:block">Offline Invoice AI</span>
        </Link>

        <div className="hidden md:flex items-center gap-1">
          {links.map((l) => {
            const active = location.pathname === l.to
            return (
              <Link
                key={l.to}
                to={l.to}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-colors ${
                  active ? 'bg-dark-800 text-dark-100' : 'text-dark-400 hover:text-dark-200 hover:bg-dark-800/50'
                }`}
              >
                <l.icon className="w-4 h-4" />
                {l.label}
              </Link>
            )
          })}
        </div>

        <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden p-2 text-dark-400">
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t border-dark-800 px-4 py-2 space-y-1">
          {links.map((l) => {
            const active = location.pathname === l.to
            return (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-colors ${
                  active ? 'bg-dark-800 text-dark-100' : 'text-dark-400'
                }`}
              >
                <l.icon className="w-4 h-4" />
                {l.label}
              </Link>
            )
          })}
        </div>
      )}
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-dark-950">
        <Navbar />
        <main className="p-4 md:p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/invoices" element={<Invoices />} />
            <Route path="/invoice/:id" element={<InvoiceDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
