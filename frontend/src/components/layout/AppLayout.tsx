import type { ReactNode } from 'react'
import { Bell, ChevronDown, Sparkles } from 'lucide-react'
import { NavLink, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { usePortfolio } from '../../hooks/usePortfolio'

const navigation = [
  ['Overview', '/dashboard'],
  ['Portfolio', '/portfolio'],
  ['Analytics', '/analytics'],
  ['AI Copilot', '/copilot'],
  ['Knowledge', '/documents'],
]

const pageTitle: Record<string, string> = {
  '/dashboard': 'Overview', '/portfolio': 'Portfolio', '/analytics': 'Analytics', '/copilot': 'AI Copilot', '/documents': 'Knowledge base',
}

export default function AppLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()
  const { portfolios, activePortfolio, selectPortfolio } = usePortfolio()
  const location = useLocation()
  const initials = user?.full_name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase()

  return <div className="app-shell">
    <aside className="sidebar">
      <NavLink to="/dashboard" className="brand"><span className="brand-mark">F</span><span>FinGenie</span></NavLink>
      <p className="sidebar-label">Workspace</p>
      <nav>{navigation.map(([label, to]) => <NavLink key={to} to={to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}><span className="nav-dot" />{label}</NavLink>)}</nav>
      <div className="sidebar-bottom">
        <div className="assistant-teaser"><Sparkles size={17} /><div><strong>Ask FinGenie</strong><span>Portfolio & market answers</span></div></div>
        <button className="user-mini" onClick={logout}><span className="avatar">{initials}</span><span><strong>{user?.full_name}</strong><small>Sign out</small></span></button>
      </div>
    </aside>
    <main className="main-content">
      <header className="topbar">
        <div><p className="eyebrow">FINANCIAL COMMAND CENTER</p><h1>{pageTitle[location.pathname] ?? 'FinGenie'}</h1></div>
        <div className="topbar-actions">
          {portfolios.length > 0 && <label className="portfolio-picker"><span>Portfolio</span><select value={activePortfolio?.id ?? ''} onChange={(event) => selectPortfolio(portfolios.find((item) => item.id === Number(event.target.value)) ?? null)}>{portfolios.map((portfolio) => <option key={portfolio.id} value={portfolio.id}>{portfolio.name}</option>)}</select><ChevronDown size={15} /></label>}
          <button className="icon-button" aria-label="Notifications"><Bell size={19} /></button>
        </div>
      </header>
      <div className="page-content">{children}</div>
    </main>
  </div>
}
