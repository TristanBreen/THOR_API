import React from 'react'
import { TrendingDown, Zap, Coffee, Moon, Activity } from 'lucide-react'

interface PredictionData {
  [key: string]: number
}

interface PredictionsProps {
  predictions: PredictionData | null
  isLoading: boolean
}

const getRiskLevel = (percentage: number): { label: string; color: string; bgColor: string } => {
  if (percentage < 15)
    return { label: 'Low Risk', color: 'text-green-400', bgColor: 'bg-green-900/20' }
  if (percentage < 35)
    return { label: 'Moderate Risk', color: 'text-amber-400', bgColor: 'bg-amber-900/20' }
  return { label: 'High Risk', color: 'text-rose-400', bgColor: 'bg-rose-900/20' }
}

const Predictions: React.FC<PredictionsProps> = ({ predictions, isLoading }) => {
  if (isLoading || !predictions || Object.keys(predictions).length === 0) {
    return null
  }

  const pred24 = predictions['24h'] || 0
  const pred48 = predictions['48h'] || 0
  const pred72 = predictions['72h'] || 0

  const timeframes = [
    { label: 'Next 24 Hours', value: pred24, icon: Zap },
    { label: 'Next 48 Hours', value: pred48, icon: TrendingDown },
    { label: 'Next 72 Hours', value: pred72, icon: Activity },
  ]

  return (
    <div className="mb-8 animate-slideUp">
      <div className="card bg-gradient-to-r from-slate-800/30 to-slate-700/20 border-l-4 border-sage-600 p-6">
        <div className="flex items-center gap-2 mb-6">
          <Zap className="w-5 h-5 text-sage-500" />
          <h2 className="text-xl font-bold text-slate-100 font-serif">Seizure Risk Predictions</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {timeframes.map((timeframe, index) => {
            const risk = getRiskLevel(timeframe.value)
            const Icon = timeframe.icon

            return (
              <div
                key={index}
                className={`${risk.bgColor} border border-slate-600 rounded-lg p-4 text-center hover:shadow-soft transition-all duration-300`}
              >
                <Icon className={`w-6 h-6 mx-auto mb-2 ${risk.color}`} />
                <p className="text-sm font-semibold text-slate-300 mb-2">{timeframe.label}</p>
                <p className={`text-3xl font-bold ${risk.color} mb-1`}>
                  {timeframe.value.toFixed(1)}%
                </p>
                <p className={`text-xs font-semibold ${risk.color}`}>{risk.label}</p>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default Predictions
