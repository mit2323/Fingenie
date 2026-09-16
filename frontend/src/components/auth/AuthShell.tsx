import type { ReactNode } from 'react'
import { Sparkles, TrendingUp } from 'lucide-react'

export default function AuthShell({ children }: { children: ReactNode }) {
  return <main className="auth-shell">
    <section className="auth-intro"><a className="brand" href="/"><span className="brand-mark">F</span><span>FinGenie</span></a><div className="auth-hero"><span className="hero-icon"><TrendingUp size={26} /></span><p className="eyebrow">INVEST WITH CLARITY</p><h1>Your financial command center.</h1><p>See your portfolio, understand its risks, and get grounded answers from your AI financial copilot.</p><div className="hero-note"><Sparkles size={17} /> Built around your real portfolio data</div></div></section>
    <section className="auth-panel">{children}</section>
  </main>
}
