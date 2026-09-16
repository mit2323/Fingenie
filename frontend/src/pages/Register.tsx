import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthShell from '../components/auth/AuthShell'
import { useAuth } from '../hooks/useAuth'
import { getApiError } from '../services/api'

export default function Register() {
  const { register } = useAuth(); const navigate = useNavigate()
  const [fullName, setFullName] = useState(''); const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [busy, setBusy] = useState(false)
  const submit = async (event: React.FormEvent) => { event.preventDefault(); setError(''); setBusy(true); try { await register(fullName, email, password); navigate('/dashboard') } catch (err) { setError(getApiError(err, 'Unable to create your account.')) } finally { setBusy(false) } }
  return <AuthShell><form className="auth-card" onSubmit={submit}><p className="eyebrow">GET STARTED</p><h2>Build your financial picture</h2><p className="muted">Create an account to start tracking your portfolio.</p><label>Full name<input required minLength={3} autoComplete="name" value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Your name" /></label><label>Email address<input required type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label><label>Password<input required type="password" minLength={8} autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Minimum 8 characters" /></label>{error && <p className="form-error">{error}</p>}<button className="button full" disabled={busy}>{busy ? 'Creating account…' : 'Create account'}</button><p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p></form></AuthShell>
}
