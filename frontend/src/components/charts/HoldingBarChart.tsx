import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function HoldingBarChart({ data }: { data: Array<{ ticker: string; investment: number }> }) {
  if (!data.length) return <div className="chart-empty">Holdings will appear here once added.</div>
  return <ResponsiveContainer width="100%" height={280}><BarChart data={data} margin={{ top: 8, right: 4, left: -18, bottom: 0 }}><CartesianGrid vertical={false} stroke="#edf0f5" /><XAxis dataKey="ticker" tickLine={false} axisLine={false} tick={{ fill: '#718096', fontSize: 12 }} /><YAxis tickFormatter={(value) => `₹${Number(value) / 1000}k`} tickLine={false} axisLine={false} tick={{ fill: '#718096', fontSize: 11 }} /><Tooltip formatter={(value: number) => [`₹${value.toLocaleString('en-IN')}`, 'Investment']} cursor={{ fill: '#f1f6ff' }} /><Bar dataKey="investment" fill="#4f7cff" radius={[6, 6, 0, 0]} maxBarSize={46} /></BarChart></ResponsiveContainer>
}
