import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    router.push('/dashboard')
  }, [router])

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-sage-900 via-sage-800 to-sage-700">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-cream-50 mb-4 font-serif">
          Seizure Wellness Dashboard
        </h1>
        <p className="text-lg text-cream-200">Loading dashboard...</p>
      </div>
    </div>
  )
}
