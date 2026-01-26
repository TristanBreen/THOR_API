import React from 'react'
import { Lightbulb, TrendingDown, Moon, Heart, Coffee, Footprints } from 'lucide-react'

interface HealthInsightsData {
  sleep_analysis?: {
    before_seizure_avg_total?: number
    baseline_avg_total?: number
    before_seizure_avg_deep?: number
    baseline_avg_deep?: number
    before_seizure_avg_rem?: number
    baseline_avg_rem?: number
    before_seizure_count?: number
    baseline_count?: number
  }
  heart_rate_analysis?: {
    seizure_day_min_hr?: number
    baseline_min_hr?: number
  }
  activity_analysis?: {
    before_seizure_avg_distance?: number
    baseline_avg_distance?: number
  }
}

interface InsightsData {
  [key: string]: string | number
}

interface InsightsProps {
  insights: InsightsData | null
  healthInsights: HealthInsightsData | null
  isLoading: boolean
}

const Insights: React.FC<InsightsProps> = ({ insights, healthInsights, isLoading }) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {[...Array(2)].map((_, i) => (
          <div key={i} className="card p-6 animate-pulse bg-[#FCF9F2]">
            <div className="h-6 bg-[#E5E1D8] rounded w-1/2 mb-6"></div>
            {[...Array(3)].map((_, j) => (
              <div key={j} className="mb-4">
                <div className="h-4 bg-[#E5E1D8] rounded w-full mb-2"></div>
                <div className="h-3 bg-[#E5E1D8] rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-slideUp">
      {/* Seizure Insights */}
      <div className="card p-6 border-t-4 border-[#8B7355] bg-[#FCF9F2]">
        <div className="flex items-center gap-2 mb-6">
          <Lightbulb className="w-5 h-5 text-[#8B7355]" />
          <h3 className="text-lg font-bold text-[#3D3530] font-serif">Seizure Patterns</h3>
        </div>

        <div className="space-y-4">
          {insights && insights['period_related_count'] && (
            <div className="insight-item">
              <div className="w-10 h-10 rounded-full bg-[#E5E1D8] flex items-center justify-center flex-shrink-0">
                <span className="text-lg">🩸</span>
              </div>
              <div>
                <h4 className="font-semibold text-[#3D3530]">Menstrual Cycle</h4>
                <p className="text-sm text-[#6B655F]">
                  {((insights['period_related_count'] as number / (insights['total_seizures'] as number)) * 100).toFixed(1)}% of seizures occurred during menstrual cycle
                </p>
              </div>
            </div>
          )}

          {insights && insights['food_eaten_count'] && (
            <div className="insight-item">
              <div className="w-10 h-10 rounded-full bg-[#E5E1D8] flex items-center justify-center flex-shrink-0">
                <Coffee className="w-5 h-5 text-[#8B7355]" />
              </div>
              <div>
                <h4 className="font-semibold text-[#3D3530]">Food Intake</h4>
                <p className="text-sm text-[#6B655F]">
                  {((insights['food_eaten_count'] as number / (insights['total_seizures'] as number)) * 100).toFixed(1)}% of seizures occurred after eating
                </p>
              </div>
            </div>
          )}

          {insights && insights['duration_stats'] && (
            <div className="insight-item">
              <div className="w-10 h-10 rounded-full bg-[#E5E1D8] flex items-center justify-center flex-shrink-0">
                <span className="text-lg">⏱️</span>
              </div>
              <div>
                <h4 className="font-semibold text-[#3D3530]">Duration Patterns</h4>
                <p className="text-sm text-[#6B655F]">
                  Average: {insights['duration_mean']}s | Range: {insights['duration_min']}s - {insights['duration_max']}s
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Health Insights */}
      <div className="card p-6 border-t-4 border-[#8B7355] bg-[#FCF9F2]">
        <div className="flex items-center gap-2 mb-6">
          <Heart className="w-5 h-5 text-[#8B7355]" />
          <h3 className="text-lg font-bold text-[#3D3530] font-serif">Health & Wellness</h3>
        </div>

        <div className="space-y-4">
          {healthInsights?.sleep_analysis?.before_seizure_avg_total && (
            <div className="insight-item">
              <div className="w-10 h-10 rounded-full bg-[#E5E1D8] flex items-center justify-center flex-shrink-0">
                <Moon className="w-5 h-5 text-[#8B7355]" />
              </div>
              <div>
                <h4 className="font-semibold text-[#3D3530]">Sleep Quality</h4>
                <p className="text-sm text-[#6B655F]">
                  Sleep 1-3 days before seizures: {healthInsights.sleep_analysis.before_seizure_avg_total.toFixed(1)}h vs baseline{' '}
                  {healthInsights.sleep_analysis.baseline_avg_total?.toFixed(1) || 'N/A'}h
                </p>
              </div>
            </div>
          )}

          {healthInsights?.heart_rate_analysis?.seizure_day_min_hr && (
            <div className="insight-item">
              <div className="w-10 h-10 rounded-full bg-[#E5E1D8] flex items-center justify-center flex-shrink-0">
                <Heart className="w-5 h-5 text-[#8B7355]" />
              </div>
              <div>
                <h4 className="font-semibold text-[#3D3530]">Heart Rate</h4>
                <p className="text-sm text-[#6B655F]">
                  Resting HR on seizure days: {healthInsights.heart_rate_analysis.seizure_day_min_hr.toFixed(0)} bpm vs baseline{' '}
                  {healthInsights.heart_rate_analysis.baseline_min_hr?.toFixed(0) || 'N/A'} bpm
                </p>
              </div>
            </div>
          )}

          {healthInsights?.activity_analysis?.before_seizure_avg_distance && (
            <div className="insight-item">
              <div className="w-10 h-10 rounded-full bg-[#E5E1D8] flex items-center justify-center flex-shrink-0">
                <Footprints className="w-5 h-5 text-[#8B7355]" />
              </div>
              <div>
                <h4 className="font-semibold text-[#3D3530]">Activity Level</h4>
                <p className="text-sm text-[#6B655F]">
                  Activity 1-2 days before seizures: {healthInsights.activity_analysis.before_seizure_avg_distance.toFixed(2)} mi vs baseline{' '}
                  {healthInsights.activity_analysis.baseline_avg_distance?.toFixed(2) || 'N/A'} mi
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Insights
