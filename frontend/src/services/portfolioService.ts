import api from './api'
import type { Holding, Portfolio, PortfolioSummary, SectorAllocation } from '../types'

export const portfolioService = {
  list: () => api.get<Portfolio[]>('/portfolios').then((response) => response.data),
  create: (payload: { name: string; base_currency: string }) =>
    api.post<Portfolio>('/portfolios', payload).then((response) => response.data),
  update: (id: number, payload: Partial<{ name: string; base_currency: string }>) =>
    api.put<Portfolio>(`/portfolios/${id}`, payload).then((response) => response.data),
  remove: (id: number) => api.delete(`/portfolios/${id}`),
  holdings: (portfolioId: number) => api.get<Holding[]>(`/holdings/${portfolioId}`).then((response) => response.data),
  addHolding: (payload: { portfolio_id: number; ticker: string; quantity: number; buy_price: number }) =>
    api.post<Holding>('/holdings', payload).then((response) => response.data),
  updateHolding: (id: number, payload: { quantity: number; buy_price: number }) =>
    api.put<Holding>(`/holdings/${id}`, payload).then((response) => response.data),
  removeHolding: (id: number) => api.delete(`/holdings/${id}`),
  summary: (portfolioId: number) =>
    api.get<PortfolioSummary>(`/portfolio-summary/${portfolioId}`).then((response) => response.data),
  allocation: (portfolioId: number) =>
    api.get<SectorAllocation[]>(`/analytics/sector-allocation/${portfolioId}`).then((response) => response.data),
}
