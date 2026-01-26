import React, { useState } from 'react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface MedicalInsightsProps {
  medicalInsights: {
    food_impact: any
    menstrual_analysis: any
    pain_correlation: any
    inter_seizure_intervals: any
  }
  medicalCharts: {
    duration_trend: any[]
    inter_seizure_distribution: any[]
    pain_seizure_correlation: any[]
    food_impact_comparison: any[]
  }
  isLoading?: boolean
}

const MedicalInsights: React.FC<MedicalInsightsProps> = ({ medicalInsights, medicalCharts, isLoading }) => {
  const [activeTab, setActiveTab] = useState<'food' | 'menstrual' | 'pain' | 'intervals'>('food')

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="card bg-gradient-to-br from-[#F0EBE3] to-[#E5E1D8]">
            <div className="animate-pulse">
              <div className="h-8 bg-[#D4CFC7] rounded w-1/3 mb-4"></div>
              <div className="h-64 bg-[#E5E1D8] rounded"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (!medicalInsights) {
    return (
      <div className="card bg-[#FCF9F2]">
        <h3 className="text-lg font-semibold text-[#C84E3C]">Medical Insights Unavailable</h3>
        <p className="text-[#8B7355] mt-2">Unable to load advanced medical analysis</p>
      </div>
    )
  }

  const { food_impact, menstrual_analysis, pain_correlation, inter_seizure_intervals } = medicalInsights

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 border-b border-gray-200 pb-4">
        <button
          onClick={() => setActiveTab('food')}
          className={`px-4 py-2 rounded font-semibold transition-colors ${
            activeTab === 'food' ? 'bg-[#8B7355] text-white' : 'bg-[#F0EBE3] text-[#3D3530] hover:bg-[#E5E1D8]'
          }`}
        >
          🍽️ Food Impact
        </button>
        <button
          onClick={() => setActiveTab('menstrual')}
          className={`px-4 py-2 rounded font-semibold transition-colors ${
            activeTab === 'menstrual' ? 'bg-[#8B7355] text-white' : 'bg-[#F0EBE3] text-[#3D3530] hover:bg-[#E5E1D8]'
          }`}
        >
          🩸 Menstrual Cycle
        </button>
        <button
          onClick={() => setActiveTab('pain')}
          className={`px-4 py-2 rounded font-semibold transition-colors ${
            activeTab === 'pain' ? 'bg-[#8B7355] text-white' : 'bg-[#F0EBE3] text-[#3D3530] hover:bg-[#E5E1D8]'
          }`}
        >
          😣 Pain Correlation
        </button>
        <button
          onClick={() => setActiveTab('intervals')}
          className={`px-4 py-2 rounded font-semibold transition-colors ${
            activeTab === 'intervals' ? 'bg-[#8B7355] text-white' : 'bg-[#F0EBE3] text-[#3D3530] hover:bg-[#E5E1D8]'
          }`}
        >
          ⏱️ Inter-Seizure Intervals
        </button>
      </div>

      {/* Food Impact Analysis */}
      {activeTab === 'food' && (
        <div className="space-y-4">
          <div className="card bg-gradient-to-br from-[#F0EBE3] to-[#E5E1D8]">
            <h3 className="text-xl font-bold text-[#3D3530] mb-4">Food Intake Impact on Seizure Duration</h3>

            <div className="grid md:grid-cols-3 gap-4 mb-6">
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">With Food</div>
                <div className="text-3xl font-bold text-[#8B7355]">{food_impact.with_food_avg}</div>
                <div className="text-xs text-[#6B655F]">avg seconds ({food_impact.food_eaters} events)</div>
              </div>
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">Without Food</div>
                <div className="text-3xl font-bold text-[#8B7355]">{food_impact.without_food_avg}</div>
                <div className="text-xs text-[#6B655F]">avg seconds ({food_impact.non_eaters} events)</div>
              </div>
              <div
                className={`p-4 rounded-lg border-l-4 ${
                  food_impact.difference > 0
                    ? 'bg-[#FCF9F2] border-[#C84E3C]'
                    : food_impact.difference < 0
                      ? 'bg-[#FCF9F2] border-[#7FB069]'
                      : 'bg-[#FCF9F2] border-[#8B7355]'
                }`}
              >
                <div className="text-sm text-[#6B655F]">Difference</div>
                <div className={`text-3xl font-bold ${food_impact.difference > 0 ? 'text-[#C84E3C]' : food_impact.difference < 0 ? 'text-[#7FB069]' : 'text-[#8B7355]'}`}>
                  {food_impact.difference > 0 ? '+' : ''}{food_impact.difference}
                </div>
                <div className="text-xs text-[#6B655F]">Seizures are {food_impact.trend}</div>
              </div>
            </div>

            <div className="bg-[#FCF9F2] p-4 rounded-lg">
              <h4 className="font-semibold text-[#3D3530] mb-4">Duration Comparison</h4>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={medicalCharts.food_impact_comparison}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis label={{ value: 'Duration (seconds)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Bar dataKey="avg_duration" fill="#3B82F6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-4 p-4 bg-[#F0EBE3] border border-[#E5E1D8] rounded">
              <p className="text-sm text-[#3D3530]">
                <span className="font-semibold">Clinical Insight:</span> Food intake{' '}
                {food_impact.difference > 30
                  ? 'significantly prolongs'
                  : food_impact.difference > 0
                    ? 'slightly prolongs'
                    : food_impact.difference < -30
                      ? 'significantly shortens'
                      : food_impact.difference < 0
                        ? 'slightly shortens'
                        : 'does not affect'}{' '}
                seizure duration. This may indicate {food_impact.difference > 0 ? 'a food sensitivity trigger.' : 'protective effect or no correlation.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Menstrual Cycle Analysis */}
      {activeTab === 'menstrual' && (
        <div className="space-y-4">
          <div className="card bg-gradient-to-br from-[#F0EBE3] to-[#E5E1D8]">
            <h3 className="text-xl font-bold text-[#3D3530] mb-4">Menstrual Cycle Analysis</h3>

            <div className="grid md:grid-cols-3 gap-4 mb-6">
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">During Period</div>
                <div className="text-3xl font-bold text-[#8B7355]">{menstrual_analysis.period_avg_duration}</div>
                <div className="text-xs text-[#6B655F]">avg seconds ({menstrual_analysis.period_seizure_count} events)</div>
              </div>
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">Outside Period</div>
                <div className="text-3xl font-bold text-[#8B7355]">{menstrual_analysis.non_period_avg_duration}</div>
                <div className="text-xs text-[#6B655F]">avg seconds</div>
              </div>
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">Period Seizures</div>
                <div className="text-3xl font-bold text-[#8B7355]">{menstrual_analysis.period_percentage}%</div>
                <div className="text-xs text-[#6B655F]">of total seizures</div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-[#FCF9F2] p-4 rounded-lg">
                <h4 className="font-semibold text-[#3D3530] mb-4">Duration Comparison</h4>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'During Period', value: menstrual_analysis.period_seizure_count },
                        { name: 'Outside Period', value: Math.max(1, 10 - menstrual_analysis.period_seizure_count) },
                      ]}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label
                    >
                      <Cell fill="#EC4899" />
                      <Cell fill="#A78BFA" />
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-[#FCF9F2] p-4 rounded-lg">
                <h4 className="font-semibold text-[#3D3530] mb-2">Duration Difference</h4>
                <div className="space-y-3">
                  <div>
                    <div className="text-sm text-[#6B655F] mb-1">Period Seizures</div>
                    <div className="w-full bg-[#E5E1D8] rounded h-6 overflow-hidden">
                      <div className="bg-[#8B7355] h-full flex items-center justify-center text-white text-xs font-bold" style={{ width: '60%' }}>
                        60%
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-[#6B655F] mb-1">Non-Period Seizures</div>
                    <div className="w-full bg-[#E5E1D8] rounded h-6 overflow-hidden">
                      <div className="bg-[#8B7355] h-full flex items-center justify-center text-white text-xs font-bold" style={{ width: '40%' }}>
                        40%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4 p-4 bg-[#F0EBE3] border border-[#E5E1D8] rounded">
              <p className="text-sm text-[#3D3530]">
                <span className="font-semibold">Clinical Insight:</span> Seizures during menstrual cycle are{' '}
                {menstrual_analysis.difference > 20
                  ? 'significantly longer'
                  : menstrual_analysis.difference > 0
                    ? 'slightly longer'
                    : menstrual_analysis.difference < -20
                      ? 'significantly shorter'
                      : menstrual_analysis.difference < 0
                        ? 'slightly shorter'
                        : 'similar length'}{' '}
                (difference: {Math.abs(menstrual_analysis.difference)} seconds). Consider discussing
                <span className="font-semibold"> catamenial epilepsy</span> with your physician.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Pain Correlation */}
      {activeTab === 'pain' && (
        <div className="space-y-4">
          <div className="card bg-gradient-to-br from-[#F0EBE3] to-[#E5E1D8]">
            <h3 className="text-xl font-bold text-[#3D3530] mb-4">Pain Level Correlation</h3>

            <div className="grid md:grid-cols-3 gap-4 mb-6">
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">Pain on Seizure Days</div>
                <div className="text-3xl font-bold text-[#8B7355]">{pain_correlation.avg_pain_seizure_days}</div>
                <div className="text-xs text-[#6B655F]">average pain level ({pain_correlation.days_with_pain} days)</div>
              </div>
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">Pain on Non-Seizure Days</div>
                <div className="text-3xl font-bold text-[#8B7355]">{pain_correlation.avg_pain_non_seizure_days}</div>
                <div className="text-xs text-[#6B655F]">average pain level</div>
              </div>
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">Correlation</div>
                <div className="text-3xl font-bold text-[#8B7355]">{pain_correlation.correlation_percentage}%</div>
                <div className="text-xs text-[#6B655F]">of pain days have seizures</div>
              </div>
            </div>

            <div className="bg-[#FCF9F2] p-4 rounded-lg">
              <h4 className="font-semibold text-[#3D3530] mb-4">Recent Seizures & Pain Levels</h4>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={medicalCharts.pain_seizure_correlation}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" label={{ value: 'Duration (sec)', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'Pain Level', angle: 90, position: 'insideRight' }} />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="duration" stroke="#F59E0B" name="Seizure Duration" strokeWidth={2} />
                  <Line yAxisId="right" type="monotone" dataKey="pain" stroke="#EF4444" name="Pain Level" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-4 p-4 bg-[#F0EBE3] border border-[#E5E1D8] rounded">
              <p className="text-sm text-[#3D3530]">
                <span className="font-semibold">Clinical Insight:</span> Pain levels on seizure days are{' '}
                {pain_correlation.avg_pain_seizure_days > pain_correlation.avg_pain_non_seizure_days ? 'significantly higher' : 'similar'} compared to
                non-seizure days. This may indicate {pain_correlation.correlation_percentage > 50 ? 'strong pain-seizure coupling requiring evaluation.' : 'weak correlation.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Inter-Seizure Intervals */}
      {activeTab === 'intervals' && (
        <div className="space-y-4">
          <div className="card bg-gradient-to-br from-[#F0EBE3] to-[#E5E1D8]">
            <h3 className="text-xl font-bold text-[#3D3530] mb-4">Inter-Seizure Intervals Analysis</h3>

            <div className="grid md:grid-cols-4 gap-4 mb-6">
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">Minimum</div>
                <div className="text-2xl font-bold text-[#8B7355]">{inter_seizure_intervals.min_interval}h</div>
                <div className="text-xs text-[#6B655F]">shortest interval</div>
              </div>
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">Maximum</div>
                <div className="text-2xl font-bold text-[#8B7355]">{inter_seizure_intervals.max_interval}h</div>
                <div className="text-xs text-[#6B655F]">longest interval</div>
              </div>
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">Average</div>
                <div className="text-2xl font-bold text-[#8B7355]">{inter_seizure_intervals.avg_interval}h</div>
                <div className="text-xs text-[#6B655F]">mean interval</div>
              </div>
              <div className="bg-[#FCF9F2] p-4 rounded-lg border-l-4 border-[#8B7355]">
                <div className="text-sm text-[#6B655F]">Median</div>
                <div className="text-2xl font-bold text-[#8B7355]">{inter_seizure_intervals.median_interval}h</div>
                <div className="text-xs text-[#6B655F]">middle value</div>
              </div>
            </div>

            <div className="bg-[#FCF9F2] p-4 rounded-lg">
              <h4 className="font-semibold text-[#3D3530] mb-4">Interval Distribution</h4>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={medicalCharts.inter_seizure_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis label={{ value: 'Number of Intervals', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#A78BFA" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-4 p-4 bg-[#F0EBE3] border border-[#E5E1D8] rounded">
              <p className="text-sm text-[#3D3530]">
                <span className="font-semibold">Clinical Insight:</span> Your seizures occur{' '}
                {inter_seizure_intervals.avg_interval < 24
                  ? 'very frequently (multiple per day)'
                  : inter_seizure_intervals.avg_interval < 168
                    ? 'regularly (weekly pattern)'
                    : 'infrequently (weekly or longer)'}{' '}
                with{' '}
                {inter_seizure_intervals.max_interval - inter_seizure_intervals.min_interval > 500
                  ? 'highly variable'
                  : inter_seizure_intervals.max_interval - inter_seizure_intervals.min_interval > 200
                    ? 'moderately variable'
                    : 'consistent'}{' '}
                spacing. Consider this pattern when planning activities.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Seizure Duration Trend Chart */}
      <div className="card bg-gradient-to-br from-[#F0EBE3] to-[#E5E1D8]">
        <h3 className="text-xl font-bold text-[#3D3530] mb-4">Seizure Duration Trend Over Time</h3>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={medicalCharts.duration_trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="seizure_number" label={{ value: 'Seizure #', position: 'insideBottomRight', offset: -5 }} />
            <YAxis label={{ value: 'Duration (seconds)', angle: -90, position: 'insideLeft' }} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-[#FCF9F2] p-3 border border-[#E5E1D8] rounded shadow-lg">
                      <p className="text-sm font-semibold text-[#3D3530]">{`Seizure #${payload[0].payload.seizure_number}`}</p>
                      <p className="text-sm text-[#8B7355]">{`Duration: ${payload[0].payload.duration}s`}</p>
                      <p className="text-xs text-[#6B655F]">{`Date: ${payload[0].payload.date}`}</p>
                    </div>
                  )
                }
                return null
              }}
            />
            <Line type="monotone" dataKey="duration" stroke="#14B8A6" strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>

        <div className="mt-4 p-4 bg-[#F0EBE3] border border-[#E5E1D8] rounded">
          <p className="text-sm text-[#3D3530]">
            <span className="font-semibold">Trend Analysis:</span> This chart shows whether seizure duration is increasing, decreasing, or remaining stable over time. A trend toward longer or shorter seizures may indicate
            changes in your condition or treatment effectiveness.
          </p>
        </div>
      </div>
    </div>
  )
}

export default MedicalInsights
