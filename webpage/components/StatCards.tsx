import React from 'react'
import { AlertCircle, TrendingUp, Activity, Heart, Moon, Clock } from 'lucide-react'

interface StatisticData {
  total_seizures: number
  recent_seizures_7_days: number
  avg_per_week: number
  avg_duration: string
  min_duration: string
  max_duration: string
  date_range_days: number
  avg_per_day: number
  food_eaten_count: number
  no_food_count: number
  first_record: string
  period_related_count: number
}

interface StatCardsProps {
  stats: StatisticData | null
  isLoading: boolean
}

const StatCards: React.FC<StatCardsProps> = ({ stats, isLoading }) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="card p-6 animate-pulse bg-[#FCF9F2]">
            <div className="h-4 bg-[#E5E1D8] rounded w-1/3 mb-4"></div>
            <div className="h-8 bg-[#E5E1D8] rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-[#E5E1D8] rounded w-2/3"></div>
          </div>
        ))}
      </div>
    )
  }

  if (!stats) return null

  const isAlert = stats.recent_seizures_7_days > 3

  const cards = [
    {
      label: 'Total Seizures',
      value: stats.total_seizures,
      subtitle: `Since ${stats.first_record}`,
      icon: TrendingUp,
      color: 'sage',
    },
    {
      label: 'Last 7 Days',
      value: stats.recent_seizures_7_days,
      subtitle: `${stats.avg_per_week.toFixed(1)} seizures/week`,
      icon: AlertCircle,
      color: isAlert ? 'rose' : 'sage',
      alert: isAlert,
    },
    {
      label: 'Average Duration',
      value: `${stats.avg_duration}s`,
      subtitle: `Min: ${stats.min_duration}s | Max: ${stats.max_duration}s`,
      icon: Clock,
      color: 'sage',
    },
    {
      label: 'Days Tracked',
      value: stats.date_range_days,
      subtitle: `${stats.avg_per_day.toFixed(2)} seizures/day`,
      icon: Activity,
      color: 'sage',
    },
    {
      label: 'With Food',
      value: stats.food_eaten_count,
      subtitle: `${((stats.food_eaten_count / stats.total_seizures) * 100).toFixed(1)}%`,
      icon: Heart,
      color: 'sage',
    },
    {
      label: 'Without Food',
      value: stats.no_food_count,
      subtitle: `${((stats.no_food_count / stats.total_seizures) * 100).toFixed(1)}%`,
      icon: Moon,
      color: 'sage',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-slideUp">
      {cards.map((card, index) => {
        const Icon = card.icon
        const bgColor = card.alert
          ? 'from-[#F5EFE7] to-[#F0EBE3]'
          : 'from-[#F0EBE3] to-[#E5E1D8]'

        return (
          <div
            key={index}
            className={`stat-card bg-gradient-to-br ${bgColor} group cursor-pointer`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <p className="text-xs font-bold uppercase tracking-wider text-[#6B655F] group-hover:text-[#3D3530] transition-colors">
                  {card.label}
                </p>
              </div>
              <Icon className={`w-5 h-5 ${card.alert ? 'text-[#C84E3C]' : 'text-[#8B7355]'}`} />
            </div>

            <div className="mb-2">
              <p
                className={`text-3xl font-bold ${
                  card.alert ? 'text-[#C84E3C]' : 'text-[#3D3530]'
                }`}
              >
                {card.value}
              </p>
            </div>

            <p className="text-sm text-[#6B655F]">{card.subtitle}</p>
          </div>
        )
      })}
    </div>
  )
}

export default StatCards
