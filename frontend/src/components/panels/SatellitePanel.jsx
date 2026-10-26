import { useEffect, useState } from 'react'
import { useUIStore } from '../../store/uiStore.js'
export default function SatellitePanel() {
  const [status, setStatus] = useState(null)
  const satelliteLayer = useUIStore(s => s.satelliteLayer)
  const setSatelliteLayer = useUIStore(s => s.setSatelliteLayer)
  useEffect(() => {
    fetch('/api/satellite/status')
      .then(r => r.json())
      .then(setStatus)
      .catch(() => setStatus({ credentials_configured: false }))
  }, [])
  const modes = [
    { id: 'TRUE_COLOR', label: 'True colour' },
    { id: 'NDWI', label: 'NDWI (water)' },
    { id: 'NBR', label: 'NBR (burn)' },
  ]
  return (
    <div className="p-3 border-b border-slate-800 text-xs">
      <h2 className="text-sm font-semibold mb-2">Satellite (Sentinel-2)</h2>
      {!status?.credentials_configured ? (
        <div className="text-slate-500">Credentials not configured.</div>
      ) : (
        <>
          <div className="text-slate-400 mb-2">Overlay mode:</div>
          <div className="space-y-1">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="radio" name="sat" checked={satelliteLayer === null}
                     onChange={() => setSatelliteLayer(null)} />
              <span>Off</span>
            </label>
            {modes.map(m => (
              <label key={m.id} className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="sat" checked={satelliteLayer === m.id}
                       onChange={() => setSatelliteLayer(m.id)} />
                <span>{m.label}</span>
              </label>
            ))}
          </div>
        </>
      )}
    </div>
  )
}