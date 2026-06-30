import type { InvoiceListResponse, Invoice, DashboardData, HealthStatus, UploadResponse } from '../types'

const BASE_URL = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  return response.json()
}

export const api = {
  health: () => request<HealthStatus>('/health'),

  upload: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch(`${BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }
    return response.json()
  },

  getInvoices: (search?: string, limit = 50, offset = 0) => {
    const params = new URLSearchParams()
    if (search) params.set('search', search)
    params.set('limit', String(limit))
    params.set('offset', String(offset))
    return request<InvoiceListResponse>(`/invoices?${params}`)
  },

  getInvoice: (id: number) => request<Invoice>(`/invoice/${id}`),

  deleteInvoice: (id: number) => request<{ message: string }>(`/invoice/${id}`, { method: 'DELETE' }),

  getDashboard: () => request<DashboardData>('/dashboard'),

  processInvoice: (id: number) => request<UploadResponse>(`/process/${id}`, { method: 'POST' }),

  getExportJsonUrl: (id: number) => `${BASE_URL}/invoice/${id}/export/json`,

  getExportCsvUrl: (id: number) => `${BASE_URL}/invoice/${id}/export/csv`,

  getExportOcrUrl: (id: number) => `${BASE_URL}/invoice/${id}/export/ocr`,
}
