import { AuthProvider } from './context/AuthContext'
import { PortfolioProvider } from './context/PortfolioContext'
import AppRoutes from './routes/AppRoutes'

export default function App() {
  return (
    <AuthProvider>
      <PortfolioProvider>
        <AppRoutes />
      </PortfolioProvider>
    </AuthProvider>
  )
}
