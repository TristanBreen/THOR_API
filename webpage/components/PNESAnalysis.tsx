import React from 'react'

interface RiskFactor {
  indicator: string
  score: string | number
  description: string
  pnes_relevance: string
}

interface PNESAnalysisProps {
  pnesAnalysis: {
    pnes_likelihood_score: number
    classification: string
    risk_factors: RiskFactor[]
    recommendations: string[]
  } | null
  isLoading?: boolean
}

const PNESAnalysis: React.FC<PNESAnalysisProps> = ({ pnesAnalysis, isLoading }) => {
  if (isLoading) {
    return (
      <div className="card bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="animate-pulse">
          <div className="h-8 bg-purple-200 rounded w-1/3 mb-4"></div>
          <div className="h-32 bg-purple-100 rounded"></div>
        </div>
      </div>
    )
  }

  if (!pnesAnalysis) {
    return (
      <div className="card bg-red-50">
        <h3 className="text-lg font-semibold text-red-900">PNES Analysis Unavailable</h3>
        <p className="text-red-700 mt-2">Unable to load PNES detection data</p>
      </div>
    )
  }

  const getSeverityColor = (score: number) => {
    if (score >= 50) return 'from-purple-500 to-purple-700'
    if (score >= 30) return 'from-purple-400 to-purple-600'
    if (score >= 15) return 'from-purple-300 to-purple-500'
    return 'from-purple-200 to-purple-400'
  }

  return (
    <div className="space-y-6">
      {/* PNES Diagnosis Banner */}
      <div className={`card bg-gradient-to-br ${getSeverityColor(pnesAnalysis.pnes_likelihood_score)} p-8`}>
        <div className="flex items-center justify-between gap-6">
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-[#3D3530] mb-3">✓ PNES Diagnosis Confirmed</h3>
            <p className="text-[#6B655F] text-base leading-relaxed">
              Psychogenic Non-Epileptic Seizures detected. Analysis below shows symptom severity and 
              clinical manifestation patterns.
            </p>
          </div>
          <div className="text-right">
            <div className="text-base font-semibold text-[#6B655F] mb-2">Symptom Severity Index</div>
            <div className="text-5xl font-bold text-[#3D3530]">{pnesAnalysis.pnes_likelihood_score}</div>
            <div className="text-[#6B655F] text-sm">/ 100</div>
          </div>
        </div>

        {/* Severity Bar */}
        <div className="mt-6 bg-white/20 rounded-full h-3 overflow-hidden">
          <div
            className="bg-white h-full rounded-full transition-all duration-500"
            style={{ width: `${pnesAnalysis.pnes_likelihood_score}%` }}
          ></div>
        </div>

        {/* Diagnosis Summary */}
        <div className="mt-6 bg-white/10 rounded-lg p-5 border border-white/20">
          <p className="text-[#3D3530] font-semibold text-base mb-2">Clinical Status:</p>
          <p className="text-[#6B655F]">
            {pnesAnalysis.classification === 'HIGH' &&
              'Strong PNES presentation with multiple psychological indicators. Psychological intervention recommended as primary treatment approach.'}
            {pnesAnalysis.classification === 'MODERATE' &&
              'Clear PNES manifestation with mixed psychological and behavioral indicators. Integrated psychological and medical management recommended.'}
            {pnesAnalysis.classification === 'LOW' &&
              'PNES diagnosis confirmed with milder symptom presentation. Ongoing monitoring and psychological support beneficial.'}
            {pnesAnalysis.classification === 'MINIMAL' &&
              'PNES confirmed with subtle symptom manifestation. Continue current management strategy.'}
          </p>
        </div>
      </div>

      {/* Clinical Manifestation Factors */}
      {pnesAnalysis.risk_factors.length > 0 && (
        <div className="card p-8">
          <h4 className="font-bold text-[#3D3530] mb-6 text-xl">🔍 PNES Manifestation Factors</h4>
          <div className="space-y-4">
            {pnesAnalysis.risk_factors.map((factor, idx) => (
              <div key={idx} className="border-l-4 border-[#8B7355] bg-[#F0EBE3] rounded-lg p-5 hover:bg-[#E5E1D8] transition-colors">
                <div className="flex items-start justify-between mb-3 gap-4">
                  <h5 className="font-bold text-[#3D3530] text-base">{factor.indicator}</h5>
                  <span className="text-sm font-bold text-white bg-[#8B7355] px-3 py-1 rounded-full whitespace-nowrap">
                    Severity: {factor.score}%
                  </span>
                </div>
                <p className="text-[#6B655F] text-sm mb-3 leading-relaxed">{factor.description}</p>
                <div className="bg-[#FCF9F2] rounded p-3 text-sm">
                  <p className="text-[#3D3530]">
                    <span className="font-bold text-[#8B7355]">How it manifests in PNES:</span> {factor.pnes_relevance}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Management Recommendations */}
      {pnesAnalysis.recommendations.length > 0 && (
        <div className="card border-l-4 border-[#8B7355] bg-[#F0EBE3] p-8">
          <h4 className="font-bold text-[#3D3530] mb-6 text-xl flex items-center gap-3">
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m7-4a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Treatment & Management Plan
          </h4>
          <ul className="space-y-3">
            {pnesAnalysis.recommendations.map((rec, idx) => (
              <li key={idx} className="flex gap-4 text-[#3D3530] text-base leading-relaxed">
                <span className="text-[#8B7355] font-bold text-lg flex-shrink-0 mt-0.5">→</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Key Information */}
      <div className="bg-[#F0EBE3] border-2 border-[#E5E1D8] rounded-lg p-6">
        <p className="text-base text-[#3D3530] leading-relaxed">
          <span className="font-bold block mb-3">📋 About PNES Management:</span>
          PNES (Psychogenic Non-Epileptic Seizures) are real seizure-like episodes of psychological origin, 
          not deliberate or "fake" seizures. With proper psychological treatment, cognitive behavioral therapy, 
          stress management, and sometimes medication, most patients experience significant improvement. The goal 
          is to help the brain relearn normal functioning through evidence-based psychological intervention.
        </p>
      </div>
    </div>
  )
}

export default PNESAnalysis
