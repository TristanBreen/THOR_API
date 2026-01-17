import React, { useEffect, useState, useCallback } from 'react'
import Head from 'next/head'
import StatCards from '@/components/StatCards'
import Predictions from '@/components/Predictions'
import Insights from '@/components/Insights'
import Charts from '@/components/Charts'
import DataTable from '@/components/DataTable'
import Header from '@/components/Header'
import ErrorAlert from '@/components/ErrorAlert'
import Footer from '@/components/Footer'
import MedicalInsights from '@/components/MedicalInsights'

interface DashboardData {
  last_updated: string
  statistics: any
  predictions: any
  charts: any
  health_insights: any
  health_charts: any
  medical_insights: any
  medical_charts: any
  pnes_analysis: any
  insights: any
  timeline: any
  records: any
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch('/api/data')
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const result = await response.json()
      setData(result)
      setLastRefresh(new Date())
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load data'
      setError(message)
      console.error('Data fetch error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 60000) // Auto-refresh every minute
    return () => clearInterval(interval)
  }, [fetchData])

  const handleExport = async () => {
    try {
      const response = await fetch('/api/export')
      if (!response.ok) throw new Error('Export failed')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `seizure_data_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Export error:', err)
      alert('Failed to export data')
    }
  }

  return (
    <>
      <Head>
        <title>Seizure Wellness Dashboard</title>
        <meta name="description" content="Comprehensive health insights and seizure tracking" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-sage-50 via-cream-50 to-cream-100">
        {/* Header */}
        <Header
          isLoading={isLoading}
          lastUpdated={data?.last_updated || ''}
          onRefresh={fetchData}
          onExport={handleExport}
        />

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Error Alert */}
          {error && <ErrorAlert error={error} onRetry={fetchData} />}

          {/* Predictions Banner */}
          {data && <Predictions predictions={data.predictions} isLoading={isLoading} />}

          {/* Statistics Grid */}
          <section className="mb-12">
            <StatCards stats={data?.statistics} isLoading={isLoading} />
          </section>

          {/* Insights Sections */}
          {data && (
            <section className="mb-12">
              <Insights
                insights={data.insights}
                healthInsights={data.health_insights}
                isLoading={isLoading}
              />
            </section>
          )}

          {/* Medical Insights Section */}
          {data && (
            <section className="mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Advanced Medical Insights</h2>
              <MedicalInsights medicalInsights={data.medical_insights} medicalCharts={data.medical_charts} isLoading={isLoading} />
            </section>
          )}

          {/* Charts Section */}
          {data && (
            <section className="mb-12">
              <Charts data={data.charts} isLoading={isLoading} />
            </section>
          )}

          {/* Data Table */}
          {data && (
            <section>
              <DataTable data={data.records} isLoading={isLoading} />
            </section>
          )}

          {/* Footer */}
          <Footer />
        </div>
      </main>
    </>
  )
}
