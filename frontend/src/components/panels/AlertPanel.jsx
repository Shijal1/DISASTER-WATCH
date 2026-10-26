import { useEffect, useState } from 'react'
import { listAlerts, acknowledgeAlert, resolveAlert } from '../../api/alerts.js'
const SEVERITY_STYLE = {
  ESCALATED_CRITICAL: 'border-red-700 bg-red-950 text-red-100 animate-pulse',
  CRITICAL:           'border-red-500 bg-red-950/60 text-red-50',
  WARNING:            'border-yellow-500 bg-yellow-950/30 text-yellow-50',
  INFO:               'border-slate-500 bg-slate-800 text-slate-200',
}
export default function AlertPanel({ lastEvent }) {
  const [alerts, setAlerts] = useState([])
  const [busy, setBusy] = useState(null)
  const refresh = async () => setAlerts(await listAlerts())
  useEffect(() => { refresh() }, [])
  useEffect(() => { if (lastEvent) refresh() }, [lastEvent])
  const onAck = async (id, e) => {
    e.stopPropagation()
    setBusy(id)
    try {
      await acknowledgeAlert(id, 'operator_priya')
      await refresh()
    } finally { setBusy(null) }
  }
  const onResolve = async (id, e) => {
    e.stopPropagation()
    setBusy(id)
    try {
      await resolveAlert(id)
      await refresh()
    } finally { setBusy(null) }
  }
  return (
    <div className="p-3">
      <h2 className="text-sm font-semibold mb-2">
        Active Alerts <span className="text-slate-500">({alerts.length})</span>
      </h2>
      <ul className="space-y-2 text-xs">
        {alerts.map(a => {
          const style = SEVERITY_STYLE[a.severity] || SEVERITY_STYLE.INFO
          const isEscalated = (a.escalation_level ?? 0) > 0
          return (
            <li key={a.alert_id}
                className={`rounded p-2 border-l-4 ${style}`}>
              <div className="flex items-center justify-between">
                <span className="font-semibold uppercase">{a.type}</span>
                <span className="text-[10px] opacity-70">#{a.alert_id}</span>
              </div>
              <div className="mt-1">{a.message}</div>
              <div className="flex items-center justify-between mt-1 text-[10px] opacity-70">
                <span>{new Date(a.created_at).toLocaleTimeString()}</span>
                {isEscalated && (
                  <span className="font-bold">
                    L{a.escalation_level} escalated
                  </span>
                )}
              </div>
              {a.status === 'active' && (
                <div className="flex gap-2 mt-2">
                  <button
                    disabled={busy === a.alert_id}
                    onClick={(e) => onAck(a.alert_id, e)}
                    className="px-2 py-0.5 rounded bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white">
                    Acknowledge
                  </button>
                  <button
                    disabled={busy === a.alert_id}
                    onClick={(e) => onResolve(a.alert_id, e)}
                    className="px-2 py-0.5 rounded bg-slate-700 hover:bg-slate-600 disabled:opacity-50">
                    Resolve
                  </button>
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}