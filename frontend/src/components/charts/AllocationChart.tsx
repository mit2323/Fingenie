import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import type { SectorAllocation } from '../../types'

const colors = ['#44c8a1', '#6997ff', '#a982ff', '#f7b955', '#f17b82', '#5ec4e3']

export default function AllocationChart({ data }: { data: SectorAllocation[] }) {
  if (!data.length) return <div className="chart-empty">Add holdings to see allocation.</div>
  return <div className="allocation-chart"><ResponsiveContainer width="100%" height={210}><PieChart><Pie data={data} dataKey="investment" nameKey="sector" innerRadius={62} outerRadius={88} paddingAngle={3} stroke="none">{data.map((item, index) => <Cell key={item.sector} fill={colors[index % colors.length]} />)}</Pie><Tooltip formatter={(value: number) => [`₹${value.toLocaleString('en-IN')}`, 'Investment']} /></PieChart></ResponsiveContainer><div className="chart-center"><strong>{data.length}</strong><span>sectors</span></div></div>
}
