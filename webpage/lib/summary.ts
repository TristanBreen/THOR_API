// Everything the dashboard shows, computed from her real data (read-only). Nothing here is hard-coded.
import fs from 'fs'
import path from 'path'
import { parse } from 'csv-parse/sync'

const DATA_DIR = process.env.THOR_DATA_DIR || '/data/Data'
const PRED_DIR = process.env.THOR_PREDICTIONS_DIR || '/predictions'
const DAY = 86400000

type Row = Record<string, string>
export interface Seizure { t: Date; duration: number | null; period: boolean | null; eaten: boolean | null; food: string }

function readCsv(file: string): Row[] {
  const p = path.join(DATA_DIR, file)
  if (!fs.existsSync(p)) return []
  const rows = parse(fs.readFileSync(p, 'utf-8'), { columns: (h: string[]) => h.map((c) => c.trim()), skip_empty_lines: true, relax_column_count: true, bom: true }) as Row[]
  return rows
}
const bool = (v?: string) => { const s = (v || '').trim(); return s === 'True' ? true : s === 'False' ? false : null }
function localDate(d: string, t: string) {               // CSV times are local wall-clock (Arizona)
  const [y, m, dd] = d.trim().split('-').map(Number); const [h, mi, s] = (t || '0:0:0').trim().split(':').map(Number)
  const out = new Date(y, m - 1, dd, h || 0, mi || 0, s || 0); return isNaN(out.getTime()) ? null : out
}
const fmt = (d: Date, o: Intl.DateTimeFormatOptions) => d.toLocaleString('en-US', o)
const dayLabel = (d: Date) => fmt(d, { weekday: 'short', month: 'short', day: 'numeric' })
const timeLabel = (d: Date) => fmt(d, { hour: 'numeric', minute: '2-digit' })
export const durLabel = (s: number | null) => s == null ? '—' : s < 60 ? `${Math.round(s)}s` : `${Math.floor(s / 60)}m ${String(Math.round(s % 60)).padStart(2, '0')}s`
const median = (a: number[]) => { if (!a.length) return NaN; const b = [...a].sort((x, y) => x - y); const m = b.length >> 1; return b.length % 2 ? b[m] : (b[m - 1] + b[m]) / 2 }
const quant = (a: number[], q: number) => { const b = [...a].sort((x, y) => x - y); return b[Math.min(b.length - 1, Math.max(0, Math.round(q * (b.length - 1))))] }
const ymd = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
const pct = (a: number, b: number) => b ? Math.round((a / b) * 100) : 0

export function loadSeizures(): Seizure[] {
  return readCsv('seizures.csv').map((r) => {
    const t = localDate(r['Date'] || '', r['Time'] || '')
    const dur = parseFloat(r['Duration']); const food = (r['Food Eaten'] ?? r['FoodEaten'] ?? '').trim()
    return t && { t, duration: isFinite(dur) ? dur : null, period: bool(r['Peiod'] ?? r['Period']), eaten: bool(r['Eaten']), food: food === 'NULL' ? '' : food }
  }).filter(Boolean).sort((a: any, b: any) => a.t - b.t) as Seizure[]
}

function loadPain() {
  return readCsv('pain.csv').map((r) => ({ t: localDate(r['Date'] || '', r['Time'] || ''), v: parseFloat(r['Pain']) }))
    .filter((p) => p.t && isFinite(p.v)).sort((a: any, b: any) => a.t - b.t) as { t: Date; v: number }[]
}

function loadPrediction(now: Date) {
  try {   // new model (thor-predict-v2)
    const s = JSON.parse(fs.readFileSync(path.join(PRED_DIR, 'status.json'), 'utf-8'))
    const p = s.predictions; const typical = s.typical_24h_lately
    const ratio = typical ? p['24h'] / typical : 1
    return {
      source: 'v2', p24: p['24h'], p48: p['48h'], p72: p['72h'], typical24: typical,
      level: ratio < 0.75 ? 'lower' : ratio > 1.33 ? 'higher' : 'usual',
      updated: s.updated ? timeLabel(new Date(s.updated)) : null,
      validation: s.validation || null, live: s.live_accuracy || {},
    }
  } catch { return null }   // shown as "Prediction not available right now"
}

export function buildSummary() {
  const now = new Date()
  const S = loadSeizures(); const P = loadPain()
  const last = S[S.length - 1]
  const n = S.length

  // --- headline numbers
  const monthKey = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  const byMonth = new Map<string, number>(); S.forEach((s) => byMonth.set(monthKey(s.t), (byMonth.get(monthKey(s.t)) || 0) + 1))
  const thisMonth = monthKey(now)
  const prevMonths: number[] = []
  for (let i = 1; i <= 6; i++) { const d = new Date(now.getFullYear(), now.getMonth() - i, 1); if (S.length && d >= new Date(S[0].t.getFullYear(), S[0].t.getMonth(), 1)) prevMonths.push(byMonth.get(monthKey(d)) || 0) }
  const in30 = S.filter((s) => now.getTime() - s.t.getTime() < 30 * DAY).length
  const prev30 = S.filter((s) => { const a = now.getTime() - s.t.getTime(); return a >= 30 * DAY && a < 60 * DAY }).length
  const daysSince = last ? (now.getTime() - last.t.getTime()) / DAY : null

  // --- weekly counts (weeks start Monday), every week since the first seizure
  const weekStart = (d: Date) => { const x = new Date(d.getFullYear(), d.getMonth(), d.getDate()); x.setDate(x.getDate() - ((x.getDay() + 6) % 7)); return x }
  const weekly: { week: string; label: string; count: number }[] = []
  if (n) { const counts = new Map<string, number>(); S.forEach((s) => { const k = ymd(weekStart(s.t)); counts.set(k, (counts.get(k) || 0) + 1) })
    for (let w = weekStart(S[0].t); w <= now; w = new Date(w.getFullYear(), w.getMonth(), w.getDate() + 7)) weekly.push({ week: ymd(w), label: fmt(w, { month: 'short', day: 'numeric' }), count: counts.get(ymd(w)) || 0 }) }
  const monthly = [...byMonth.entries()].sort().map(([k, c]) => ({ month: k, label: fmt(new Date(+k.slice(0, 4), +k.slice(5) - 1, 1), { month: 'short', year: '2-digit' }), count: c }))

  // --- honest findings (each says what it's based on)
  const findings: { title: string; text: string }[] = []
  const gaps = S.slice(1).map((s, i) => (s.t.getTime() - S[i].t.getTime()) / DAY)
  const within24 = gaps.filter((g) => g <= 1).length, within72 = gaps.filter((g) => g <= 3).length
  if (gaps.length > 10) {
    findings.push({ title: 'The days after a seizure', text: `In the 3 days after a seizure, another followed ${pct(within72, gaps.length)}% of the time (${pct(within24, gaps.length)}% within 24 hours). The typical gap is ${median(gaps) < 1 ? Math.round(median(gaps) * 24) + ' hours' : median(gaps).toFixed(1) + ' days'}.` })
  }
  const busiest = monthly.reduce((a, b) => (b.count > (a?.count ?? -1) ? b : a), monthly[0])
  if (busiest && prevMonths.length >= 3) {
    const recent3 = prevMonths.slice(0, 3); const avg = recent3.reduce((a, b) => a + b, 0) / 3
    findings.push({ title: 'Recent months vs her busiest', text: `The busiest month was ${fmt(new Date(+busiest.month.slice(0, 4), +busiest.month.slice(5) - 1, 1), { month: 'long', year: 'numeric' })} (${busiest.count}). The last 3 full months averaged ${avg.toFixed(1)} a month.` })
  }
  const afternoon = S.filter((s) => s.t.getHours() >= 12 && s.t.getHours() < 18).length
  if (n) findings.push({ title: 'Time of day', text: `${pct(afternoon, n)}% were logged between 12 and 6 PM. This shows when they were logged; seizures during sleep may go unrecorded.` })
  const durs = S.map((s) => s.duration).filter((d): d is number => d != null && d > 0)
  if (durs.length) findings.push({ title: 'How long they last', text: `Typically ${durLabel(median(durs))}; most are between ${durLabel(quant(durs, 0.25))} and ${durLabel(quant(durs, 0.75))}. Longest: ${durLabel(Math.max(...durs))}.` })
  const withDur = S.filter((s) => s.duration != null && s.duration > 0)
  const recentDur = withDur.slice(-10).map((s) => s.duration!), priorDur = withDur.slice(-40, -10).map((s) => s.duration!)
  let durTrend: any = null
  if (recentDur.length >= 8 && priorDur.length >= 15) {
    const a = median(recentDur), b = median(priorDur), change = (a - b) / b
    durTrend = { recent: durLabel(a), prior: durLabel(b), direction: change > 0.2 ? 'longer' : change < -0.2 ? 'shorter' : 'same' }
    findings.unshift({ title: durTrend.direction === 'same' ? 'Seizure length is steady' : `Recent seizures have been ${durTrend.direction}`,
      text: `The last 10 lasted ${durTrend.recent} (median) vs ${durTrend.prior} for the 30 before.${durTrend.direction === 'longer' ? ' Worth mentioning to her doctor. Part of it could be a change in how they’re timed.' : ''}` })
  }
  const dowCounts = [1, 2, 3, 4, 5, 6, 0].map((d) => S.filter((s) => s.t.getDay() === d).length)   // Mon..Sun
  if (n >= 50) {
    const exp = n / 7, chi = dowCounts.reduce((a, c) => a + (c - exp) ** 2 / exp, 0)          // > 12.6 = unlikely by chance (5%)
    const wkday = dowCounts.slice(0, 5).reduce((a, b) => a + b, 0) / 5, wkend = (dowCounts[5] + dowCounts[6]) / 2
    if (chi > 12.6 && Math.abs(wkday - wkend) / Math.max(wkday, wkend) > 0.25)
      findings.push({ title: wkend < wkday ? 'Weekends are quieter' : 'Weekends are busier', text: `Since tracking began, each weekday has had about ${Math.round(wkday)} seizures in total, vs about ${Math.round(wkend)} each for Saturday and Sunday. That's more of a difference than chance would explain. It could reflect routine, stress or where she is, not necessarily the day itself.` })
  }
  const withP = S.filter((s) => s.period !== null); const onP = withP.filter((s) => s.period).length
  if (withP.length) findings.push({ title: 'Period', text: `${onP} of ${withP.length} seizures (${pct(onP, withP.length)}%) were logged during her period. Period is only recorded when a seizure is logged, so this can't show a monthly pattern yet.` })
  const withF = S.filter((s) => s.eaten !== null && s.duration != null)
  if (withF.length > 10) {
    const a = withF.filter((s) => s.eaten).map((s) => s.duration!); const b = withF.filter((s) => !s.eaten).map((s) => s.duration!)
    const ma = median(a), mb = median(b); const same = Math.abs(ma - mb) < 0.2 * median(durs)
    findings.push({ title: 'Food', text: `${a.length} after eating, ${b.length} without. Length was ${same ? 'about the same either way' : ma > mb ? 'longer after eating' : 'longer without food'} (${durLabel(ma)} vs ${durLabel(mb)}).` })
  }

  // --- pain
  const painByDay = new Map<string, number[]>(); P.forEach((p) => { const k = ymd(p.t); painByDay.set(k, [...(painByDay.get(k) || []), p.v]) })
  const dayAvg = (k: string) => { const v = painByDay.get(k)!; return v.reduce((a, b) => a + b, 0) / v.length }
  const seizureDays = new Set(S.map((s) => ymd(s.t)))
  const sd = [...painByDay.keys()].filter((k) => seizureDays.has(k)).map(dayAvg), od = [...painByDay.keys()].filter((k) => !seizureDays.has(k)).map(dayAvg)
  const mean = (a: number[]) => a.length ? a.reduce((x, y) => x + y, 0) / a.length : NaN
  const daily30: { day: string; label: string; avg: number | null; seizure: boolean }[] = []
  for (let i = 29; i >= 0; i--) { const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i); const k = ymd(d)
    daily30.push({ day: k, label: fmt(d, { month: 'short', day: 'numeric' }), avg: painByDay.has(k) ? Math.round(dayAvg(k) * 10) / 10 : null, seizure: seizureDays.has(k) }) }
  const last30vals = P.filter((p) => now.getTime() - p.t.getTime() < 30 * DAY).map((p) => p.v)
  const lastPain = P[P.length - 1]
  if (sd.length >= 5 && od.length >= 5) findings.push({ title: 'Pain and seizures', text: `Pain averaged ${mean(sd).toFixed(1)} on days with a seizure vs ${mean(od).toFixed(1)} on other days (${sd.length} vs ${od.length} days with pain logged). That's a link, not proof of a cause.` })

  // --- details charts
  const hours = Array.from({ length: 24 }, (_, h) => ({ hour: h, label: fmt(new Date(2000, 0, 1, h), { hour: 'numeric' }), count: S.filter((s) => s.t.getHours() === h).length }))
  const dbins: [string, number, number][] = [['<30s', 0, 30], ['30–60s', 30, 60], ['1–1½m', 60, 90], ['1½–2m', 90, 120], ['2–3m', 120, 180], ['3m+', 180, 1e9]]
  const gbins: [string, number, number][] = [['<1 day', 0, 1], ['1–3 days', 1, 3], ['3–7 days', 3, 7], ['1–2 wks', 7, 14], ['2+ wks', 14, 1e9]]

  // --- the log, newest first; flag entries logged under 2 minutes after the previous one
  const records = S.map((s, i) => ({
    day: dayLabel(s.t), time: timeLabel(s.t), date: ymd(s.t), duration: durLabel(s.duration), period: s.period, eaten: s.eaten, food: s.food,
    possible_duplicate: i > 0 && s.t.getTime() - S[i - 1].t.getTime() < 120000,
  })).reverse()

  return {
    updated: timeLabel(now), updated_iso: now.toISOString(),
    total: n, first: n ? fmt(S[0].t, { month: 'short', day: 'numeric', year: 'numeric' }) : null,
    last: last ? { day: dayLabel(last.t), time: timeLabel(last.t), duration: durLabel(last.duration), days_since: daysSince } : null,
    month: { name: fmt(now, { month: 'long' }), count: byMonth.get(thisMonth) || 0, typical: prevMonths.length ? median(prevMonths) : null, day_of_month: now.getDate() },
    last30: { count: in30, prev: prev30 },
    prediction: loadPrediction(now),
    weekly, monthly, findings,
    streak: daysSince == null ? null : { current_days: Math.floor(daysSince), longest_days: gaps.length ? Math.floor(Math.max(...gaps, daysSince)) : Math.floor(daysSince), longer_before: gaps.filter((g) => g > daysSince).length, total_gaps: gaps.length },
    after_seizure: last && daysSince != null && daysSince < 3 && gaps.length > 10 ? { pct72: pct(within72, gaps.length), hours_left: Math.max(1, Math.round((3 - daysSince) * 24)) } : null,
    duration_trend: durTrend,
    duration_monthly: monthly.map((m) => { const v = withDur.filter((s) => monthKey(s.t) === m.month).map((s) => s.duration!); return { month: m.month, label: m.label, median: v.length ? Math.round(median(v)) : null, n: v.length } }),
    calendar: (() => { const c: Record<string, number> = {}; S.forEach((s) => { const k = ymd(s.t); c[k] = (c[k] || 0) + 1 }); return c })(),
    today: ymd(now), first_day: n ? ymd(S[0].t) : null,
    pain: { latest: lastPain ? { value: lastPain.v, day: dayLabel(lastPain.t), time: timeLabel(lastPain.t) } : null, avg30: last30vals.length ? Math.round(mean(last30vals) * 10) / 10 : null, daily30 },
    details: {
      hours,
      durations: dbins.map(([label, a, b]) => ({ label, count: durs.filter((d) => d >= a && d < b).length })),
      gaps: gbins.map(([label, a, b]) => ({ label, count: gaps.filter((g) => g >= a && g < b).length })),
    },
    records,
  }
}
