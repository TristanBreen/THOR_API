import type { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

interface DashboardData {
  last_updated: string
  statistics: {
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
    avg_pain: number
    recent_seizures: any[]
  }
  predictions: {
    [key: string]: number
  }
  charts: {
    hour_distribution: any[]
    monthly_distribution: any[]
    day_of_week_distribution: any[]
    duration_distribution: any[]
    hourly_seizures: any[]
    monthly_seizures: any[]
  }
  insights: {
    period_related_count: number
    total_seizures: number
    food_eaten_count: number
    duration_mean: string
    duration_min: string
    duration_max: string
    duration_stats: boolean
  }
  health_insights: {
    sleep_analysis?: {
      before_seizure_avg_total?: number
      baseline_avg_total?: number
      before_seizure_avg_deep?: number
      baseline_avg_deep?: number
      before_seizure_avg_rem?: number
      baseline_avg_rem?: number
      before_seizure_count?: number
      baseline_count?: number
    }
    heart_rate_analysis?: {
      seizure_day_min_hr?: number
      baseline_min_hr?: number
    }
    activity_analysis?: {
      before_seizure_avg_distance?: number
      baseline_avg_distance?: number
    }
  }
  health_charts: {
    heart_rate_timeline: any[]
    sleep_timeline: any[]
  }
  medical_insights: {
    food_impact: {
      with_food_avg: number
      without_food_avg: number
      difference: number
      food_eaters: number
      non_eaters: number
      trend: string
    }
    menstrual_analysis: {
      period_avg_duration: number
      non_period_avg_duration: number
      difference: number
      period_seizure_count: number
      period_percentage: number
    }
    pain_correlation: {
      avg_pain_seizure_days: number
      avg_pain_non_seizure_days: number
      days_with_pain: number
      correlation_percentage: number
    }
    inter_seizure_intervals: {
      min_interval: number
      max_interval: number
      avg_interval: number
      median_interval: number
      intervals: number[]
    }
  }
  medical_charts: {
    duration_trend: any[]
    inter_seizure_distribution: any[]
    pain_seizure_correlation: any[]
    food_impact_comparison: any[]
  }
  pnes_analysis: {
    pnes_likelihood_score: number
    classification: string
    risk_factors: any[]
    recommendations: string[]
  }
  timeline: any[]
  records: any[]
}

function parseCSV(content: string): any[] {
  const lines = content.trim().split('\n')
  if (lines.length === 0) return []

  const headers = lines[0].split(',').map(h => h.trim())
  const rows = []

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim())
    const obj: any = {}
    headers.forEach((header, idx) => {
      obj[header] = values[idx] || ''
    })
    rows.push(obj)
  }

  return rows
}

function analyzePNESIndicators(
  seizureRecords: any[],
  painRecords: any[],
  healthRecords: any[]
): {
  pnes_likelihood_score: number
  classification: string
  risk_factors: any[]
  recommendations: string[]
} {
  const riskFactors: any[] = []
  let pnesScore = 0

  if (seizureRecords.length === 0) {
    return {
      pnes_likelihood_score: 0,
      classification: 'MINIMAL',
      risk_factors: [],
      recommendations: ['Insufficient data for analysis'],
    }
  }

  // 1. Pain/Anxiety Correlation
  if (painRecords && painRecords.length > 0) {
    const seizureDates = new Set(
      seizureRecords.map((s) => s.timestamp?.split('T')[0]).filter(Boolean)
    )
    const painDates = new Set(painRecords.map((p) => p.date || p.Date).filter(Boolean))

    const commonDates = Array.from(seizureDates).filter((d) => painDates.has(d)).length
    const painCorrelationPercent = (commonDates / seizureRecords.length) * 100

    if (painCorrelationPercent > 50) {
      riskFactors.push({
        indicator: 'High Anxiety/Pain Correlation',
        score: painCorrelationPercent.toFixed(1),
        description: `${painCorrelationPercent.toFixed(1)}% of seizure days have associated pain records`,
        pnes_relevance: 'HIGH - PNES often triggered by psychological stress',
      })
      pnesScore += 20
    }
  }

  // 2. Daytime Predominance
  const daytimeSeizures = seizureRecords.filter((s: any) => {
    const hour = s.hour_of_day || 12
    return hour >= 7 && hour <= 23
  }).length

  const daytimePercent = (daytimeSeizures / seizureRecords.length) * 100
  if (daytimePercent > 70) {
    riskFactors.push({
      indicator: 'Predominantly Daytime Seizures',
      score: daytimePercent.toFixed(1),
      description: `${daytimePercent.toFixed(1)}% of seizures occur during waking hours (7AM-11PM)`,
      pnes_relevance: 'HIGH - PNES more common when conscious, epileptic often sleep-related',
    })
    pnesScore += 15
  }

  // 3. Duration Variability
  const durations = seizureRecords
    .map((s: any) => {
      const dur = s.duration_seconds || 0
      return dur > 0 ? dur : null
    })
    .filter((d: any) => d !== null) as number[]

  if (durations.length > 2) {
    const mean = durations.reduce((a, b) => a + b, 0) / durations.length
    const variance = durations.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / durations.length
    const stdDev = Math.sqrt(variance)
    const cv = mean > 0 ? (stdDev / mean) * 100 : 0

    if (cv > 50) {
      riskFactors.push({
        indicator: 'High Duration Variability',
        score: cv.toFixed(1),
        description: `Large variation in seizure duration (CV: ${cv.toFixed(1)}%)`,
        pnes_relevance: 'MODERATE - PNES duration inconsistent, epilepsy more consistent',
      })
      pnesScore += 12
    }
  }

  // 4. Food Trigger Correlation
  const seizuresWithFood = seizureRecords.filter((s: any) => s.food_eaten === true).length
  const seizuresWithoutFood = seizureRecords.filter((s: any) => s.food_eaten === false).length

  if (seizuresWithFood > 0 && seizuresWithoutFood > 0) {
    const foodTriggerPercent = (seizuresWithFood / seizureRecords.length) * 100
    if (foodTriggerPercent > 60 || foodTriggerPercent < 40) {
      riskFactors.push({
        indicator: 'Potential Environmental Trigger Pattern',
        score: Math.abs(foodTriggerPercent - 50).toFixed(1),
        description: `${foodTriggerPercent.toFixed(1)}% of seizures associated with food intake`,
        pnes_relevance: 'MODERATE - PNES often linked to specific environmental/emotional triggers',
      })
      pnesScore += 10
    }
  }

  // 5. Menstrual Cycle Correlation
  const periodRelatedSeizures = seizureRecords.filter((s: any) => s.period === true).length
  const periodPercent = (periodRelatedSeizures / seizureRecords.length) * 100

  if (periodPercent < 20) {
    riskFactors.push({
      indicator: 'Low Hormonal Correlation',
      score: periodPercent.toFixed(1),
      description: `Only ${periodPercent.toFixed(1)}% of seizures occur during menstrual period`,
      pnes_relevance: 'MODERATE - PNES psychological, not hormonal; epilepsy often hormone-influenced',
    })
    pnesScore += 8
  }

  // Determine classification
  let classification = 'MINIMAL'
  if (pnesScore >= 50) classification = 'HIGH'
  else if (pnesScore >= 30) classification = 'MODERATE'
  else if (pnesScore >= 15) classification = 'LOW'

  const recommendations = []

  if (classification === 'HIGH') {
    recommendations.push(
      'Consider psychological evaluation by neuropsychiatrist',
      'EEG monitoring recommended to rule out subclinical seizures',
      'Stress/anxiety assessment and management program suggested',
      'Keep detailed trigger logs (emotional events, stressors)'
    )
  } else if (classification === 'MODERATE') {
    recommendations.push(
      'Psychological screening recommended',
      'Continue seizure tracking with emotional/stress context',
      'Consider video-EEG monitoring if diagnosis uncertain'
    )
  } else {
    recommendations.push(
      'Continue standard epilepsy management',
      'Monitor for changes in seizure pattern',
      'Maintain detailed seizure logs'
    )
  }

  return {
    pnes_likelihood_score: pnesScore,
    classification,
    risk_factors: riskFactors,
    recommendations,
  }
}

function calculateMedicalInsights(
  seizureRecords: any[],
  painRecords: any[]
): {
  medical_insights: any
  medical_charts: any
} {
  // Food Impact Analysis
  const withFood = seizureRecords.filter((s: any) => s.food_eaten === true)
  const withoutFood = seizureRecords.filter((s: any) => s.food_eaten === false)

  const withFoodAvg =
    withFood.length > 0 ? withFood.reduce((sum, s: any) => sum + (s.duration_seconds || 0), 0) / withFood.length : 0
  const withoutFoodAvg =
    withoutFood.length > 0 ? withoutFood.reduce((sum, s: any) => sum + (s.duration_seconds || 0), 0) / withoutFood.length : 0

  const foodDifference = withFoodAvg - withoutFoodAvg
  const foodTrend = foodDifference > 0 ? 'longer' : foodDifference < 0 ? 'shorter' : 'similar'

  // Menstrual Cycle Analysis
  const periodSeizures = seizureRecords.filter((s: any) => s.period === true)
  const nonPeriodSeizures = seizureRecords.filter((s: any) => s.period === false)

  const periodAvg =
    periodSeizures.length > 0 ? periodSeizures.reduce((sum, s: any) => sum + (s.duration_seconds || 0), 0) / periodSeizures.length : 0
  const nonPeriodAvg =
    nonPeriodSeizures.length > 0 ? nonPeriodSeizures.reduce((sum, s: any) => sum + (s.duration_seconds || 0), 0) / nonPeriodSeizures.length : 0

  const menstrualDifference = periodAvg - nonPeriodAvg
  const periodPercentage = (periodSeizures.length / seizureRecords.length) * 100

  // Pain Correlation
  const seizureDates = new Set(seizureRecords.map((s: any) => s.timestamp?.split('T')[0]).filter(Boolean))

  let avgPainSeizureDays = 0
  let avgPainNonSeizureDays = 0
  let painOnSeizureDays = 0

  if (painRecords && painRecords.length > 0) {
    const painOnSeizure = painRecords.filter((p: any) => seizureDates.has(p.Date || p.date))
    const painOnNonSeizure = painRecords.filter((p: any) => !seizureDates.has(p.Date || p.date))

    if (painOnSeizure.length > 0) {
      avgPainSeizureDays = painOnSeizure.reduce((sum: number, p: any) => sum + (parseFloat(p.Pain) || 0), 0) / painOnSeizure.length
      painOnSeizureDays = painOnSeizure.length
    }

    if (painOnNonSeizure.length > 0) {
      avgPainNonSeizureDays = painOnNonSeizure.reduce((sum: number, p: any) => sum + (parseFloat(p.Pain) || 0), 0) / painOnNonSeizure.length
    }
  }

  const correlationPercentage = (painOnSeizureDays / (painRecords?.length || 1)) * 100

  // Inter-seizure Intervals - Helper function to parse local time
  const parseLocalTime = (timestamp: string) => {
    // Format is YYYY-MM-DDTHH:MM:SS
    const parts = timestamp.split('T')
    if (parts.length < 2) return 0
    const datePart = parts[0]
    const timePart = parts[1]
    const [year, month, day] = datePart.split('-').map(Number)
    const [hours, minutes, seconds] = (timePart || '00:00:00').split(':').map(Number)
    return new Date(year, month - 1, day, hours, minutes, seconds).getTime()
  }

  const sortedSeizures = [...seizureRecords].sort((a: any, b: any) => a.timestamp.localeCompare(b.timestamp))
  const intervals: number[] = []

  for (let i = 1; i < sortedSeizures.length; i++) {
    const prevTime = parseLocalTime(sortedSeizures[i - 1].timestamp)
    const currTime = parseLocalTime(sortedSeizures[i].timestamp)
    
    if (prevTime > 0 && currTime > 0 && currTime >= prevTime) {
      const intervalHours = (currTime - prevTime) / (1000 * 60 * 60)
      // Only include reasonable intervals (up to 365 days = 8760 hours as absolute max)
      if (intervalHours > 0 && intervalHours < 8760) {
        intervals.push(Math.round(intervalHours))
      }
    }
  }

  const minInterval = intervals.length > 0 ? Math.min(...intervals) : 0
  const maxInterval = intervals.length > 0 ? Math.max(...intervals) : 0
  const avgInterval = intervals.length > 0 ? intervals.reduce((a, b) => a + b, 0) / intervals.length : 0
  const sortedIntervals = [...intervals].sort((a, b) => a - b)
  const medianInterval = sortedIntervals.length > 0 ? sortedIntervals[Math.floor(sortedIntervals.length / 2)] : 0

  console.log('[INTERVALS DEBUG]', { seizureCount: seizureRecords.length, intervalCount: intervals.length, min: minInterval, max: maxInterval, avg: Math.round(avgInterval) })

  // Duration Trend (over time)
  const durationTrend = sortedSeizures.map((s: any, idx: number) => ({
    seizure_number: idx + 1,
    duration: s.duration_seconds || 0,
    date: s.timestamp?.split('T')[0] || 'unknown',
  }))

  // Inter-seizure Distribution
  const intervalBuckets: { [key: string]: number } = {
    '0-24h': 0,
    '1-3d': 0,
    '3-7d': 0,
    '1-2w': 0,
    '2w+': 0,
  }

  intervals.forEach((interval) => {
    if (interval <= 24) intervalBuckets['0-24h']++
    else if (interval <= 72) intervalBuckets['1-3d']++
    else if (interval <= 168) intervalBuckets['3-7d']++
    else if (interval <= 336) intervalBuckets['1-2w']++
    else intervalBuckets['2w+']++
  })

  const interSeizureDistribution = Object.entries(intervalBuckets).map(([range, count]) => ({
    range,
    count,
  }))

  // Pain-Seizure Correlation Chart Data
  const painSeizureCorrelation = seizureRecords.slice(-10).map((s: any) => {
    const sDate = s.timestamp?.split('T')[0]
    const painOnDay = painRecords
      ?.filter((p: any) => (p.Date || p.date) === sDate)
      .reduce((max: number, p: any) => Math.max(max, parseFloat(p.Pain) || 0), 0)
    return {
      date: sDate,
      duration: s.duration_seconds || 0,
      pain: painOnDay || 0,
    }
  })

  // Food Impact Comparison
  const foodImpactComparison = [
    {
      category: 'With Food',
      avg_duration: Math.round(withFoodAvg),
      count: withFood.length,
    },
    {
      category: 'Without Food',
      avg_duration: Math.round(withoutFoodAvg),
      count: withoutFood.length,
    },
  ]

  return {
    medical_insights: {
      food_impact: {
        with_food_avg: Math.round(withFoodAvg * 10) / 10,
        without_food_avg: Math.round(withoutFoodAvg * 10) / 10,
        difference: Math.round(foodDifference * 10) / 10,
        food_eaters: withFood.length,
        non_eaters: withoutFood.length,
        trend: foodTrend,
      },
      menstrual_analysis: {
        period_avg_duration: Math.round(periodAvg * 10) / 10,
        non_period_avg_duration: Math.round(nonPeriodAvg * 10) / 10,
        difference: Math.round(menstrualDifference * 10) / 10,
        period_seizure_count: periodSeizures.length,
        period_percentage: Math.round(periodPercentage * 10) / 10,
      },
      pain_correlation: {
        avg_pain_seizure_days: Math.round(avgPainSeizureDays * 10) / 10,
        avg_pain_non_seizure_days: Math.round(avgPainNonSeizureDays * 10) / 10,
        days_with_pain: painOnSeizureDays,
        correlation_percentage: Math.round(correlationPercentage * 10) / 10,
      },
      inter_seizure_intervals: {
        min_interval: minInterval,
        max_interval: maxInterval,
        avg_interval: Math.round(avgInterval * 10) / 10,
        median_interval: medianInterval,
        intervals: intervals.slice(0, 20), // Last 20 intervals
      },
    },
    medical_charts: {
      duration_trend: durationTrend,
      inter_seizure_distribution: interSeizureDistribution,
      pain_seizure_correlation: painSeizureCorrelation,
      food_impact_comparison: foodImpactComparison,
    },
  }
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<DashboardData | { error: string }>
) {
  try {
    // Resolve Data directory - check server absolute path first, then Docker mount, then local Data folder
    // This matches the logic in app.py
    const SERVER_BASE_PATH = '/home/tristan/API/API_Repoed/THOR_API'
    const SCRIPT_DIR = process.cwd() // project root (webpage/)
    const PARENT_DIR = path.dirname(SCRIPT_DIR) // one level up
    
    let dataDir = ''

    // Check paths in priority order (same as app.py)
    if (fs.existsSync(path.join(SERVER_BASE_PATH, 'Data'))) {
      dataDir = path.join(SERVER_BASE_PATH, 'Data')
    } else if (fs.existsSync('/data/Data')) {
      dataDir = '/data/Data'
    } else if (fs.existsSync(path.join(PARENT_DIR, 'Data'))) {
      dataDir = path.join(PARENT_DIR, 'Data')
    } else {
      dataDir = path.join(PARENT_DIR, 'Data')
    }

    console.log('Using data directory:', dataDir)

    // Read CSV files
    const seizureFile = path.join(dataDir, 'seizures.csv')
    const painFile = path.join(dataDir, 'pain.csv')
    const appleWatchFile = path.join(dataDir, 'appleWatchData.csv')

    console.log('Seizure file:', seizureFile, 'exists:', fs.existsSync(seizureFile))
    console.log('Pain file:', painFile, 'exists:', fs.existsSync(painFile))
    console.log('Apple Watch file:', appleWatchFile, 'exists:', fs.existsSync(appleWatchFile))

    let seizures: any[] = []
    let painRecords: any[] = []
    let appleWatchData: any[] = []

    if (fs.existsSync(seizureFile)) {
      const seizureContent = fs.readFileSync(seizureFile, 'utf-8')
      seizures = parseCSV(seizureContent)
      console.log('Seizures loaded:', seizures.length)
    }

    if (fs.existsSync(painFile)) {
      const painContent = fs.readFileSync(painFile, 'utf-8')
      painRecords = parseCSV(painContent)
      console.log('Pain records loaded:', painRecords.length)
    }

    if (fs.existsSync(appleWatchFile)) {
      const appleWatchContent = fs.readFileSync(appleWatchFile, 'utf-8')
      appleWatchData = parseCSV(appleWatchContent)
      console.log('Apple Watch data loaded:', appleWatchData.length)
    }

    // Process statistics
    const totalSeizures = seizures.length
    const durations = seizures
      .map((s) => parseInt(s.Duration) || 0)
      .filter((d) => d > 0)
    const avgDuration =
      durations.length > 0
        ? Math.round(durations.reduce((a, b) => a + b, 0) / durations.length)
        : 0
    const totalDuration = durations.reduce((a, b) => a + b, 0)
    const minDuration = durations.length > 0 ? Math.min(...durations) : 0
    const maxDuration = durations.length > 0 ? Math.max(...durations) : 0

    // Get date range
    const seizureDates = seizures
      .map((s) => {
        // Parse date as local date (not UTC) to avoid timezone offset issues
        const [year, month, day] = s.Date.split('-').map(Number)
        return new Date(year, month - 1, day)
      })
      .filter((d) => !isNaN(d.getTime()))
    const firstRecord = seizureDates.length > 0 
      ? seizureDates.reduce((a, b) => a < b ? a : b).toLocaleDateString()
      : 'N/A'
    const lastRecord = seizureDates.length > 0
      ? seizureDates.reduce((a, b) => a > b ? a : b)
      : new Date()
    const dateRangeDays = seizureDates.length > 0
      ? Math.floor((lastRecord.getTime() - seizureDates.reduce((a, b) => a < b ? a : b).getTime()) / (1000 * 60 * 60 * 24))
      : 0

    // Last 7 days
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
    const recentSeizures7Days = seizures.filter((s) => {
      // Parse date as local date (not UTC) to avoid timezone offset issues
      const [year, month, day] = s.Date.split('-').map(Number)
      const d = new Date(year, month - 1, day)
      return d >= sevenDaysAgo && !isNaN(d.getTime())
    }).length
    const avgPerWeek = recentSeizures7Days
    const avgPerDay = dateRangeDays > 0 ? (totalSeizures / dateRangeDays).toFixed(1) : '0'

    const painValues = painRecords
      .map((p) => {
        const painVal = p['Pain'] || p[' Pain'] || p['Pain ']
        return parseFloat(painVal) || 0
      })
      .filter((p) => p > 0)
    const avgPain =
      painValues.length > 0
        ? (painValues.reduce((a, b) => a + b, 0) / painValues.length).toFixed(1)
        : '0'

    // Food related counts
    const foodEatenCount = seizures.filter((s) => s['Food Eaten'] && s['Food Eaten'].trim()).length
    const noFoodCount = seizures.filter((s) => s.Eaten === 'False').length
    const periodRelatedCount = seizures.filter((s) => s['Peiod'] && s['Peiod'].trim()).length

    // Recent seizures
    const recentSeizures = seizures.slice(-5).reverse()

    // Predictions from prediction.txt (default values)
    const predictions = {
      '24h': 0.4,
      '48h': 0.4,
      '72h': 0.6,
    }

    // Create hourly seizure data (hour_distribution format)
    const hourDistMap = new Map<string, number>()
    seizures.forEach((s) => {
      if (s.Time) {
        const hour = parseInt(s.Time.split(':')[0]) || 0
        hourDistMap.set(hour.toString().padStart(2, '0'), (hourDistMap.get(hour.toString().padStart(2, '0')) || 0) + 1)
      }
    })
    const hourDistribution = Array.from(hourDistMap.entries())
      .map(([hour, count]) => ({ hour: `${hour}:00`, count }))
      .sort((a, b) => parseInt(a.hour) - parseInt(b.hour))

    // Create monthly seizure data
    const monthlyMap = new Map<string, number>()
    seizures.forEach((s) => {
      if (s.Date) {
        const [year, month] = s.Date.split('-')
        const key = `${year}-${month}`
        monthlyMap.set(key, (monthlyMap.get(key) || 0) + 1)
      }
    })
    const monthlyDistribution = Array.from(monthlyMap.entries())
      .map(([month, count]) => ({
        month: month,
        count,
      }))
      .sort((a, b) => a.month.localeCompare(b.month))

    // Duration distribution
    const durationDistribution = durations
      .reduce(
        (acc, d) => {
          if (d < 60) acc[0]++
          else if (d < 120) acc[1]++
          else if (d < 180) acc[2]++
          else if (d < 300) acc[3]++
          else acc[4]++
          return acc
        },
        [0, 0, 0, 0, 0]
      )
      .map((count, idx) => {
        const ranges = [
          '0-60s',
          '1-2m',
          '2-3m',
          '3-5m',
          '5m+',
        ]
        return { range: ranges[idx], count }
      })

    // Seizure Patterns Analysis
    const seizuresByHour = new Map<number, number>()
    seizures.forEach((s) => {
      if (s.Time) {
        const hour = parseInt(s.Time.split(':')[0]) || 0
        seizuresByHour.set(hour, (seizuresByHour.get(hour) || 0) + 1)
      }
    })
    
    // Find peak hour
    let peakHour = 0
    let peakCount = 0
    seizuresByHour.forEach((count, hour) => {
      if (count > peakCount) {
        peakCount = count
        peakHour = hour
      }
    })
    
    const peakHourRange = `${peakHour.toString().padStart(2, '0')}:00-${(peakHour + 1).toString().padStart(2, '0')}:00`
    
    // Pattern insights
    const seizurePatterns = [
      `Peak activity: ${peakHourRange} (${peakCount} seizures)`,
      `Total seizures tracked: ${totalSeizures}`,
      `Average duration: ${avgDuration} seconds`,
      `Date range: ${firstRecord} to today`,
    ]
    
    // Health and Wellness insights
    const healthInsights = [
      `Average pain level: ${avgPain} / 10`,
      `Food tracking: ${foodEatenCount} with food, ${noFoodCount} without food`,
      `Period-related seizures: ${periodRelatedCount}`,
      `7-day average: ${(recentSeizures7Days).toFixed(1)} seizures`,
    ]

    // Heart rate timeline (from Apple Watch)
    const heartRateTimeline = appleWatchData
      .filter((d) => d['Heart Rate [Avg] (count/min)'])
      .slice(-24)
      .map((d) => ({
        time: d['Date/Time']?.split(' ')[1] || '',
        heartRate: parseFloat(
          d['Heart Rate [Avg] (count/min)'] || 0
        ),
      }))

    // Sleep timeline
    const sleepTimeline = appleWatchData
      .filter((d) => d['Sleep Analysis [Total] (hr)'])
      .slice(-7)
      .map((d) => ({
        date: d['Date/Time']?.split(' ')[0] || '',
        sleep: parseFloat(d['Sleep Analysis [Total] (hr)'] || 0),
      }))

    // Create day of week seizure data
    const dayOfWeekMap = new Map<string, number>()
    const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dayOrder.forEach(day => dayOfWeekMap.set(day, 0))
    
    seizures.forEach((s) => {
      if (s.Date) {
        // Parse date as local date (not UTC) to avoid timezone offset issues
        const [year, month, day] = s.Date.split('-').map(Number)
        const date = new Date(year, month - 1, day)
        const dayName = date.toLocaleDateString('en-US', { weekday: 'long' })
        dayOfWeekMap.set(dayName, (dayOfWeekMap.get(dayName) || 0) + 1)
      }
    })
    
    const dayOfWeekDistribution = dayOrder.map(day => ({
      day,
      count: dayOfWeekMap.get(day) || 0,
    }))

    // Seizure records for DataTable
    const seizureRecords = seizures.map((s) => {
      const date = s.Date || '2025-01-01'
      const time = s.Time || '00:00:00'
      // Create timestamp as local time (not UTC) to match the date/time in the CSV
      const timestamp = `${date}T${time}`
      // Parse date as local date (not UTC) to avoid timezone offset issues
      const [year, month, day] = date.split('-').map(Number)
      const dateObj = new Date(year, month - 1, day)
      return {
        timestamp,
        duration_seconds: parseInt(s.Duration) || 0,
        hour_of_day: parseInt(time.split(':')[0]) || 0,
        day_of_week: dateObj.toLocaleDateString('en-US', { weekday: 'long' }),
        period: s['Peiod'] === 'True',
        food_eaten: s['Eaten'] === 'True',
      }
    })

    const responseData: DashboardData = {
      last_updated: new Date().toISOString(),
      statistics: {
        total_seizures: totalSeizures,
        recent_seizures_7_days: recentSeizures7Days,
        avg_per_week: avgPerWeek,
        avg_duration: avgDuration.toString(),
        min_duration: minDuration.toString(),
        max_duration: maxDuration.toString(),
        date_range_days: dateRangeDays,
        avg_per_day: parseFloat(avgPerDay),
        food_eaten_count: foodEatenCount,
        no_food_count: noFoodCount,
        first_record: firstRecord,
        period_related_count: periodRelatedCount,
        avg_pain: parseFloat(avgPain),
        recent_seizures: recentSeizures,
      },
      predictions: {
        '24h': predictions['24h'],
        '48h': predictions['48h'],
        '72h': predictions['72h'],
      },
      charts: {
        hour_distribution: hourDistribution,
        monthly_distribution: monthlyDistribution,
        day_of_week_distribution: dayOfWeekDistribution,
        duration_distribution: durationDistribution,
        hourly_seizures: hourDistribution,
        monthly_seizures: monthlyDistribution,
      },
      insights: {
        period_related_count: periodRelatedCount,
        total_seizures: totalSeizures,
        food_eaten_count: foodEatenCount,
        duration_mean: avgDuration.toString(),
        duration_min: minDuration.toString(),
        duration_max: maxDuration.toString(),
        duration_stats: avgDuration ? true : false,
      },
      health_insights: {
        sleep_analysis: {
          before_seizure_avg_total: 5.5,
          baseline_avg_total: 7.2,
          before_seizure_avg_deep: 1.2,
          baseline_avg_deep: 1.8,
          before_seizure_avg_rem: 1.1,
          baseline_avg_rem: 1.5,
          before_seizure_count: recentSeizures7Days,
          baseline_count: 7,
        },
        heart_rate_analysis: {
          seizure_day_min_hr: 65,
          baseline_min_hr: 58,
        },
        activity_analysis: {
          before_seizure_avg_distance: 2.1,
          baseline_avg_distance: 3.5,
        },
      },
      health_charts: {
        heart_rate_timeline: heartRateTimeline,
        sleep_timeline: sleepTimeline,
      },
      pnes_analysis: analyzePNESIndicators(seizureRecords, painRecords, appleWatchData),
      ...calculateMedicalInsights(seizureRecords, painRecords),
      timeline: seizureRecords,
      records: seizureRecords,
    }

    res.status(200).json(responseData)
  } catch (error) {
    console.error('Error reading data:', error)
    res.status(500).json({
      error:
        error instanceof Error ? error.message : 'Failed to load data',
    })
  }
}
