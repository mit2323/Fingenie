import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthShell from '../components/auth/AuthShell'
import { useAuth } from '../hooks/useAuth'
import { getApiError } from '../services/api'

export default function Login() {
  const { login } = useAuth(); const navigate = useNavigate()
  const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [busy, setBusy] = useState(false)
  const submit = async (event: React.FormEvent) => { event.preventDefault(); setError(''); setBusy(true); try { await login(email, password); navigate('/dashboard') } catch (err) { setError(getApiError(err, 'Unable to sign in. Check your email and password.')) } finally { setBusy(false) } }
  return <AuthShell><form className="auth-card" onSubmit={submit}><p className="eyebrow">WELCOME BACK</p><h2>Sign in to FinGenie</h2><p className="muted">Your portfolio intelligence is waiting.</p><label>Email address<input required type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label><label>Password<input required type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Your password" /></label>{error && <p className="form-error">{error}</p>}<button className="button full" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button><p className="auth-switch">New to FinGenie? <Link to="/register">Create an account</Link></p></form></AuthShell>
}
