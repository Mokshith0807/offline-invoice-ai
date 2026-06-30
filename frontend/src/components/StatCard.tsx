import { FileText, Clock, HardDrive, Activity, CheckCircle, XCircle, Clock as ClockIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  icon: 'invoices' | 'processing' | 'completed' | 'failed' | 'pending' | 'storage'
}

const iconMap = {
  invoices: FileText,
  processing: Activity,
  completed: CheckCircle,
  failed: XCircle,
  pending: ClockIcon,
  storage: HardDrive,
}

const colorMap = {
  invoices: 'text-blue-400 bg-blue-500/10',
  processing: 'text-yellow-400 bg-yellow-500/10',
  completed: 'text-green-400 bg-green-500/10',
  failed: 'text-red-400 bg-red-500/10',
  pending: 'text-purple-400 bg-purple-500/10',
  storage: 'text-cyan-400 bg-cyan-500/10',
}

export default function StatCard({ title, value, icon }: StatCardProps) {
  const Icon = iconMap[icon]
  const colorClass = colorMap[icon]

  return (
    <div className="bg-dark-800 rounded-xl p-5 border border-dark-700">
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-lg ${colorClass}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <p className="text-sm text-dark-400">{title}</p>
          <p className="text-2xl font-bold text-dark-100">{value}</p>
        </div>
      </div>
    </div>
  )
}
