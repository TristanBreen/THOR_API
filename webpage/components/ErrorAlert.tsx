import React from 'react'
import { AlertCircle } from 'lucide-react'

interface ErrorAlertProps {
  error: string
  onRetry: () => void
}

const ErrorAlert: React.FC<ErrorAlertProps> = ({ error, onRetry }) => {
  return (
    <div className="animate-slideUp">
      <div className="card bg-red-900 border-l-4 border-red-500 p-4 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-semibold text-red-200">Error Loading Data</h3>
          <p className="text-sm text-red-100 mt-1">{error}</p>
          <button
            onClick={onRetry}
            className="mt-3 text-sm font-semibold text-red-300 hover:text-red-200 transition-colors"
          >
            Try Again →
          </button>
        </div>
      </div>
    </div>
  )
}

export default ErrorAlert
