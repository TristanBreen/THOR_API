import React, { useState } from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts'

interface ChartsData {
  [key: string]: any
}

interface ChartsProps {
  data: ChartsData | null
  isLoading: boolean
}

const Charts: React.FC<ChartsProps> = ({ data, isLoading }) => {
  const [expandedChart, setExpandedChart] = useState<string | null>(null)

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card p-6 h-80 animate-pulse">
            <div className="h-6 bg-cream-200 rounded w-1/3 mb-4"></div>
            <div className="h-72 bg-cream-100 rounded"></div>
          </div>
        ))}
      </div>
    )
  }

  if (!data) return null

  const chartConfigs = [
    {
      id: 'hourly',
      title: 'Seizure Risk by Hour of Day',
      description: 'Identify high-risk times',
      render: () => {
        const hourData = data.hour_distribution || []
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hourData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis dataKey="hour" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  border: 'none',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="count" fill="#2d5a3d" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )
      },
    },
    {
      id: 'monthly',
      title: 'Seizure Trends Over Time',
      description: 'Monthly seizure frequency',
      render: () => {
        const monthData = data.monthly_distribution || []
        return (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={monthData}>
              <defs>
                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2d5a3d" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#2d5a3d" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis dataKey="month" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  border: 'none',
                  borderRadius: '8px',
                }}
              />
              <Area
                type="monotone"
                dataKey="count"
                stroke="#2d5a3d"
                fillOpacity={1}
                fill="url(#colorCount)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )
      },
    },
    {
      id: 'duration',
      title: 'Duration Distribution',
      description: 'Seizure duration patterns',
      render: () => {
        const durationData = data.duration_distribution || []
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={durationData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis dataKey="range" stroke="#888" angle={-45} textAnchor="end" height={80} />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  border: 'none',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="count" fill="#4a7c59" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )
      },
    },
    {
      id: 'dayofweek',
      title: 'Seizures by Day of Week',
      description: 'Weekly pattern analysis',
      render: () => {
        const dayData = data.day_of_week_distribution || []
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dayData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis dataKey="day" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  border: 'none',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="count" fill="#c1566c" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )
      },
    },
  ]

  return (
    <div className="space-y-8 animate-slideUp">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {chartConfigs.map((config) => (
          <div key={config.id} className="card p-6 border-t-4 border-sage-500">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-sage-900 font-serif">{config.title}</h3>
              <p className="text-sm text-sage-600">{config.description}</p>
            </div>
            {config.render()}
          </div>
        ))}
      </div>

      {/* Additional health charts */}
      {data.heart_rate_timeline && (
        <div className="card p-6 border-t-4 border-rose-500">
          <h3 className="text-lg font-bold text-sage-900 font-serif mb-4">Heart Rate Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.heart_rate_timeline}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis dataKey="date" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  border: 'none',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="avg_hr" stroke="#c1566c" dot={false} />
              <Line type="monotone" dataKey="min_hr" stroke="#4a7c59" dot={false} />
              <Line type="monotone" dataKey="max_hr" stroke="#8b7355" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {data.sleep_timeline && (
        <div className="card p-6 border-t-4 border-indigo-500">
          <h3 className="text-lg font-bold text-sage-900 font-serif mb-4">Sleep Timeline</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.sleep_timeline}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis dataKey="date" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  border: 'none',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="total_sleep" stroke="#4a7c59" dot={false} />
              <Line type="monotone" dataKey="deep_sleep" stroke="#2d5a3d" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

export default Charts
