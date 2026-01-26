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
    return { label: 'Low Risk', color: 'text-green-400', bgColor: 'bg-green-900' }
  if (percentage < 35)
    return { label: 'Moderate Risk', color: 'text-amber-400', bgColor: 'bg-amber-900' }
  return { label: 'High Risk', color: 'text-red-400', bgColor: 'bg-red-900' }
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
      <div className="card bg-gradient-to-r from-gray-800 to-gray-700 border-l-4 border-blue-500 p-6">
        <div className="flex items-center gap-2 mb-6">
          <Zap className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl font-bold text-white font-serif">Seizure Risk Predictions</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {timeframes.map((timeframe, index) => {
            const risk = getRiskLevel(timeframe.value)
            const Icon = timeframe.icon

            return (
              <div
                key={index}
                className={`${risk.bgColor} border border-gray-600 rounded-lg p-4 text-center hover:shadow-soft transition-all duration-300`}
              >
                <Icon className={`w-6 h-6 mx-auto mb-2 ${risk.color}`} />
                <p className="text-sm font-semibold text-gray-300 mb-2">{timeframe.label}</p>
                <p className="text-2xl font-bold text-white mb-2">{timeframe.value.toFixed(1)}%</p>
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
