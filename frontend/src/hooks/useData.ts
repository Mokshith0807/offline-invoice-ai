import { useState, useEffect, useCallback } from 'react'
import type { DashboardData, InvoiceListResponse, Invoice, HealthStatus } from '../types'
import { api } from '../services/api'

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    try {
      setLoading(true)
      const result = await api.getDashboard()
      setData(result)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])
  return { data, loading, error, refresh: fetch }
}

export function useInvoices(search?: string) {
  const [data, setData] = useState<InvoiceListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    try {
      setLoading(true)
      const result = await api.getInvoices(search)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load invoices')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => { fetch() }, [fetch])
  return { data, loading, error, refresh: fetch }
}

export function useInvoice(id: number | null) {
  const [data, setData] = useState<Invoice | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (id === null) return
    try {
      setLoading(true)
      const result = await api.getInvoice(id)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load invoice')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { fetch() }, [fetch])
  return { data, loading, error, refresh: fetch }
}

export function useHealth() {
  const [data, setData] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)

  const fetch = useCallback(async () => {
    try {
      const result = await api.health()
      setData(result)
    } catch {
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])
  return { data, loading, refresh: fetch }
}
