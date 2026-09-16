export interface User {
  id: number
  full_name: string
  email: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface Portfolio {
  id: number
  name: string
  base_currency: string
  created_at: string
}

export interface Holding {
  id: number
  portfolio_id: number
  stock_id: number
  quantity: number
  average_buy_price: number
  created_at: string
  ticker?: string | null
  company_name?: string | null
  current_price?: number | null
  price_as_of?: string | null
  price_fetched_at?: string | null
  current_value?: number | null
  profit_loss?: number | null
  profit_loss_percentage?: number | null
}

export interface PortfolioSummary {
  total_investment: number
  current_value: number
  profit_loss: number
  return_percentage: number
  holding_count: number
}

export interface SectorAllocation {
  sector: string
  investment: number
  percentage: number
}

export interface MarketData {
  ticker: string
  company_name: string
  current_price: number | null
  previous_close: number | null
  open_price: number | null
  day_high: number | null
  day_low: number | null
  fifty_two_week_high: number | null
  fifty_two_week_low: number | null
  volume: number | null
  market_cap: number | null
  pe_ratio: number | null
  dividend_yield: number | null
  currency: string | null
  exchange: string | null
  price_as_of: string | null
  fetched_at: string
}

export interface Conversation {
  id: number
  title: string | null
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id?: number
  role: 'user' | 'assistant'
  content: string
  created_at?: string
}

export interface ChatSource {
  source: string
  chunk_index: number
}

export interface ChatResponse {
  message: string
  intent: string
  conversation_id: number
  sources: ChatSource[]
}
