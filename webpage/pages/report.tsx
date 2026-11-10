// Doctor summary: a printable page built from the same live numbers as the dashboard (/api/summary).
import React, { useEffect, useState } from 'react'
import Head from 'next/head'

const ink = '#1F1B18', muted = '#5F5852', line = '#DDD7CC', sage = '#4A7C59'
const yesNo = (v: boolean | null) => (v === true ? 'Yes' : v === false ? 'No' : '—')

function MonthlyBars({ months }: { months: any[] }) {
  const max = Math.max(1, ...months.map((m) => m.count)), W = 640, H = 120, bw = W / months.length
  return (
    <svg viewBox={`0 0 ${W} ${H + 18}`} width="100%" role="img" aria-label="Seizures per month">
      {months.map((m, i) => {
        const h = (m.count / max) * H
        return (
          <g key={m.month}>
            <rect x={i * bw + 3} y={H - h} width={bw - 6} height={h} fill={sage} rx={2} />
            <text x={i * bw + bw / 2} y={H - h - 3} fontSize="10" textAnchor="middle" fill={ink}>{m.count}</text>
            <text x={i * bw + bw / 2} y={H + 13} fontSize="9" textAnchor="middle" fill={muted}>{m.label}</text>
          </g>
        )
      })}
    </svg>
  )
}

export default function Report() {
  const [s, setS] = useState<any>(null)
  const [full, setFull] = useState(false)
  useEffect(() => { fetch('/api/summary', { cache: 'no-store' }).then((r) => r.json()).then(setS).catch(() => setS({ error: true })) }, [])
  if (!s) return <p style={{ padding: 24, fontFamily: 'system-ui' }}>Loading…</p>
  if (s.error) return <p style={{ padding: 24, fontFamily: 'system-ui' }}>Couldn’t load the data.</p>

  const cutoff = new Date(new Date(s.today + 'T12:00:00').getTime() - 90 * 86400000).toISOString().slice(0, 10)
  const log = full ? s.records : s.records.filter((r: any) => r.date >= cutoff)
  const months = s.duration_monthly
  const keepFindings = s.findings.filter((f: any) => !/^Time of day|^Food$/.test(f.title))
  const notes = s.findings.filter((f: any) => /^Time of day|^Food$/.test(f.title))
  const Row = ({ k, v }: any) => <tr><td className="k">{k}</td><td className="v">{v}</td></tr>

  return (
    <>
      <Head>
        <title>{`Seizure summary – ${s.generated}`}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <style>{`
        body { background: #fff; }
        .rep { max-width: 760px; margin: 0 auto; padding: 20px 16px 40px; font-family: system-ui, -apple-system, sans-serif; color: ${ink}; font-size: 14px; line-height: 1.4; }
        .rep h1 { font-family: Georgia, serif; font-size: 26px; margin: 0; }
        .rep h2 { font-size: 15px; margin: 22px 0 8px; padding-bottom: 4px; border-bottom: 2px solid ${ink}; }
        .rep table { width: 100%; border-collapse: collapse; }
        .rep td, .rep th { padding: 5px 6px; border-bottom: 1px solid ${line}; text-align: left; vertical-align: top; }
        .rep th { font-size: 12px; color: ${muted}; font-weight: 600; }
        .rep td.k { color: ${muted}; width: 46%; } .rep td.v { font-weight: 600; }
        .rep .num { text-align: right; font-variant-numeric: tabular-nums; }
        .rep .muted { color: ${muted}; font-size: 12px; }
        .rep ul { margin: 0; padding-left: 18px; } .rep li { margin-bottom: 6px; }
        .bar { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0 4px; }
        .bar button, .bar a { font: inherit; font-size: 14px; font-weight: 600; padding: 10px 14px; border-radius: 10px; border: 1px solid ${line}; background: #F6F2E9; color: ${ink}; text-decoration: none; }
        .bar .primary { background: ${sage}; color: #fff; border-color: ${sage}; }
        .log td { font-size: 13px; }
        @media print {
          .noprint { display: none !important; }
          .rep { padding: 0; font-size: 11.5px; max-width: none; }
          .rep h1 { font-size: 20px; } .rep h2 { font-size: 13px; margin-top: 14px; }
          .rep td, .rep th { padding: 3px 4px; }
          .log td { font-size: 10.5px; }
          tr, li { break-inside: avoid; }
          @page { margin: 14mm; }
        }
      `}</style>
      <div className="rep">
        <div className="noprint bar">
          <button className="primary" onClick={() => window.print()}>Print / Save as PDF</button>
          <button onClick={() => setFull(!full)}>{full ? 'Log: last 90 days only' : 'Include the full log'}</button>
          <a href="/dashboard">← Dashboard</a>
        </div>

        <h1>Seizure summary</h1>
        <p className="muted" style={{ margin: '4px 0 0' }}>Self-reported log, {s.first} – {s.last?.day ?? '—'} · generated {s.generated}</p>

        <h2>Overview</h2>
        <table><tbody>
          <Row k="Seizures logged" v={`${s.total} since ${s.first}`} />
          <Row k="Last 30 days / last 90 days" v={`${s.last30.count} / ${s.last90}`} />
          <Row k="Typical month (median of last 6)" v={s.month.typical ?? '—'} />
          <Row k="Most recent" v={s.last ? `${s.last.day}, ${s.last.time} (${s.last.duration})` : '—'} />
          <Row k="Seizure-free now / longest stretch" v={s.streak ? `${s.streak.current_days} days / ${s.streak.longest_days} days` : '—'} />
          {s.overall_duration && <Row k="Duration, median (middle half)" v={`${s.overall_duration.median} (${s.overall_duration.q1} – ${s.overall_duration.q3})`} />}
          {s.duration_trend && <Row k="Duration, last 10 vs previous 30" v={`${s.duration_trend.recent} vs ${s.duration_trend.prior}${s.duration_trend.direction !== 'same' ? ` (${s.duration_trend.direction})` : ''}`} />}
          {s.overall_duration && <Row k="Longest seizure" v={s.overall_duration.longest} />}
        </tbody></table>

        <h2>Seizures per month</h2>
        <MonthlyBars months={months} />
        <table style={{ marginTop: 6 }}>
          <thead><tr><th>Month</th><th className="num">Seizures</th><th className="num">Median length</th><th className="num">Longest</th></tr></thead>
          <tbody>
            {months.slice().reverse().map((m: any) => (
              <tr key={m.month}><td>{m.label}</td><td className="num">{m.count}</td>
                <td className="num">{m.median != null ? `${Math.floor(m.median / 60)}m ${String(m.median % 60).padStart(2, '0')}s` : '—'}</td>
                <td className="num">{m.max != null ? `${Math.floor(m.max / 60)}m ${String(Math.round(m.max % 60)).padStart(2, '0')}s` : '—'}</td></tr>
            ))}
          </tbody>
        </table>

        <h2>Patterns in the log</h2>
        <ul>{keepFindings.map((f: any) => <li key={f.title}><b>{f.title}.</b> {f.text}</li>)}</ul>

        <h2>Seizure log {full ? '(all)' : '(last 90 days)'}</h2>
        <table className="log">
          <thead><tr><th>Date</th><th>Time</th><th className="num">Length</th><th>Period</th><th>Eaten</th><th>Food</th></tr></thead>
          <tbody>
            {log.map((r: any, i: number) => (
              <tr key={i}><td>{r.day}{r.date.slice(0, 4) !== s.today.slice(0, 4) ? ` ${r.date.slice(0, 4)}` : ''}{r.possible_duplicate ? ' *' : ''}</td><td>{r.time}</td><td className="num">{r.duration}</td><td>{yesNo(r.period)}</td><td>{yesNo(r.eaten)}</td><td>{r.food}</td></tr>
            ))}
          </tbody>
        </table>
        {log.some((r: any) => r.possible_duplicate) && <p className="muted">* Logged less than 2 minutes after the previous entry; possibly a duplicate.</p>}

        <h2>About this data</h2>
        <ul className="muted">
          <li>Seizures were logged by the patient from her phone; times are when each was logged, so seizures during sleep may be missing.</li>
          <li>“Period” and “Eaten” are recorded at the time of each seizure only (no separate cycle or meal log yet).</li>
          {notes.map((f: any) => <li key={f.title}>{f.title}: {f.text}</li>)}
        </ul>
      </div>
    </>
  )
}
