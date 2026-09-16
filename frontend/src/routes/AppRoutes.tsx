import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import AppLayout from '../components/layout/AppLayout'
import { LoadingBlock } from '../components/common/Feedback'
import Login from '../pages/Login'
import Register from '../pages/Register'
import Dashboard from '../pages/Dashboard'
import Portfolio from '../pages/Portfolio'
import Analytics from '../pages/Analytics'
import Copilot from '../pages/Copilot'
import Documents from '../pages/Documents'

function Protected({ children }: { children: React.ReactNode }) { const { user, loading } = useAuth(); if (loading) return <LoadingBlock label="Opening FinGenie…" />; return user ? <AppLayout>{children}</AppLayout> : <Navigate to="/login" replace /> }
function Guest({ children }: { children: React.ReactNode }) { const { user, loading } = useAuth(); if (loading) return <LoadingBlock label="Opening FinGenie…" />; return user ? <Navigate to="/dashboard" replace /> : children }

export default function AppRoutes() { return <Routes><Route path="/login" element={<Guest><Login /></Guest>} /><Route path="/register" element={<Guest><Register /></Guest>} /><Route path="/dashboard" element={<Protected><Dashboard /></Protected>} /><Route path="/portfolio" element={<Protected><Portfolio /></Protected>} /><Route path="/analytics" element={<Protected><Analytics /></Protected>} /><Route path="/copilot" element={<Protected><Copilot /></Protected>} /><Route path="/documents" element={<Protected><Documents /></Protected>} /><Route path="*" element={<Navigate to="/dashboard" replace />} /></Routes> }
