import { useState } from 'react'
import { LoaderCircle, RefreshCw, X } from 'lucide-react'
import { marketService } from '../../services/marketService'
import { portfolioService } from '../../services/portfolioService'
import { getApiError } from '../../services/api'
import type { MarketData } from '../../types'

const quoteTime = (value: string | null) => value
  ? new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
  : 'time not supplied by exchange'

export default function AddHoldingModal({ portfolioId, onClose, onCreated }: { portfolioId: number; onClose: () => void; onCreated: () => void }) {
  const [ticker, setTicker] = useState('')
  const [quantity, setQuantity] = useState('')
  const [buyPrice, setBuyPrice] = useState('')
  const [quote, setQuote] = useState<MarketData | null>(null)
  const [fetchingQuote, setFetchingQuote] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const fetchLivePrice = async () => {
    if (!ticker.trim()) {
      setError('Enter a ticker before fetching its live price.')
      return
    }
    setError('')
    setFetchingQuote(true)
    try {
      const marketQuote = await marketService.get(ticker)
      setQuote(marketQuote)
    } catch (err) {
      setQuote(null)
      setError(getApiError(err, 'Unable to retrieve a live price for this ticker.'))
    } finally {
      setFetchingQuote(false)
    }
  }

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      await portfolioService.addHolding({ portfolio_id: portfolioId, ticker, quantity: Number(quantity), buy_price: Number(buyPrice) })
      onCreated()
      onClose()
    } catch (err) {
      setError(getApiError(err))
    } finally {
      setSaving(false)
    }
  }

  return <div className="modal-overlay" role="presentation">
    <form className="modal" onSubmit={submit}>
      <div className="modal-header"><div><p className="eyebrow">PORTFOLIO HOLDING</p><h2>Add an investment</h2></div><button type="button" className="icon-button" onClick={onClose}><X size={20} /></button></div>
      <p className="muted">Use the NSE ticker, such as <strong>TCS</strong> or <strong>INFY</strong>. You can retrieve the latest available market price before saving.</p>
      <label>Ticker<input autoFocus required value={ticker} onChange={(event) => { setTicker(event.target.value.toUpperCase()); setQuote(null) }} placeholder="e.g. TCS" maxLength={20} /></label>
      <div className="live-quote-actions"><button type="button" className="button secondary compact" onClick={() => void fetchLivePrice()} disabled={fetchingQuote}>{fetchingQuote ? <LoaderCircle className="spin" size={15} /> : <RefreshCw size={15} />}{fetchingQuote ? 'Fetching price…' : 'Fetch live price'}</button></div>
      {quote && <div className="live-quote"><div><span>Latest price</span><strong>{quote.current_price === null ? 'Unavailable' : `₹${quote.current_price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`}</strong></div><div><span>{quote.company_name}</span><small>Quote as of {quoteTime(quote.price_as_of)} · refreshed {quoteTime(quote.fetched_at)}</small></div>{quote.current_price !== null && <button type="button" className="text-link" onClick={() => setBuyPrice(String(quote.current_price))}>Use as buy price</button>}</div>}
      <div className="form-row"><label>Quantity<input required type="number" min="0.01" step="any" value={quantity} onChange={(event) => setQuantity(event.target.value)} placeholder="10" /></label><label>Buy price (₹)<input required type="number" min="0.01" step="any" value={buyPrice} onChange={(event) => setBuyPrice(event.target.value)} placeholder="3,800" /></label></div>
      {error && <p className="form-error">{error}</p>}
      <div className="modal-actions"><button type="button" className="button secondary" onClick={onClose}>Cancel</button><button className="button" disabled={saving}>{saving ? 'Adding…' : 'Add holding'}</button></div>
    </form>
  </div>
}
