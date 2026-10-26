
import { Polygon } from 'react-leaflet'
import { useIncidentStore } from '../../store/incidentStore.js'

const COLORS = { CORE: '#dc2626', HIGH: '#ea580c', MEDIUM: '#eab308', LOW: '#16a34a' }

export default function RiskZones() {
  const predictions = useIncidentStore(s => s.predictions)
  const selectedId = useIncidentStore(s => s.selectedId)
  if (!selectedId) return null
  const zones = predictions[selectedId] || []

  return zones.map(z => {
    if (!z.geometry) return null
    let geo; try { geo = JSON.parse(z.geometry) } catch { return null }
    const positions = geo.coordinates[0].map(([lng, lat]) => [lat, lng])
    return (
      <Polygon key={z.prediction_id} positions={positions}
               pathOptions={{ color: COLORS[z.risk_level] || '#94a3b8', fillOpacity: 0.15, weight: 2 }} />
    )
  })
}
