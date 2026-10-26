
import { useState } from 'react'
import { submitSOS } from '../../api/sos.js'

const CATEGORIES = ['flood', 'earthquake', 'fire', 'medical', 'trapped', 'other']

export default function SOSForm() {
  const [form, setForm] = useState({
    category: 'flood', affected_people: 1, description: '',
    latitude: 28.61, longitude: 77.20,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const onSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError(null); setResult(null)
    try {
      const res = await submitSOS({
        ...form,
        affected_people: Number(form.affected_people),
        latitude: Number(form.latitude),
        longitude: Number(form.longitude),
      })
      setResult(res)
    } catch (err) {
      setError(err?.response?.data?.detail || err.message)
    } finally { setLoading(false) }
  }

  const onGPS = () => {
    navigator.geolocation?.getCurrentPosition((p) => {
      setForm(f => ({ ...f, latitude: p.coords.latitude, longitude: p.coords.longitude }))
    })
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4 bg-slate-900 rounded-lg p-4 border border-slate-800">
      <div>
        <label className="block text-xs text-slate-400 mb-1">Emergency category</label>
        <select value={form.category} onChange={(e) => setForm(f => ({ ...f, category: e.target.value }))}
                className="w-full bg-slate-800 rounded px-3 py-2 text-sm">
          {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <div>
        <label className="block text-xs text-slate-400 mb-1">People affected</label>
        <input type="number" min="0" value={form.affected_people}
               onChange={(e) => setForm(f => ({ ...f, affected_people: e.target.value }))}
               className="w-full bg-slate-800 rounded px-3 py-2 text-sm" />
      </div>

      <div>
        <label className="block text-xs text-slate-400 mb-1">Describe the emergency</label>
        <textarea rows="4" required minLength={3} value={form.description}
                  onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
                  placeholder="e.g. People trapped on the roof, water rising fast, one person bleeding"
                  className="w-full bg-slate-800 rounded px-3 py-2 text-sm" />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Latitude</label>
          <input type="number" step="any" value={form.latitude}
                 onChange={(e) => setForm(f => ({ ...f, latitude: e.target.value }))}
                 className="w-full bg-slate-800 rounded px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Longitude</label>
          <input type="number" step="any" value={form.longitude}
                 onChange={(e) => setForm(f => ({ ...f, longitude: e.target.value }))}
                 className="w-full bg-slate-800 rounded px-3 py-2 text-sm" />
        </div>
      </div>

      <button type="button" onClick={onGPS} className="text-xs text-blue-400 hover:text-blue-300">
        Use my current location
      </button>

      <button type="submit" disabled={loading}
              className="w-full bg-red-600 hover:bg-red-700 disabled:opacity-50 rounded py-2 font-semibold">
        {loading ? 'Sending…' : 'Send SOS'}
      </button>

      {error && <div className="text-sm text-red-400 bg-red-950/40 rounded p-3">{String(error)}</div>}

      {result && (
        <div className="text-sm bg-slate-800 rounded p-3 space-y-1">
          <div>Incident <b>#{result.incident_id}</b> created.</div>
          <div>Triage severity: <b className="text-orange-400">{result.severity}</b></div>
          {result.matched_evidence?.length > 0 && <div>Matched: {result.matched_evidence.join(', ')}</div>}
          {result.candidate_location && <div>Location phrase: {result.candidate_location}</div>}
        </div>
      )}
    </form>
  )
}
