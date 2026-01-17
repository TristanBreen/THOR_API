import React from 'react'
import { Download, RefreshCw } from 'lucide-react'

interface HeaderProps {
  isLoading: boolean
  lastUpdated: string
  onRefresh: () => void
  onExport: () => void
}

const Header: React.FC<HeaderProps> = ({ isLoading, lastUpdated, onRefresh, onExport }) => {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-white/80 border-b border-cream-200 shadow-soft">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-sage-900 font-serif">
              ⚡ Seizure Wellness Dashboard
            </h1>
            <p className="text-sm text-sage-600 mt-1">
              Last updated: {lastUpdated || '---'}
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="btn-primary flex items-center gap-2 disabled:opacity-50"
              title="Refresh data"
            >
              <RefreshCw
                className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`}
              />
              <span className="hidden sm:inline">Refresh</span>
            </button>

            <button
              onClick={onExport}
              disabled={isLoading}
              className="btn-secondary flex items-center gap-2 disabled:opacity-50"
              title="Export data as CSV"
            >
              <Download className="w-5 h-5" />
              <span className="hidden sm:inline">Export</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
