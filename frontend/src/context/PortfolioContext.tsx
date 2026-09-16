import { createContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { portfolioService } from '../services/portfolioService'
import type { Portfolio } from '../types'
import { useAuth } from '../hooks/useAuth'

interface PortfolioContextValue {
  portfolios: Portfolio[]
  activePortfolio: Portfolio | null
  loading: boolean
  selectPortfolio: (portfolio: Portfolio | null) => void
  refreshPortfolios: () => Promise<void>
}

export const PortfolioContext = createContext<PortfolioContextValue | undefined>(undefined)

export function PortfolioProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [activePortfolio, setActivePortfolio] = useState<Portfolio | null>(null)
  const [loading, setLoading] = useState(false)

  const refreshPortfolios = async () => {
    if (!user) {
      setPortfolios([])
      setActivePortfolio(null)
      return
    }
    setLoading(true)
    try {
      const next = await portfolioService.list()
      setPortfolios(next)
      setActivePortfolio((current) => next.find((item) => item.id === current?.id) ?? next[0] ?? null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void refreshPortfolios() }, [user])

  const value = useMemo(() => ({
    portfolios,
    activePortfolio,
    loading,
    selectPortfolio: setActivePortfolio,
    refreshPortfolios,
  }), [portfolios, activePortfolio, loading])

  return <PortfolioContext.Provider value={value}>{children}</PortfolioContext.Provider>
}
