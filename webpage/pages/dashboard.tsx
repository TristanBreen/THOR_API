import React, { useCallback, useEffect, useMemo, useState } from 'react'
import Head from 'next/head'
import { RefreshCw, Download, ChevronDown, ChevronLeft, ChevronRight, Zap } from 'lucide-react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, LineChart, Line, CartesianGrid } from 'recharts'

type Summary = any
const C = { ink: '#2D2926', muted: '#6B655F', line: '#E5E1D8', card: '#FFFDF8', bg: '#F6F2E9', sage: '#4A7C59', sageLight: '#A9C4AE', amber: '#B7791F', rose: '#B4475C' }

function Card({ title, children, right, className = '' }: { title?: string; children: React.ReactNode; right?: React.ReactNode; className?: string }) {
  return (
    <section className={`rounded-2xl border p-4 sm:p-5 ${className}`} style={{ background: C.card, borderColor: C.line }}>
      {title && <div className="mb-3 flex items-center justify-between gap-2"><h2 className="text-[15px] font-semibold" style={{ color: C.ink }}>{title}</h2>{right}</div>}
      {children}
    </section>
  )
}
const Muted = ({ children, className = '' }: any) => <p className={`text-[13px] leading-snug ${className}`} style={{ color: C.muted }}>{children}</p>

function sinceText(days: number | null) {
  if (days == null) return { big: '—', unit: '' }
  if (days < 1) { const h = Math.max(1, Math.round(days * 24)); return { big: String(h), unit: h === 1 ? 'hour' : 'hours' } }
  const d = Math.floor(days); return { big: String(d), unit: d === 1 ? 'day' : 'days' }
}

function Hero({ s }: { s: Summary }) {
  const t = sinceText(s.last?.days_since ?? null)
  const typ = s.month.typical
  return (
    <Card>
      <div className="flex items-end gap-2">
        <span className="text-6xl font-bold leading-none tracking-tight" style={{ color: C.ink }}>{t.big}</span>
        <span className="pb-1 text-lg font-medium" style={{ color: C.ink }}>{t.unit}</span>
      </div>
      <p className="mt-1 text-[15px]" style={{ color: C.ink }}>since the last seizure</p>
      {s.last && <Muted className="mt-1">{s.last.day} at {s.last.time} · lasted {s.last.duration}</Muted>}
      <div className="mt-4 grid grid-cols-2 gap-3">
        <Stat label={`This ${s.month.name}`} value={s.month.count} note={typ != null ? `typical month: ${typ % 1 ? typ.toFixed(1) : typ}` : ''} />
        <Stat label="Last 30 days" value={s.last30.count} note={`30 days before: ${s.last30.prev}`} />
      </div>
      {s.streak && s.streak.longest_days > 0 && (
        <div className="mt-4">
          <div className="flex justify-between text-[12px]" style={{ color: C.muted }}>
            <span>Seizure-free stretch</span><span>longest: {s.streak.longest_days} days</span>
          </div>
          <div className="mt-1 h-2 overflow-hidden rounded-full" style={{ background: C.bg }}>
            <div className="h-full rounded-full" style={{ width: `${Math.min(100, (s.streak.current_days / s.streak.longest_days) * 100)}%`, background: C.sage, minWidth: 6 }} />
          </div>
          <Muted className="mt-1">{s.streak.longer_before === 0 ? 'Her longest stretch yet.' : `${s.streak.longer_before} of ${s.streak.total_gaps} past stretches were longer than this one so far.`}</Muted>
        </div>
      )}
    </Card>
  )
}
const Stat = ({ label, value, note }: any) => (
  <div className="rounded-xl p-3" style={{ background: C.bg }}>
    <div className="text-[12px] font-medium uppercase tracking-wide" style={{ color: C.muted }}>{label}</div>
    <div className="text-2xl font-bold" style={{ color: C.ink }}>{value}</div>
    {note && <div className="text-[12px]" style={{ color: C.muted }}>{note}</div>}
  </div>
)

function Risk({ p, after }: { p: any; after?: any }) {
  if (!p) return <Card title="Chance of a seizure"><Muted>Prediction not available right now.</Muted></Card>
  const lvl = { lower: ['Lower than usual', C.sage, '#E8F1EA'], usual: ['About usual', C.amber, '#FBF1DF'], higher: ['Higher than usual', C.rose, '#F8E5E9'] }[p.level as 'lower' | 'usual' | 'higher']
  return (
    <Card title="Chance of a seizure" right={p.source === 'v2' && <span className="rounded-full px-2.5 py-1 text-[12px] font-semibold" style={{ color: lvl[1], background: lvl[2] }}>{lvl[0]}</span>}>
      {after && (
        <div className="mb-3 rounded-xl px-3 py-2 text-[13px] leading-snug" style={{ background: '#FBF1DF', color: '#7A5212' }}>
          After a seizure, another has followed within 3 days {after.pct72}% of the time.
        </div>
      )}
      <div className="grid grid-cols-3 gap-2 text-center">
        {[['24h', 'next 24 hours'], ['48h', 'next 2 days'], ['72h', 'next 3 days']].map(([k, label]) => (
          <div key={k} className="rounded-xl py-3" style={{ background: C.bg }}>
            <div className="text-2xl font-bold" style={{ color: C.ink }}>{Math.round(p[`p${k.slice(0, 2)}`])}%</div>
            <div className="text-[12px]" style={{ color: C.muted }}>{label}</div>
          </div>
        ))}
      </div>
      {p.typical24 != null && <Muted className="mt-3">Her typical lately: about {Math.round(p.typical24)}% on any given day.{p.updated ? ` Updated ${p.updated}.` : ''}</Muted>}
      <details className="mt-2 group">
        <summary className="flex cursor-pointer list-none items-center gap-1 text-[13px] font-medium" style={{ color: C.sage }}>How reliable is this? <ChevronDown className="h-4 w-4 transition group-open:rotate-180" /></summary>
        <div className="mt-2 space-y-2">
          <Muted>It looks at how recently and how often seizures have happened (they tend to cluster) and the time of day. It can tell busier stretches from quieter ones; it can’t predict a specific seizure.</Muted>
          {p.validation && <Muted>{p.validation}</Muted>}
          {p.live?.['24h'] && <Muted>Since it started running live: said {p.live['24h'].said_avg}% on average for the next 24 hours; a seizure followed {p.live['24h'].happened}% of the time ({p.live['24h'].n} predictions).</Muted>}
        </div>
      </details>
    </Card>
  )
}

function Trend({ s }: { s: Summary }) {
  const [range, setRange] = useState<'6m' | '1y' | 'all'>('6m')
  const data = useMemo(() => {
    const n = range === '6m' ? 26 : range === '1y' ? 52 : s.weekly.length
    return s.weekly.slice(-n)
  }, [s.weekly, range])
  const max = Math.max(1, ...data.map((d: any) => d.count))
  return (
    <Card title="Seizures per week" right={
      <div className="flex rounded-lg p-0.5" style={{ background: C.bg }}>
        {(['6m', '1y', 'all'] as const).map((r) => (
          <button key={r} onClick={() => setRange(r)} className="rounded-md px-2.5 py-1 text-[12px] font-semibold"
            style={range === r ? { background: C.card, color: C.ink, boxShadow: '0 1px 2px rgba(0,0,0,.08)' } : { color: C.muted }}>{r === 'all' ? 'All' : r === '6m' ? '6 mo' : '1 yr'}</button>
        ))}
      </div>}>
      <div className="h-44 -ml-3">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke={C.line} />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: C.muted }} tickLine={false} axisLine={false} interval="preserveStartEnd" minTickGap={28} />
            <YAxis allowDecimals={false} width={28} tick={{ fontSize: 11, fill: C.muted }} tickLine={false} axisLine={false} domain={[0, max]} ticks={Array.from(new Set([0, Math.ceil(max / 2), max]))} />
            <Tooltip cursor={{ fill: 'rgba(0,0,0,.04)' }} formatter={(v: any) => [v, 'seizures']} labelFormatter={(l) => `Week of ${l}`} />
            <Bar dataKey="count" radius={[3, 3, 0, 0]}>
              {data.map((d: any, i: number) => <Cell key={d.week} fill={i === data.length - 1 ? C.sage : C.sageLight} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <Muted className="mt-1">{s.total} seizures logged since {s.first}.</Muted>
    </Card>
  )
}

function Pain({ pain }: { pain: any }) {
  if (!pain.latest) return null
  return (
    <Card title="Pain" right={<span className="text-[13px]" style={{ color: C.muted }}>last 30 days</span>}>
      <div className="mb-2 flex items-baseline gap-4">
        <div><span className="text-2xl font-bold" style={{ color: C.ink }}>{pain.latest.value}</span><span style={{ color: C.muted }}>/10</span><Muted>latest · {pain.latest.day}</Muted></div>
        {pain.avg30 != null && <div><span className="text-2xl font-bold" style={{ color: C.ink }}>{pain.avg30}</span><span style={{ color: C.muted }}>/10</span><Muted>30-day average</Muted></div>}
      </div>
      <div className="h-32 -ml-3">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={pain.daily30} margin={{ top: 6, right: 6, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke={C.line} />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: C.muted }} tickLine={false} axisLine={false} interval="preserveStartEnd" minTickGap={30} />
            <YAxis domain={[0, 10]} ticks={[0, 5, 10]} width={28} tick={{ fontSize: 11, fill: C.muted }} tickLine={false} axisLine={false} />
            <Tooltip formatter={(v: any) => [v, 'avg pain']} />
            <Line dataKey="avg" stroke={C.rose} strokeWidth={2} connectNulls
              dot={(props: any) => props.payload.seizure ? <circle key={props.index} cx={props.cx} cy={props.cy} r={4} fill={C.ink} /> : <g key={props.index} />} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <Muted className="mt-1">Dark dots mark days with a seizure.</Muted>
    </Card>
  )
}

function Calendar({ s }: { s: Summary }) {
  const today = new Date(s.today + 'T12:00:00')
  const [offset, setOffset] = useState(0)
  const first = new Date(today.getFullYear(), today.getMonth() - offset, 1)
  const days = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate()
  const lead = (first.getDay() + 6) % 7                       // Monday-first grid
  const key = (d: number) => `${first.getFullYear()}-${String(first.getMonth() + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
  const earliest = s.first_day ? new Date(s.first_day + 'T12:00:00') : today
  const canBack = first > new Date(earliest.getFullYear(), earliest.getMonth(), 1)
  const total = Array.from({ length: days }, (_, i) => s.calendar[key(i + 1)] || 0).reduce((a: number, b: number) => a + b, 0)
  const btn = 'flex h-9 w-9 items-center justify-center rounded-full disabled:opacity-30'
  return (
    <Card title="Calendar" right={
      <div className="flex items-center gap-1">
        <button className={btn} style={{ background: C.bg }} disabled={!canBack} onClick={() => setOffset(offset + 1)} aria-label="Previous month"><ChevronLeft className="h-5 w-5" style={{ color: C.ink }} /></button>
        <button className={btn} style={{ background: C.bg }} disabled={offset === 0} onClick={() => setOffset(offset - 1)} aria-label="Next month"><ChevronRight className="h-5 w-5" style={{ color: C.ink }} /></button>
      </div>}>
      <div className="mb-2 flex items-baseline justify-between">
        <span className="text-[15px] font-semibold" style={{ color: C.ink }}>{first.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>
        <span className="text-[13px]" style={{ color: C.muted }}>{total} seizure{total === 1 ? '' : 's'}</span>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center text-[11px] font-medium" style={{ color: C.muted }}>
        {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => <div key={i}>{d}</div>)}
      </div>
      <div className="mt-1 grid grid-cols-7 gap-1">
        {Array.from({ length: lead }, (_, i) => <div key={'x' + i} />)}
        {Array.from({ length: days }, (_, i) => {
          const k = key(i + 1), c = s.calendar[k] || 0, isToday = k === s.today, future = k > s.today
          return (
            <div key={k} className="flex aspect-square flex-col items-center justify-center rounded-lg text-[13px]"
              style={{ background: c ? (c > 1 ? C.sage : C.sageLight) : C.bg, color: c > 1 ? '#fff' : future ? '#C9C3B8' : C.ink, outline: isToday ? `2px solid ${C.ink}` : 'none', outlineOffset: -2 }}>
              <span className={c ? 'font-semibold' : ''}>{i + 1}</span>
              {c > 1 && <span className="text-[9px] leading-none">×{c}</span>}
            </div>
          )
        })}
      </div>
      <Muted className="mt-2">Shaded days had a seizure; darker means more than one.</Muted>
    </Card>
  )
}

function Duration({ s }: { s: Summary }) {
  const data = s.duration_monthly.filter((m: any) => m.median != null)
  const top = Math.max(120, Math.ceil(Math.max(...data.map((m: any) => m.median)) / 30) * 30)
  const ticks = Array.from({ length: top / 30 + 1 }, (_, i) => i * 30).filter((v) => v % 60 === 0 || top <= 150)
  const mmss = (v: number) => v % 60 ? `${Math.floor(v / 60)}m${v % 60}` : `${v / 60}m`
  const t = s.duration_trend
  return (
    <Card title="How long they last" right={<span className="text-[13px]" style={{ color: C.muted }}>median per month</span>}>
      {t && (
        <div className="mb-2 flex items-baseline gap-4">
          <div><span className="text-2xl font-bold" style={{ color: C.ink }}>{t.recent}</span><Muted>last 10 seizures</Muted></div>
          <div><span className="text-2xl font-bold" style={{ color: C.muted }}>{t.prior}</span><Muted>the 30 before</Muted></div>
        </div>
      )}
      <div className="h-36 -ml-3">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 6, right: 8, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke={C.line} />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: C.muted }} tickLine={false} axisLine={false} interval="preserveStartEnd" minTickGap={28} />
            <YAxis width={44} tick={{ fontSize: 11, fill: C.muted }} tickLine={false} axisLine={false} domain={[0, top]} ticks={ticks} tickFormatter={mmss} />
            <Tooltip formatter={(_v: any, _n: any, item: any) => [`${Math.floor(item.payload.median / 60)}m ${String(item.payload.median % 60).padStart(2, '0')}s (${item.payload.n} seizures)`, 'median']} />
            <Line dataKey="median" stroke={C.sage} strokeWidth={2} dot={{ r: 3, fill: C.sage }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {t?.direction === 'longer' && <Muted className="mt-1">Fewer seizures lately, but longer ones. Worth mentioning to her doctor.</Muted>}
    </Card>
  )
}

function Findings({ items }: { items: any[] }) {
  return (
    <Card title="What the data shows">
      <ul className="space-y-3">
        {items.map((f) => (
          <li key={f.title}><div className="text-[14px] font-semibold" style={{ color: C.ink }}>{f.title}</div><Muted>{f.text}</Muted></li>
        ))}
      </ul>
    </Card>
  )
}

const Tag = ({ on, children, color }: any) => <span className="rounded-full px-2 py-0.5 text-[11px] font-semibold" style={on ? { color, background: color + '1A' } : { color: C.muted, background: C.bg }}>{children}</span>
function Log({ records }: { records: any[] }) {
  const [shown, setShown] = useState(10)
  return (
    <Card title="Seizure log" right={<span className="text-[13px]" style={{ color: C.muted }}>{records.length} total</span>}>
      <ul className="divide-y" style={{ borderColor: C.line }}>
        {records.slice(0, shown).map((r, i) => (
          <li key={i} className="flex items-start justify-between gap-3 py-2.5" style={{ borderColor: C.line }}>
            <div className="min-w-0">
              <div className="text-[14px] font-semibold" style={{ color: C.ink }}>{r.day} <span className="font-normal" style={{ color: C.muted }}>· {r.time}</span></div>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {r.period && <Tag on color={C.rose}>Period</Tag>}
                {r.eaten === true && <Tag on color={C.sage}>{r.food ? `Ate: ${r.food}` : 'Had eaten'}</Tag>}
                {r.eaten === false && <Tag>Hadn’t eaten</Tag>}
                {r.possible_duplicate && <Tag on color={C.amber}>Possible double entry</Tag>}
              </div>
            </div>
            <div className="shrink-0 text-[15px] font-semibold tabular-nums" style={{ color: C.ink }}>{r.duration}</div>
          </li>
        ))}
      </ul>
      {shown < records.length && (
        <button onClick={() => setShown(shown + 20)} className="mt-2 w-full rounded-xl py-2.5 text-[14px] font-semibold" style={{ background: C.bg, color: C.ink }}>Show more</button>
      )}
    </Card>
  )
}

function MiniBars({ data, x, title }: any) {
  return (
    <div>
      <div className="mb-1 text-[13px] font-semibold" style={{ color: C.ink }}>{title}</div>
      <div className="h-32 -ml-3">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke={C.line} />
            <XAxis dataKey={x} tick={{ fontSize: 10, fill: C.muted }} tickLine={false} axisLine={false} interval={data.length <= 8 ? 0 : 'preserveStartEnd'} minTickGap={14} />
            <YAxis allowDecimals={false} width={28} tick={{ fontSize: 10, fill: C.muted }} tickLine={false} axisLine={false} />
            <Tooltip cursor={{ fill: 'rgba(0,0,0,.04)' }} formatter={(v: any) => [v, 'seizures']} />
            <Bar dataKey="count" fill={C.sage} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
function Details({ s }: { s: Summary }) {
  return (
    <Card>
      <details className="group">
        <summary className="flex cursor-pointer list-none items-center justify-between text-[15px] font-semibold" style={{ color: C.ink }}>More charts <ChevronDown className="h-5 w-5 transition group-open:rotate-180" style={{ color: C.muted }} /></summary>
        <div className="mt-4 grid gap-5 sm:grid-cols-2">
          <MiniBars title="By month" data={s.monthly} x="label" />
          <MiniBars title="Time of day logged" data={s.details.hours} x="label" />
          <MiniBars title="How long they lasted" data={s.details.durations} x="label" />
          <MiniBars title="Time since the one before" data={s.details.gaps} x="label" />
        </div>
      </details>
    </Card>
  )
}

export default function Dashboard() {
  const [s, setS] = useState<Summary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [today, setToday] = useState('')   // set in the browser (her local date), avoids server/client mismatch
  useEffect(() => { setToday(new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })) }, [])
  const load = useCallback(async () => {
    setLoading(true)
    try {
      const r = await fetch('/api/summary', { cache: 'no-store' })
      if (!r.ok) throw new Error(String(r.status))
      setS(await r.json()); setError(null)
    } catch { setError('Couldn’t load the data. Pull to refresh or tap ↻.') } finally { setLoading(false) }
  }, [])
  useEffect(() => { load(); const id = setInterval(load, 5 * 60000); return () => clearInterval(id) }, [load])

  return (
    <>
      <Head>
        <title>Seizure Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <meta name="theme-color" content={C.bg} />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>" />
      </Head>
      <main className="min-h-screen pb-10" style={{ background: C.bg }}>
        <header className="border-b" style={{ background: `linear-gradient(180deg, #EEF3EB 0%, ${C.bg} 100%)`, borderColor: C.line, paddingTop: 'env(safe-area-inset-top)' }}>
          <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 pb-5 pt-6 sm:pb-7 sm:pt-9">
            <div className="flex min-w-0 items-center gap-3 sm:gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl shadow-sm sm:h-14 sm:w-14" style={{ background: C.sage }}>
                <Zap className="h-6 w-6 sm:h-7 sm:w-7" fill="#FFFDF8" strokeWidth={0} />
              </div>
              <div className="min-w-0">
                <h1 className="font-serif text-[28px] font-bold leading-tight tracking-tight sm:text-4xl" style={{ color: C.ink }}>Seizure Dashboard</h1>
                <p className="mt-0.5 text-[15px] font-medium" style={{ color: C.muted }}>{today}</p>
                <p className="text-[12px]" style={{ color: C.muted, opacity: 0.8 }}>{s ? `Updated ${s.updated}` : 'Loading…'}</p>
              </div>
            </div>
            <button onClick={load} aria-label="Refresh" className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full shadow-sm active:scale-95 sm:h-12 sm:w-12" style={{ background: C.card, border: `1px solid ${C.line}` }}>
              <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} style={{ color: C.ink }} />
            </button>
          </div>
        </header>

        <div className="mx-auto max-w-5xl space-y-3 px-4 pt-4 lg:grid lg:grid-cols-2 lg:items-start lg:gap-4 lg:space-y-0">
          {error && <div className="rounded-xl p-3 text-[14px] lg:col-span-2" style={{ background: '#F8E5E9', color: C.rose }}>{error}</div>}
          {!s && !error && [1, 2, 3].map((i) => <div key={i} className="h-40 animate-pulse rounded-2xl" style={{ background: C.card }} />)}
          {s && (<>
            <Hero s={s} />
            <Risk p={s.prediction} after={s.after_seizure} />
            <div className="lg:col-span-2"><Trend s={s} /></div>
            <Calendar s={s} />
            <Duration s={s} />
            <Pain pain={s.pain} />
            <Findings items={s.findings} />
            <div className="lg:col-span-2"><Log records={s.records} /></div>
            <div className="lg:col-span-2"><Details s={s} /></div>
            <a href="/api/export" className="flex items-center justify-center gap-2 rounded-xl border py-3 text-[14px] font-semibold lg:col-span-2" style={{ borderColor: C.line, color: C.ink, background: C.card }}>
              <Download className="h-4 w-4" /> Download all data (CSV)
            </a>
          </>)}
        </div>
      </main>
    </>
  )
}
