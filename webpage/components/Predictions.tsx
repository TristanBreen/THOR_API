import React, { useEffect, useState } from 'react'
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
    return { label: 'Low Risk', color: 'text-green-600', bgColor: 'bg-green-100' }
  if (percentage < 35)
    return { label: 'Moderate Risk', color: 'text-amber-700', bgColor: 'bg-amber-100' }
  return { label: 'High Risk', color: 'text-red-700', bgColor: 'bg-red-100' }
}

const Predictions: React.FC<PredictionsProps> = ({ predictions, isLoading }) => {
  const [pred24, setPred24] = useState(0)
  const [pred48, setPred48] = useState(0)
  const [pred72, setPred72] = useState(0)

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const response = await fetch('/api/predictions')
        if (response.ok) {
          const data = await response.json()
          setPred24(data.pred24 || 0)
          setPred48(data.pred48 || 0)
          setPred72(data.pred72 || 0)
        }
      } catch (error) {
        console.error('Failed to fetch predictions:', error)
      }
    }

    fetchPredictions()
    const interval = setInterval(fetchPredictions, 60000) // Update every minute
    return () => clearInterval(interval)
  }, [])

  if (isLoading && pred24 === 0 && pred48 === 0 && pred72 === 0) {
    return null
  }

  const timeframes = [
    { label: 'Next 24 Hours', value: pred24, icon: Zap },
    { label: 'Next 48 Hours', value: pred48, icon: TrendingDown },
    { label: 'Next 72 Hours', value: pred72, icon: Activity },
  ]

  return (
    <div className="mb-8 animate-slideUp">
      <div className="card bg-[#FCF9F2] border-l-4 border-[#8B7355] p-6">
        <div className="flex items-center gap-2 mb-6">
          <Zap className="w-5 h-5 text-[#8B7355]" />
          <h2 className="text-xl font-bold text-[#3D3530] font-serif">Seizure Risk Predictions</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {timeframes.map((timeframe, index) => {
            const risk = getRiskLevel(timeframe.value)
            const Icon = timeframe.icon

            return (
              <div
                key={index}
                className={`${risk.bgColor} border border-[#E5E1D8] rounded-lg p-4 text-center hover:shadow-soft transition-all duration-300`}
              >
                <Icon className={`w-6 h-6 mx-auto mb-2 ${risk.color}`} />
                <p className="text-sm font-semibold text-[#6B655F] mb-2">{timeframe.label}</p>
                <p className="text-2xl font-bold text-[#3D3530] mb-2">{timeframe.value.toFixed(1)}%</p>
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
