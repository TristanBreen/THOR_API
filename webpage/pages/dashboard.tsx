import React, { useCallback, useEffect, useMemo, useState } from 'react'
import Head from 'next/head'
import { RefreshCw, Download, ChevronDown } from 'lucide-react'
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

function Risk({ p }: { p: any }) {
  if (!p) return <Card title="Chance of a seizure"><Muted>Prediction not available right now.</Muted></Card>
  const lvl = { lower: ['Lower than usual', C.sage, '#E8F1EA'], usual: ['About usual', C.amber, '#FBF1DF'], higher: ['Higher than usual', C.rose, '#F8E5E9'] }[p.level as 'lower' | 'usual' | 'higher']
  return (
    <Card title="Chance of a seizure" right={p.source === 'v2' && <span className="rounded-full px-2.5 py-1 text-[12px] font-semibold" style={{ color: lvl[1], background: lvl[2] }}>{lvl[0]}</span>}>
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
        <header className="sticky top-0 z-10 border-b backdrop-blur" style={{ background: C.bg + 'EE', borderColor: C.line, paddingTop: 'env(safe-area-inset-top)' }}>
          <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
            <div>
              <h1 className="text-lg font-bold" style={{ color: C.ink }}>Seizure Dashboard</h1>
              <p className="text-[12px]" style={{ color: C.muted }}>{s ? `Updated ${s.updated}` : 'Loading…'}</p>
            </div>
            <button onClick={load} aria-label="Refresh" className="rounded-full p-2.5" style={{ background: C.card, border: `1px solid ${C.line}` }}>
              <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} style={{ color: C.ink }} />
            </button>
          </div>
        </header>

        <div className="mx-auto max-w-5xl space-y-3 px-4 pt-3 lg:grid lg:grid-cols-2 lg:items-start lg:gap-4 lg:space-y-0">
          {error && <div className="rounded-xl p-3 text-[14px] lg:col-span-2" style={{ background: '#F8E5E9', color: C.rose }}>{error}</div>}
          {!s && !error && [1, 2, 3].map((i) => <div key={i} className="h-40 animate-pulse rounded-2xl" style={{ background: C.card }} />)}
          {s && (<>
            <Hero s={s} />
            <Risk p={s.prediction} />
            <div className="lg:col-span-2"><Trend s={s} /></div>
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
