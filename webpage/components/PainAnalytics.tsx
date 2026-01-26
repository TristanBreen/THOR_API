import React from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
} from 'recharts'

interface PainAnalyticsProps {
  pain_analytics: {
    statistics: {
      total_pain_entries: number
      avg_pain: number
      min_pain: number
      max_pain: number
      median_pain: number
      std_dev: number
    }
    charts: {
      pain_timeline: any[]
      pain_by_hour: any[]
      pain_by_day_of_week: any[]
      pain_distribution: any[]
      daily_average_pain: any[]
      pain_severity_breakdown: any[]
    }
  }
}

const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#6366f1']

export default function PainAnalytics({ pain_analytics }: PainAnalyticsProps) {
  if (!pain_analytics || pain_analytics.statistics.total_pain_entries === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Pain Analytics</h2>
        <p className="text-gray-500">No pain data available.</p>
      </div>
    )
  }

  const { statistics, charts } = pain_analytics

  return (
    <div className="space-y-6">
      {/* Pain Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow p-4">
          <p className="text-sm text-gray-600 font-semibold">Total Entries</p>
          <p className="text-2xl font-bold text-[#8B7355]">{statistics.total_pain_entries}</p>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow p-4">
          <p className="text-sm text-gray-600 font-semibold">Average Pain</p>
          <p className="text-2xl font-bold text-green-600">{statistics.avg_pain.toFixed(1)}/10</p>
        </div>
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg shadow p-4">
          <p className="text-sm text-gray-600 font-semibold">Peak Pain</p>
          <p className="text-2xl font-bold text-red-600">{statistics.max_pain}/10</p>
        </div>
        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg shadow p-4">
          <p className="text-sm text-gray-600 font-semibold">Median Pain</p>
          <p className="text-2xl font-bold text-yellow-600">{statistics.median_pain}/10</p>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg shadow p-4">
          <p className="text-sm text-gray-600 font-semibold">Lowest Pain</p>
          <p className="text-2xl font-bold text-purple-600">{statistics.min_pain}/10</p>
        </div>
        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg shadow p-4">
          <p className="text-sm text-gray-600 font-semibold">Variability (σ)</p>
          <p className="text-2xl font-bold text-indigo-600">{statistics.std_dev.toFixed(2)}</p>
        </div>
      </div>

      {/* Pain Timeline */}
      {charts.pain_timeline && charts.pain_timeline.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Pain Timeline</h3>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={charts.pain_timeline.slice(-30)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis domain={[0, 10]} label={{ value: 'Pain Level', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                formatter={(value: any) => typeof value === 'number' ? value.toFixed(1) : value}
                labelFormatter={(label) => `Date: ${label}`}
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="pain"
                stroke="#ef4444"
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
                strokeWidth={2}
                isAnimationActive={false}
                name="Pain Level"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Daily Average Pain */}
      {charts.daily_average_pain && charts.daily_average_pain.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Daily Average Pain</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={charts.daily_average_pain.slice(-14)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis domain={[0, 10]} />
              <Tooltip
                formatter={(value: any) => typeof value === 'number' ? value.toFixed(1) : value}
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
              />
              <Legend />
              <Bar
                dataKey="avg_pain"
                fill="#3b82f6"
                radius={[8, 8, 0, 0]}
                name="Average Pain"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pain by Hour of Day */}
        {charts.pain_by_hour && charts.pain_by_hour.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Pain by Hour of Day</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={charts.pain_by_hour}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="hour" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip
                  formatter={(value: any) => typeof value === 'number' ? value.toFixed(1) : value}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
                />
                <Legend />
                <Bar
                  dataKey="avg_pain"
                  fill="#f59e0b"
                  radius={[8, 8, 0, 0]}
                  name="Average Pain"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Pain by Day of Week */}
        {charts.pain_by_day_of_week && charts.pain_by_day_of_week.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Pain by Day of Week</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={charts.pain_by_day_of_week}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip
                  formatter={(value: any) => typeof value === 'number' ? value.toFixed(1) : value}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
                />
                <Legend />
                <Bar
                  dataKey="avg_pain"
                  fill="#8b5cf6"
                  radius={[8, 8, 0, 0]}
                  name="Average Pain"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pain Distribution */}
        {charts.pain_distribution && charts.pain_distribution.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Pain Level Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={charts.pain_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="pain_level" label={{ value: 'Pain Level (1-10)', position: 'insideBottom', offset: -5 }} />
                <YAxis />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
                />
                <Legend />
                <Bar
                  dataKey="count"
                  fill="#ec4899"
                  radius={[8, 8, 0, 0]}
                  name="Frequency"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Pain Severity Breakdown */}
        {charts.pain_severity_breakdown && charts.pain_severity_breakdown.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Pain Severity Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={charts.pain_severity_breakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ severity, percentage }) => `${severity}: ${percentage}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {charts.pain_severity_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => `${value} entries`}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Pain Severity Stats Table */}
      {charts.pain_severity_breakdown && charts.pain_severity_breakdown.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-xl font-bold text-gray-800">Pain Severity Details</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-100 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Severity</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Count</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Percentage</th>
                </tr>
              </thead>
              <tbody>
                {charts.pain_severity_breakdown.map((item: any, idx: number) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-6 py-3 text-sm text-gray-800">{item.severity}</td>
                    <td className="px-6 py-3 text-sm text-gray-800">{item.count}</td>
                    <td className="px-6 py-3 text-sm text-gray-800">{item.percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pain Stats Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Pain Statistics Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Range</p>
            <p className="text-lg font-bold text-gray-800">
              {statistics.min_pain} - {statistics.max_pain}
            </p>
          </div>
          <div>
            <p className="text-gray-600">Median</p>
            <p className="text-lg font-bold text-gray-800">{statistics.median_pain}</p>
          </div>
          <div>
            <p className="text-gray-600">Standard Deviation</p>
            <p className="text-lg font-bold text-gray-800">{statistics.std_dev.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-gray-600">Average</p>
            <p className="text-lg font-bold text-gray-800">{statistics.avg_pain.toFixed(1)}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
