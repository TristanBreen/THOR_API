import React from 'react'

const Footer: React.FC = () => {
  const [lastRefresh, setLastRefresh] = React.useState<string>('')
  const [isMounted, setIsMounted] = React.useState(false)

  React.useEffect(() => {
    setLastRefresh(new Date().toLocaleTimeString())
    setIsMounted(true)
  }, [])

  return (
    <footer className="mt-16 pt-8 border-t border-[#E5E1D8] text-center text-sm text-[#6B655F]">
      <p>
        Seizure Wellness Dashboard v3.1 • Built with React, Next.js & Tailwind CSS
      </p>
      <p className="mt-2">
        Last sync: {isMounted ? lastRefresh : '—'} • Auto-refreshes every minute
      </p>
      <div className="mt-4 flex justify-center gap-6 text-xs">
        <a href="#" className="text-[#6B655F] hover:text-[#8B7355] transition-colors">Privacy</a>
        <a href="#" className="text-[#6B655F] hover:text-[#8B7355] transition-colors">Terms</a>
        <a href="#" className="text-[#6B655F] hover:text-[#8B7355] transition-colors">Contact</a>
      </div>
    </footer>
  )
}

export default Footer
