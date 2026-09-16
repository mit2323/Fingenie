import { useEffect, useState } from 'react'
import { BarChart3, CircleGauge, Info } from 'lucide-react'
import AllocationChart from '../components/charts/AllocationChart'
import HoldingBarChart from '../components/charts/HoldingBarChart'
import { EmptyState, ErrorState, LoadingBlock } from '../components/common/Feedback'
import { usePortfolio } from '../hooks/usePortfolio'
import { getApiError } from '../services/api'
import { portfolioService } from '../services/portfolioService'
import type { Holding, SectorAllocation } from '../types'

const rupees = (value: number) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value)

export default function Analytics() {
  const { activePortfolio } = usePortfolio(); const [allocation, setAllocation] = useState<SectorAllocation[]>([]); const [holdings, setHoldings] = useState<Holding[]>([]); const [loading, setLoading] = useState(false); const [error, setError] = useState('')
  useEffect(() => { if (!activePortfolio) return; setLoading(true); setError(''); Promise.all([portfolioService.allocation(activePortfolio.id), portfolioService.holdings(activePortfolio.id)]).then(([nextAllocation, nextHoldings]) => { setAllocation(nextAllocation); setHoldings(nextHoldings) }).catch((err) => setError(getApiError(err, 'Unable to load analytics.'))).finally(() => setLoading(false)) }, [activePortfolio?.id])
  if (!activePortfolio) return <EmptyState icon={<BarChart3 size={32} />} title="Analytics appears once you have a portfolio" text="Create a portfolio and add holdings to see allocation insights." />
  if (loading) return <LoadingBlock label="Building your analytics…" />
  if (error) return <ErrorState message={error} />
  const holdingData = holdings.map((holding) => ({ ticker: `#${holding.id}`, investment: holding.quantity * holding.average_buy_price }))
  const largest = allocation[0]
  return <div className="analytics-page"><section className="page-heading"><div><p className="eyebrow">{activePortfolio.name.toUpperCase()}</p><h2>Portfolio analytics</h2><p className="muted">A live view of invested capital and sector exposure.</p></div></section><section className="analytics-grid"><article className="panel allocation-panel"><div className="panel-head"><div><p className="eyebrow">SECTOR ALLOCATION</p><h3>Where your capital is invested</h3></div></div><AllocationChart data={allocation} /><div className="allocation-legend full">{allocation.map((item, index) => <div key={item.sector}><span className={`legend-dot dot-${index}`} />{item.sector}<strong>{item.percentage.toFixed(1)}% · {rupees(item.investment)}</strong></div>)}</div></article><article className="panel concentration-panel"><span className="metric-icon blue"><CircleGauge size={20} /></span><p className="eyebrow">EXPOSURE SIGNAL</p><h3>{largest ? `${largest.sector} is your largest sector` : 'No sector data yet'}</h3><p className="muted">{largest ? `${largest.percentage.toFixed(1)}% of your invested capital is in this sector.` : 'Add holdings to begin building a sector view.'}</p><div className="signal-line"><span style={{ width: `${Math.min(largest?.percentage ?? 0, 100)}%` }} /></div><p className="mini-note"><Info size={14} />This reflects allocation, not investment advice.</p></article></section><article className="panel holdings-chart-panel"><div className="panel-head"><div><p className="eyebrow">HOLDINGS COMPARISON</p><h3>Capital invested by holding</h3></div></div><HoldingBarChart data={holdingData} /></article></div>
}
