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
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ScatterChart,
  Scatter,
} from 'recharts'

interface TabsProps {
  charts: any
  pain_analytics: any
  medical_insights: any
  medical_charts: any
  isLoading: boolean
}

const COLORS = ['#2d5a3d', '#c1566c', '#4a7c59', '#8b7355', '#d4a574', '#6b8e6f']

export default function GraphTabs({ charts, pain_analytics, medical_insights, medical_charts, isLoading }: TabsProps) {
  const [activeTab, setActiveTab] = useState('seizures')

  if (isLoading) {
    return (
      <div className="bg-gray-900 rounded-lg shadow">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-80 animate-pulse bg-gray-700 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  // Tab 1: Seizure Analysis
  const seizureCharts = [
    {
      id: 'hourly',
      title: 'Seizure Risk by Hour of Day',
      description: 'Identify high-risk times',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={charts?.hour_distribution || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis dataKey="hour" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(255,255,255,0.95)', border: 'none', borderRadius: '8px' }} />
            <Bar dataKey="count" fill="#2d5a3d" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      ),
    },
    {
      id: 'monthly',
      title: 'Seizure Trends Over Time',
      description: 'Monthly seizure frequency',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={charts?.monthly_distribution || []}>
            <defs>
              <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2d5a3d" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#2d5a3d" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis dataKey="month" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(255,255,255,0.95)', border: 'none', borderRadius: '8px' }} />
            <Area type="monotone" dataKey="count" stroke="#2d5a3d" fillOpacity={1} fill="url(#colorCount)" />
          </AreaChart>
        </ResponsiveContainer>
      ),
    },
    {
      id: 'duration',
      title: 'Duration Distribution',
      description: 'Seizure duration patterns',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={charts?.duration_distribution || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="range" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Bar dataKey="count" fill="#4a7c59" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      ),
    },
    {
      id: 'dayofweek',
      title: 'Seizures by Day of Week',
      description: 'Weekly pattern analysis',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={charts?.day_of_week_distribution || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="day" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Bar dataKey="count" fill="#c1566c" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      ),
    },
    {
      id: 'hourly_line',
      title: 'Hourly Seizure Timeline',
      description: 'Seizure frequency by hour',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={charts?.hourly_seizures || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="hour" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Line type="monotone" dataKey="count" stroke="#2d5a3d" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      ),
    },
    {
      id: 'monthly_line',
      title: 'Monthly Seizure Trend',
      description: 'Line view of monthly trends',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={charts?.monthly_seizures || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Line type="monotone" dataKey="count" stroke="#c1566c" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      ),
    },
  ]

  // Tab 2: Pain Analytics
  const painCharts = pain_analytics
    ? [
        {
          id: 'pain_timeline',
          title: 'Pain Timeline',
          render: () => (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={pain_analytics?.charts?.pain_timeline?.slice(-30) || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
                <YAxis domain={[0, 10]} stroke="#9ca3af" />
                <Tooltip
                  formatter={(value: any) => (typeof value === 'number' ? value.toFixed(1) : value)}
                  contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }}
                />
                <Line type="monotone" dataKey="pain" stroke="#ef4444" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ),
        },
        {
          id: 'pain_by_hour',
          title: 'Pain by Hour of Day',
          render: () => (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pain_analytics?.charts?.pain_by_hour || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="hour" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  formatter={(value: any) => (typeof value === 'number' ? value.toFixed(1) : value)}
                  contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="avg_pain" fill="#f59e0b" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ),
        },
        {
          id: 'pain_by_day',
          title: 'Pain by Day of Week',
          render: () => (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pain_analytics?.charts?.pain_by_day_of_week || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="day" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  formatter={(value: any) => (typeof value === 'number' ? value.toFixed(1) : value)}
                  contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="avg_pain" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ),
        },
        {
          id: 'pain_distribution',
          title: 'Pain Level Distribution',
          render: () => (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pain_analytics?.charts?.pain_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="pain_level" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
                <Bar dataKey="count" fill="#ec4899" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ),
        },
        {
          id: 'daily_pain',
          title: 'Daily Average Pain',
          render: () => (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pain_analytics?.charts?.daily_average_pain?.slice(-14) || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  formatter={(value: any) => (typeof value === 'number' ? value.toFixed(1) : value)}
                  contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="avg_pain" fill="#3b82f6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ),
        },
        {
          id: 'pain_severity',
          title: 'Pain Severity Distribution',
          render: () => (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pain_analytics?.charts?.pain_severity_breakdown || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ severity, percentage }) => `${severity}: ${percentage}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {(pain_analytics?.charts?.pain_severity_breakdown || []).map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => `${value} entries`}
                  contentStyle={{ backgroundColor: 'rgba(255,255,255,0.95)', border: 'none', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ),
        },
      ]
    : []

  // Tab 3: Health & Correlations
  const healthCharts = []

  if (charts?.heart_rate_timeline) {
    healthCharts.push({
      id: 'heart_rate',
      title: 'Heart Rate Trend',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={charts.heart_rate_timeline}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Legend />
            <Line type="monotone" dataKey="heartRate" stroke="#c1566c" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      ),
    })
  }

  if (charts?.sleep_timeline) {
    healthCharts.push({
      id: 'sleep',
      title: 'Sleep Timeline',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={charts.sleep_timeline}>
            <defs>
              <linearGradient id="colorSleep" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4a7c59" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#4a7c59" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Area type="monotone" dataKey="sleep" stroke="#4a7c59" fillOpacity={1} fill="url(#colorSleep)" />
          </AreaChart>
        </ResponsiveContainer>
      ),
    })
  }

  if (medical_charts?.inter_seizure_distribution) {
    healthCharts.push({
      id: 'intervals',
      title: 'Inter-Seizure Interval Distribution',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={medical_charts.inter_seizure_distribution}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="range" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      ),
    })
  }

  if (medical_charts?.duration_trend) {
    healthCharts.push({
      id: 'duration_trend',
      title: 'Seizure Duration Trend',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={medical_charts.duration_trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis dataKey="seizure_number" stroke="#888" />
            <YAxis stroke="#888" label={{ value: 'Duration (seconds)', angle: -90, position: 'insideLeft' }} />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(255,255,255,0.95)', border: 'none', borderRadius: '8px' }} />
            <Line type="monotone" dataKey="duration" stroke="#d4a574" strokeWidth={2} name="Duration" />
          </LineChart>
        </ResponsiveContainer>
      ),
    })
  }

  if (medical_charts?.pain_seizure_correlation) {
    healthCharts.push({
      id: 'pain_seizure',
      title: 'Pain-Seizure Correlation',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={medical_charts.pain_seizure_correlation}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis dataKey="date" stroke="#888" angle={-45} textAnchor="end" height={80} />
            <YAxis yAxisId="left" stroke="#888" />
            <YAxis yAxisId="right" orientation="right" stroke="#888" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(255,255,255,0.95)', border: 'none', borderRadius: '8px' }} />
            <Legend />
            <Bar yAxisId="left" dataKey="seizure_count" fill="#2d5a3d" radius={[8, 8, 0, 0]} name="Seizures" />
            <Bar yAxisId="right" dataKey="avg_pain" fill="#ef4444" radius={[8, 8, 0, 0]} name="Avg Pain" />
          </BarChart>
        </ResponsiveContainer>
      ),
    })
  }

  if (medical_charts?.food_impact_comparison) {
    healthCharts.push({
      id: 'food_impact',
      title: 'Food Impact Analysis',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={medical_charts.food_impact_comparison}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis dataKey="category" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Legend />
            <Bar dataKey="avg_duration" fill="#6b8e6f" radius={[8, 8, 0, 0]} name="Avg Duration (sec)" />
          </BarChart>
        </ResponsiveContainer>
      ),
    })
  }

  if (medical_charts?.seizure_severity_distribution) {
    healthCharts.push({
      id: 'severity',
      title: 'Seizure Severity Distribution',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={medical_charts.seizure_severity_distribution}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ severity, percentage }) => `${severity}: ${percentage}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="count"
            >
              {medical_charts.seizure_severity_distribution.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value) => `${value} seizures`}
              contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }}
            />
          </PieChart>
        </ResponsiveContainer>
      ),
    })
  }

  if (medical_charts?.time_of_day_pattern) {
    healthCharts.push({
      id: 'time_pattern',
      title: 'Seizures by Time of Day',
      render: () => (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={medical_charts.time_of_day_pattern}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis dataKey="period" stroke="#888" angle={-45} textAnchor="end" height={80} />
            <YAxis stroke="#888" />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(255,255,255,0.95)', border: 'none', borderRadius: '8px' }} />
            <Bar dataKey="count" fill="#d4a574" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      ),
    })
  }

  const tabs = [
    { id: 'seizures', label: '⚡ Seizure Analysis', charts: seizureCharts },
    { id: 'pain', label: '🔥 Pain Analytics', charts: painCharts },
    { id: 'health', label: '❤️ Health & Correlations', charts: healthCharts },
    { id: 'medical', label: '📊 Medical Insights', charts: [] },
  ]

  return (
    <div className="bg-gray-900 rounded-lg shadow">
      {/* Tab Navigation */}
      <div className="flex flex-wrap border-b border-gray-700">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 px-6 py-4 font-semibold text-center transition-colors ${
              activeTab === tab.id
                ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-800'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {tabs.map((tab) => (
          activeTab === tab.id && (
            <div key={tab.id} className="space-y-8 animate-slideUp">
              {tab.id === 'medical' ? (
                <MedicalInsightsTab medicalInsights={medical_insights} medicalCharts={medical_charts} />
              ) : (
                <>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {tab.charts.map((config: any) => (
                      <div key={config.id} className="bg-gray-800 rounded-lg p-6 border-t-4 border-blue-400">
                        <div className="mb-4">
                          <h3 className="text-lg font-bold text-white">{config.title}</h3>
                          {config.description && <p className="text-sm text-gray-400">{config.description}</p>}
                        </div>
                        {config.render()}
                      </div>
                    ))}
                  </div>
                  {tab.charts.length === 0 && (
                    <div className="text-center py-12 text-gray-400">
                      <p>No data available for this tab.</p>
                    </div>
                  )}
                </>
              )}
            </div>
          )
        ))}
      </div>
    </div>
  )
}

// Medical Insights Tab Component
function MedicalInsightsTab({ medicalInsights, medicalCharts }: { medicalInsights: any; medicalCharts: any }) {
  if (!medicalInsights) return <div className="text-center py-12 text-gray-400">No medical insights available.</div>

  const { food_impact, menstrual_analysis, pain_correlation, inter_seizure_intervals } = medicalInsights

  return (
    <div className="space-y-8">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Food Impact Card */}
        <div className="bg-gradient-to-br from-green-900 to-emerald-800 rounded-lg shadow p-6">
          <p className="text-sm text-green-300 font-semibold">Food Impact</p>
          <p className="text-2xl font-bold text-green-400 mt-2">{food_impact?.trend || 'N/A'}</p>
          <p className="text-xs text-green-200 mt-1">Seizures are {food_impact?.trend === 'longer' ? 'longer' : food_impact?.trend === 'shorter' ? 'shorter' : 'similar'} with food</p>
        </div>

        {/* Menstrual Analysis Card */}
        <div className="bg-gradient-to-br from-pink-900 to-rose-800 rounded-lg shadow p-6">
          <p className="text-sm text-pink-300 font-semibold">Menstrual Cycle</p>
          <p className="text-2xl font-bold text-pink-400 mt-2">{menstrual_analysis?.period_percentage?.toFixed(1)}%</p>
          <p className="text-xs text-pink-200 mt-1">Seizures during period</p>
        </div>

        {/* Pain Correlation Card */}
        <div className="bg-gradient-to-br from-orange-900 to-amber-800 rounded-lg shadow p-6">
          <p className="text-sm text-orange-300 font-semibold">Pain Correlation</p>
          <p className="text-2xl font-bold text-orange-400 mt-2">{pain_correlation?.correlation_percentage?.toFixed(1)}%</p>
          <p className="text-xs text-orange-200 mt-1">Days with pain and seizures</p>
        </div>

        {/* Inter-Seizure Intervals Card */}
        <div className="bg-gradient-to-br from-blue-900 to-cyan-800 rounded-lg shadow p-6">
          <p className="text-sm text-blue-300 font-semibold">Max Interval</p>
          <p className="text-2xl font-bold text-blue-400 mt-2">{inter_seizure_intervals?.max_interval || 0}h</p>
          <p className="text-xs text-blue-200 mt-1">Longest time between seizures</p>
        </div>
      </div>

      {/* Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Food Impact Analysis */}
        <div className="bg-gray-800 rounded-lg shadow p-6 border-l-4 border-green-500">
          <h3 className="text-lg font-bold text-white mb-4">Food Impact Analysis</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-400">With Food - Average Duration</p>
              <p className="text-xl font-bold text-white">{food_impact?.with_food_avg?.toFixed(1)}s</p>
              <p className="text-xs text-gray-500">{food_impact?.food_eaters || 0} seizures</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Without Food - Average Duration</p>
              <p className="text-xl font-bold text-white">{food_impact?.without_food_avg?.toFixed(1)}s</p>
              <p className="text-xs text-gray-500">{food_impact?.non_eaters || 0} seizures</p>
            </div>
            <div className="pt-3 border-t border-gray-700">
              <p className="text-sm text-gray-400">Difference</p>
              <p className={`text-xl font-bold ${food_impact?.difference > 0 ? 'text-red-400' : 'text-green-400'}`}>
                {food_impact?.difference > 0 ? '+' : ''}{food_impact?.difference?.toFixed(1)}s
              </p>
            </div>
          </div>
        </div>

        {/* Menstrual Analysis */}
        <div className="bg-gray-800 rounded-lg shadow p-6 border-l-4 border-pink-500">
          <h3 className="text-lg font-bold text-white mb-4">Menstrual Cycle Analysis</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-400">During Period - Average Duration</p>
              <p className="text-xl font-bold text-white">{menstrual_analysis?.period_avg_duration?.toFixed(1)}s</p>
              <p className="text-xs text-gray-500">{menstrual_analysis?.period_seizure_count || 0} seizures</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Outside Period - Average Duration</p>
              <p className="text-xl font-bold text-white">{menstrual_analysis?.non_period_avg_duration?.toFixed(1)}s</p>
            </div>
            <div className="pt-3 border-t border-gray-700">
              <p className="text-sm text-gray-400">Difference</p>
              <p className={`text-xl font-bold ${menstrual_analysis?.difference > 0 ? 'text-red-400' : 'text-green-400'}`}>
                {menstrual_analysis?.difference > 0 ? '+' : ''}{menstrual_analysis?.difference?.toFixed(1)}s
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Pain & Interval Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pain-Seizure Correlation */}
        <div className="bg-gray-800 rounded-lg shadow p-6 border-l-4 border-orange-500">
          <h3 className="text-lg font-bold text-white mb-4">Pain-Seizure Correlation</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-400">Average Pain on Seizure Days</p>
              <p className="text-xl font-bold text-white">{pain_correlation?.avg_pain_seizure_days?.toFixed(1)}/10</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Average Pain on Non-Seizure Days</p>
              <p className="text-xl font-bold text-white">{pain_correlation?.avg_pain_non_seizure_days?.toFixed(1)}/10</p>
            </div>
            <div className="pt-3 border-t border-gray-700">
              <p className="text-sm text-gray-400">Correlation Rate</p>
              <p className="text-xl font-bold text-orange-400">{pain_correlation?.correlation_percentage?.toFixed(1)}%</p>
            </div>
          </div>
        </div>

        {/* Inter-Seizure Intervals */}
        <div className="bg-gray-800 rounded-lg shadow p-6 border-l-4 border-blue-500">
          <h3 className="text-lg font-bold text-white mb-4">Inter-Seizure Intervals</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-400">Shortest Interval</p>
              <p className="text-xl font-bold text-white">{inter_seizure_intervals?.min_interval || 0}h</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Longest Interval</p>
              <p className="text-xl font-bold text-white">{inter_seizure_intervals?.max_interval || 0}h</p>
            </div>
            <div className="pt-3 border-t border-gray-700 space-y-2">
              <div>
                <p className="text-sm text-gray-400">Average</p>
                <p className="text-lg font-bold text-white">{inter_seizure_intervals?.avg_interval?.toFixed(1)}h</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Median</p>
                <p className="text-lg font-bold text-white">{inter_seizure_intervals?.median_interval}h</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      {medicalCharts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {medicalCharts.food_impact_comparison && (
            <div className="bg-gray-800 rounded-lg p-6 border-t-4 border-green-400">
              <h3 className="text-lg font-bold text-white mb-4">Food Impact Comparison</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={medicalCharts.food_impact_comparison}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="category" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
                  <Bar dataKey="avg_duration" fill="#10b981" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {medicalCharts.inter_seizure_distribution && (
            <div className="bg-gray-800 rounded-lg p-6 border-t-4 border-blue-400">
              <h3 className="text-lg font-bold text-white mb-4">Inter-Seizure Intervals</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={medicalCharts.inter_seizure_distribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="range" stroke="#9ca3af" angle={-45} textAnchor="end" height={70} />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30,30,30,0.95)', border: 'none', borderRadius: '8px', color: '#fff' }} />
                  <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
