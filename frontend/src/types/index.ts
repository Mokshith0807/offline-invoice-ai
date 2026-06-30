export interface InvoiceItem {
  name: string
  quantity: string
  unit_price: string
  total: string
}

export interface StructuredInvoice {
  vendor: string
  invoice_number: string
  invoice_date: string
  items: InvoiceItem[]
  subtotal: string
  tax: string
  grand_total: string
  payment_method: string
}

export interface ProcessingLog {
  id: number
  invoice_id: number
  stage: string
  message: string
  duration_ms: number
  created_at: string
}

export interface Invoice {
  id: number
  filename: string
  original_text: string | null
  structured_json: StructuredInvoice | null
  processing_time_ms: number | null
  cpu_usage: number | null
  memory_usage: number | null
  model_used: string | null
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message: string | null
  created_at: string | null
  updated_at: string | null
  logs: ProcessingLog[] | null
}

export interface InvoiceListResponse {
  total: number
  invoices: Invoice[]
}

export interface DashboardData {
  total_invoices: number
  pending: number
  processing: number
  completed: number
  failed: number
  latest_invoices: Invoice[]
}

export interface HealthStatus {
  status: string
  version: string
  model_loaded: boolean
  model_path: string | null
  ocr_available: boolean
  uptime: number
  config: Record<string, unknown>
}

export interface UploadResponse {
  id: number
  filename: string
  status: string
  message: string
}
