import { useState } from 'react'
import { useIncidentStore } from '../../store/incidentStore.js'
import { useAssetStore } from '../../store/assetStore.js'
import { useUIStore } from '../../store/uiStore.js'
import { generatePredictions, startResponse, resolveIncident } from '../../api/incidents.js'
import { autoAssign } from '../../api/assets.js'
import { detectFloodDamage } from '../../api/satellite.js'

const SEV = {
  CRITICAL: 'bg-red-600',
  HIGH: 'bg-orange-600',
  MODERATE: 'bg-yellow-600',
  LOW: 'bg-green-600',
  ESCALATED_CRITICAL: 'bg-red-800',
}

const STATUS_STYLE = {
  active: 'bg-slate-600',
  responding: 'bg-blue-600',
  resolved: 'bg-emerald-700',
}

export default function IncidentPanel() {
  const incidents = useIncidentStore(s => s.incidents)
  const select = useIncidentStore(s => s.select)
  const loadPredictions = useIncidentStore(s => s.loadPredictions)
  const refreshIncidents = useIncidentStore(s => s.refresh)
  const refreshAssets = useAssetStore(s => s.refresh)
  const addDamageZone = useUIStore(s => s.addDamageZone)
  const [busy, setBusy] = useState(null)

  const wrap = async (id, fn) => {
    setBusy(id)
    try { await fn() } finally { setBusy(null); refreshIncidents(); refreshAssets() }
  }

  const onGenerate = (id, e) =>
    wrap(id, async () => {
      e.stopPropagation()
      await generatePredictions(id)
      await loadPredictions(id)
      select(id)
    })

  const onAssign = (id, e) =>
    wrap(id, async () => {
      e.stopPropagation()
      const res = await autoAssign(id)
      alert(res.assigned
        ? `Assigned ${res.asset_type} (#${res.asset_id}) - ${res.distance_km} km away`
        : `No asset assigned: ${res.reason}`)
    })

  const onAnalyse = (id, e) =>
    wrap(id, async () => {
      e.stopPropagation()
      try {
        const pred = await detectFloodDamage(id)
        addDamageZone(pred)
        alert(`AI flood detection complete: ${pred.recommended_action}`)
      } catch (err) {
        alert(err?.response?.data?.detail || 'Analysis failed')
      }
    })

  const onStart = (id, e) =>
    wrap(id, async () => {
      e.stopPropagation()
      await startResponse(id, 'operator_priya')
    })

  const onResolve = (id, e) =>
    wrap(id, async () => {
      e.stopPropagation()
      if (!confirm('Mark this incident as resolved?')) return
      await resolveIncident(id)
    })

  return (
    <div className="p-3 border-b border-slate-800">
      <h2 className="text-sm font-semibold mb-2">
        Active Incidents <span className="text-slate-500">({incidents.length})</span>
      </h2>
      <ul className="space-y-2">
        {incidents.map(inc => {
          const isResolved = inc.status === 'resolved'
          return (
            <li key={inc.incident_id}
                className={`bg-slate-800 rounded p-2 text-xs cursor-pointer hover:bg-slate-700 ${isResolved ? 'opacity-50' : ''}`}
                onClick={() => { select(inc.incident_id); loadPredictions(inc.incident_id) }}>
              <div className="flex items-center justify-between">
                <span className="font-semibold uppercase">
                  {inc.type} {inc.source === 'correlation' && <span className="text-red-400">[EMERGING]</span>}
                </span>
                <span className={`px-2 py-0.5 rounded text-white ${SEV[inc.severity] || 'bg-slate-600'}`}>
                  {inc.severity}
                </span>
              </div>

              <div className="mt-1 flex items-center gap-2 text-[10px] text-slate-400">
                <span className={`px-1.5 py-0.5 rounded text-white ${STATUS_STYLE[inc.status] || 'bg-slate-600'}`}>
                  {inc.status}
                </span>
                {inc.acknowledged_by && <span>ack: {inc.acknowledged_by}</span>}
              </div>

              <div className="text-slate-400 mt-1">{inc.description || '(no description)'}</div>
              <div className="text-slate-500 mt-1">source: {inc.source}</div>

              {!isResolved && (
                <div className="flex flex-wrap gap-2 mt-2">
                  <button disabled={busy === inc.incident_id}
                          onClick={(e) => onGenerate(inc.incident_id, e)}
                          className="px-2 py-0.5 rounded bg-blue-600 hover:bg-blue-700 disabled:opacity-50">
                    Zones
                  </button>
                  <button disabled={busy === inc.incident_id}
                          onClick={(e) => onAssign(inc.incident_id, e)}
                          className="px-2 py-0.5 rounded bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50">
                    Auto-assign
                  </button>
                  {inc.type === 'flood' && (
                    <button disabled={busy === inc.incident_id}
                            onClick={(e) => onAnalyse(inc.incident_id, e)}
                            className="px-2 py-0.5 rounded bg-purple-600 hover:bg-purple-700 disabled:opacity-50">
                      Analyse damage
                    </button>
                  )}
                  {inc.status !== 'responding' && (
                    <button disabled={busy === inc.incident_id}
                            onClick={(e) => onStart(inc.incident_id, e)}
                            className="px-2 py-0.5 rounded bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50">
                      Start response
                    </button>
                  )}
                  <button disabled={busy === inc.incident_id}
                          onClick={(e) => onResolve(inc.incident_id, e)}
                          className="px-2 py-0.5 rounded bg-slate-600 hover:bg-slate-500 disabled:opacity-50">
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