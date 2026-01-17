import React, { useMemo } from 'react'
import { format, parseISO } from 'date-fns'
import { ChevronUp, ChevronDown } from 'lucide-react'

interface SeizureRecord {
  timestamp: string
  duration_seconds: number
  hour_of_day: number
  day_of_week: string
  period: boolean
  food_eaten: boolean
}

interface DataTableProps {
  data: SeizureRecord[] | null
  isLoading: boolean
}

const DataTable: React.FC<DataTableProps> = ({ data, isLoading }) => {
  const [sortField, setSortField] = React.useState<'timestamp' | 'duration_seconds'>('timestamp')
  const [sortDir, setSortDir] = React.useState<'asc' | 'desc'>('desc')
  const [filterPeriod, setFilterPeriod] = React.useState('all')
  const [filterFood, setFilterFood] = React.useState('all')

  const filteredData = useMemo(() => {
    if (!data) return []

    let filtered = [...data]

    if (filterPeriod !== 'all') {
      filtered = filtered.filter((d) => d.period === (filterPeriod === 'yes'))
    }

    if (filterFood !== 'all') {
      filtered = filtered.filter((d) => d.food_eaten === (filterFood === 'yes'))
    }

    filtered.sort((a, b) => {
      const aVal = a[sortField]
      const bVal = b[sortField]
      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
      return sortDir === 'asc' ? comparison : -comparison
    })

    return filtered
  }, [data, filterPeriod, filterFood, sortField, sortDir])

  const toggleSort = (field: 'timestamp' | 'duration_seconds') => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDir('desc')
    }
  }

  if (isLoading) {
    return (
      <div className="card p-6 animate-pulse">
        <div className="h-6 bg-cream-200 rounded w-1/3 mb-6"></div>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-12 bg-cream-100 rounded mb-2"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="card p-6 animate-slideUp overflow-x-auto">
      <h2 className="text-xl font-bold text-sage-900 font-serif mb-6">Recent Seizure Records</h2>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="flex-1">
          <label className="block text-sm font-semibold text-sage-700 mb-2">Period</label>
          <select
            value={filterPeriod}
            onChange={(e) => setFilterPeriod(e.target.value)}
            className="w-full px-4 py-2 bg-cream-100 border border-cream-300 rounded-lg text-sage-900 focus:outline-none focus:ring-2 focus:ring-sage-500"
          >
            <option value="all">All</option>
            <option value="yes">During Period</option>
            <option value="no">Not During Period</option>
          </select>
        </div>

        <div className="flex-1">
          <label className="block text-sm font-semibold text-sage-700 mb-2">Food</label>
          <select
            value={filterFood}
            onChange={(e) => setFilterFood(e.target.value)}
            className="w-full px-4 py-2 bg-cream-100 border border-cream-300 rounded-lg text-sage-900 focus:outline-none focus:ring-2 focus:ring-sage-500"
          >
            <option value="all">All</option>
            <option value="yes">With Food</option>
            <option value="no">Without Food</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-sage-900 text-cream-50 border-b-2 border-sage-800">
              <th className="px-4 py-3 text-left font-semibold">
                <button
                  onClick={() => toggleSort('timestamp')}
                  className="flex items-center gap-2 hover:text-cream-200 transition-colors"
                >
                  Date & Time
                  {sortField === 'timestamp' && (
                    sortDir === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                  )}
                </button>
              </th>
              <th className="px-4 py-3 text-left font-semibold">
                <button
                  onClick={() => toggleSort('duration_seconds')}
                  className="flex items-center gap-2 hover:text-cream-200 transition-colors"
                >
                  Duration (s)
                  {sortField === 'duration_seconds' && (
                    sortDir === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                  )}
                </button>
              </th>
              <th className="px-4 py-3 text-left font-semibold">Hour</th>
              <th className="px-4 py-3 text-left font-semibold">Day</th>
              <th className="px-4 py-3 text-left font-semibold">Period</th>
              <th className="px-4 py-3 text-left font-semibold">Food</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-sage-600">
                  No records found
                </td>
              </tr>
            ) : (
              filteredData.slice(0, 50).map((record, idx) => (
                <tr key={idx} className="border-b border-cream-200 hover:bg-cream-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-sage-900">
                    {format(parseISO(record.timestamp), 'MMM dd, yyyy HH:mm')}
                  </td>
                  <td className="px-4 py-3 font-semibold text-sage-800">{record.duration_seconds}</td>
                  <td className="px-4 py-3">{record.hour_of_day}:00</td>
                  <td className="px-4 py-3">{record.day_of_week}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        record.period
                          ? 'bg-rose-100 text-rose-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {record.period ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        record.food_eaten
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {record.food_eaten ? 'Yes' : 'No'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {filteredData.length > 50 && (
        <p className="text-sm text-sage-600 mt-4 text-center">
          Showing 50 of {filteredData.length} records
        </p>
      )}
    </div>
  )
}

export default DataTable
