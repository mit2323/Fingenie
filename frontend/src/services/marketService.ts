import api from './api'
import type { MarketData } from '../types'

export const marketService = {
  get: (ticker: string) => api.get<MarketData>(`/market/${encodeURIComponent(ticker)}`).then((response) => response.data),
}
