import React from 'react'

const Footer: React.FC = () => {
  const [lastRefresh, setLastRefresh] = React.useState<Date>(new Date())

  React.useEffect(() => {
    setLastRefresh(new Date())
  }, [])

  return (
    <footer className="mt-16 pt-8 border-t border-cream-200 text-center text-sm text-sage-600">
      <p>
        Seizure Wellness Dashboard v2.0 • Built with React, Next.js & Tailwind CSS
      </p>
      <p className="mt-2">
        Last sync: {lastRefresh.toLocaleTimeString()} • Auto-refreshes every minute
      </p>
      <div className="mt-4 flex justify-center gap-6 text-xs">
        <a href="#" className="text-sage-500 hover:text-sage-700 transition-colors">Privacy</a>
        <a href="#" className="text-sage-500 hover:text-sage-700 transition-colors">Terms</a>
        <a href="#" className="text-sage-500 hover:text-sage-700 transition-colors">Contact</a>
      </div>
    </footer>
  )
}

export default Footer
