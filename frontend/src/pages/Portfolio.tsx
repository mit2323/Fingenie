import { useEffect, useState } from 'react'
import { BriefcaseBusiness, Pencil, Plus, RefreshCw, Trash2 } from 'lucide-react'
import AddHoldingModal from '../components/portfolio/AddHoldingModal'
import { EmptyState, ErrorState, LoadingBlock } from '../components/common/Feedback'
import { usePortfolio } from '../hooks/usePortfolio'
import { getApiError } from '../services/api'
import { portfolioService } from '../services/portfolioService'
import type { Holding, PortfolioSummary } from '../types'
import './Portfolio.css'

const rupees = (value: number) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(value)
const quoteTime = (value: string | null | undefined) => value
  ? new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
  : 'Quote time unavailable'

export default function Portfolio() {
  const { portfolios, activePortfolio, selectPortfolio, refreshPortfolios } = usePortfolio()
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [summary, setSummary] = useState<PortfolioSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showAddHolding, setShowAddHolding] = useState(false)
  const [showCreate, setShowCreate] = useState(false)
  const [showEdit, setShowEdit] = useState(false)
  const [name, setName] = useState('')
  const [creating, setCreating] = useState(false)
  const [updating, setUpdating] = useState(false)

  const load = async () => {
    if (!activePortfolio) return
    setLoading(true)
    setError('')
    try {
      const [nextHoldings, nextSummary] = await Promise.all([portfolioService.holdings(activePortfolio.id), portfolioService.summary(activePortfolio.id)])
      setHoldings(nextHoldings)
      setSummary(nextSummary)
    } catch (err) {
      setError(getApiError(err, 'Unable to load holdings.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [activePortfolio?.id])

  const createPortfolio = async (event: React.FormEvent) => {
    event.preventDefault()
    setCreating(true)
    setError('')
    try {
      const created = await portfolioService.create({ name, base_currency: 'INR' })
      await refreshPortfolios()
      selectPortfolio(created)
      setName('')
      setShowCreate(false)
    } catch (err) {
      setError(getApiError(err))
    } finally {
      setCreating(false)
    }
  }

  const deleteHolding = async (id: number) => {
    if (!window.confirm('Remove this holding from the portfolio?')) return
    try {
      await portfolioService.removeHolding(id)
      await load()
    } catch (err) {
      setError(getApiError(err, 'Could not remove holding.'))
    }
  }

  const openEditPortfolio = () => {
    if (!activePortfolio) return
    setName(activePortfolio.name)
    setError('')
    setShowEdit(true)
  }

  const updatePortfolio = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!activePortfolio) return
    setUpdating(true)
    setError('')
    try {
      const updated = await portfolioService.update(activePortfolio.id, { name: name.trim() })
      await refreshPortfolios()
      selectPortfolio(updated)
      setShowEdit(false)
      setName('')
    } catch (err) {
      setError(getApiError(err, 'Could not update portfolio.'))
    } finally {
      setUpdating(false)
    }
  }

  const deletePortfolio = async () => {
    if (!activePortfolio || !window.confirm(`Delete ${activePortfolio.name}? This cannot be undone.`)) return
    try {
      await portfolioService.remove(activePortfolio.id)
      await refreshPortfolios()
    } catch (err) {
      setError(getApiError(err, 'Could not delete portfolio.'))
    }
  }

  return <div className="portfolio-page">
    <section className="page-heading"><div><p className="eyebrow">YOUR INVESTMENTS</p><h2>Portfolio workspace</h2><p className="muted">Create portfolios and keep each holding in one clear view.</p></div><button className="button" onClick={() => setShowCreate(true)}><Plus size={17} />New portfolio</button></section>
    {error && <ErrorState message={error} />}
    <div className="portfolio-tabs">{portfolios.map((portfolio) => <button key={portfolio.id} className={portfolio.id === activePortfolio?.id ? 'selected' : ''} onClick={() => selectPortfolio(portfolio)}>{portfolio.name}</button>)}</div>
    {!activePortfolio ? <EmptyState icon={<BriefcaseBusiness size={32} />} title="No portfolio yet" text="Create a portfolio to start tracking investments." action={<button className="button" onClick={() => setShowCreate(true)}>Create portfolio</button>} /> : <>
      {loading ? <LoadingBlock /> : <>
        <section className="portfolio-summary"><div><span>Current value</span><strong>{rupees(summary?.current_value ?? 0)}</strong></div><div><span>Amount invested</span><strong>{rupees(summary?.total_investment ?? 0)}</strong></div><div><span>Return</span><strong className={(summary?.profit_loss ?? 0) >= 0 ? 'positive' : 'negative'}>{(summary?.profit_loss ?? 0) >= 0 ? '+' : ''}{summary?.return_percentage ?? 0}%</strong></div><div><span>Base currency</span><strong>{activePortfolio.base_currency}</strong></div></section>
        <section className="panel holdings-panel">
          <div className="panel-head"><div><p className="eyebrow">{holdings.length} HOLDINGS</p><h3>{activePortfolio.name}</h3><p className="live-caption">Live prices are refreshed when this portfolio is loaded.</p></div><div className="inline-actions"><button className="button secondary compact" onClick={() => void load()}><RefreshCw size={15} />Refresh prices</button><button className="button secondary compact" onClick={openEditPortfolio}><Pencil size={15} />Edit</button><button className="button secondary compact" onClick={deletePortfolio}><Trash2 size={15} />Delete</button><button className="button compact" onClick={() => setShowAddHolding(true)}><Plus size={16} />Add holding</button></div></div>
          {holdings.length === 0 ? <EmptyState title="Your portfolio is ready" text="Add your first holding to get live valuation and sector allocation." action={<button className="button" onClick={() => setShowAddHolding(true)}><Plus size={17} />Add first holding</button>} /> : <div className="table-wrap"><table><thead><tr><th>Holding</th><th>Quantity</th><th>Buy price</th><th>Current price</th><th>Profit / loss</th><th aria-label="Actions" /></tr></thead><tbody>{holdings.map((holding) => <tr key={holding.id}><td><strong>{holding.ticker ?? `Holding #${holding.id}`}</strong><small>{holding.company_name ?? `Stock record #${holding.stock_id}`}</small></td><td>{holding.quantity}</td><td>{rupees(holding.average_buy_price)}<small>Invested {rupees(holding.quantity * holding.average_buy_price)}</small></td><td>{holding.current_price == null ? 'Unavailable' : rupees(holding.current_price)}<small>{holding.price_as_of ? `Quote as of ${quoteTime(holding.price_as_of)}` : `Refreshed ${quoteTime(holding.price_fetched_at)}`}</small></td><td>{holding.profit_loss == null ? 'Unavailable' : <><strong className={holding.profit_loss >= 0 ? 'positive' : 'negative'}>{holding.profit_loss >= 0 ? '+' : ''}{rupees(holding.profit_loss)}</strong><small className={holding.profit_loss >= 0 ? 'positive' : 'negative'}>{holding.profit_loss >= 0 ? '+' : ''}{holding.profit_loss_percentage ?? 0}%</small></>}</td><td><button className="table-action" aria-label="Remove holding" onClick={() => deleteHolding(holding.id)}><Trash2 size={17} /></button></td></tr>)}</tbody></table></div>}
        </section>
      </>}
    </>}
    {showAddHolding && activePortfolio && <AddHoldingModal portfolioId={activePortfolio.id} onClose={() => setShowAddHolding(false)} onCreated={() => void load()} />}
    {showEdit && activePortfolio && <div className="modal-overlay"><form className="modal" onSubmit={updatePortfolio}><div className="modal-header"><div><p className="eyebrow">EDIT PORTFOLIO</p><h2>Update {activePortfolio.name}</h2></div><button type="button" className="icon-button" onClick={() => setShowEdit(false)}>×</button></div><p className="muted">Change the portfolio name. Its holdings and valuation are kept unchanged.</p><label>Portfolio name<input autoFocus required minLength={3} maxLength={100} value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Long-term investments" /></label><label>Base currency<select disabled><option>{activePortfolio.base_currency} — Indian Rupee</option></select></label><div className="modal-actions"><button type="button" className="button secondary" onClick={() => setShowEdit(false)}>Cancel</button><button className="button" disabled={updating}>{updating ? 'Saving…' : 'Save changes'}</button></div></form></div>}
    {showCreate && <div className="modal-overlay"><form className="modal" onSubmit={createPortfolio}><div className="modal-header"><div><p className="eyebrow">NEW PORTFOLIO</p><h2>Set up a portfolio</h2></div><button type="button" className="icon-button" onClick={() => setShowCreate(false)}>×</button></div><label>Portfolio name<input autoFocus required minLength={3} value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Long-term investments" /></label><label>Base currency<select disabled><option>INR — Indian Rupee</option></select></label><div className="modal-actions"><button type="button" className="button secondary" onClick={() => setShowCreate(false)}>Cancel</button><button className="button" disabled={creating}>{creating ? 'Creating…' : 'Create portfolio'}</button></div></form></div>}
  </div>
}
