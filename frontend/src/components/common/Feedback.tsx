import type { ReactNode } from 'react'
import { AlertCircle, Inbox, LoaderCircle } from 'lucide-react'

export function LoadingBlock({ label = 'Loading your financial data…' }: { label?: string }) {
  return <div className="loading-block"><LoaderCircle size={20} className="spin" /> {label}</div>
}

export function EmptyState({ icon, title, text, action }: { icon?: ReactNode; title: string; text: string; action?: ReactNode }) {
  return <div className="empty-state">{icon ?? <Inbox size={28} />}<h3>{title}</h3><p>{text}</p>{action}</div>
}

export function ErrorState({ message }: { message: string }) {
  return <div className="error-state"><AlertCircle size={18} />{message}</div>
}
