import { Polygon, Popup } from 'react-leaflet'
import { useUIStore } from '../../store/uiStore.js'

export default function DamageZones() {
  const zones = useUIStore(s => s.damageZones)

  return zones.map(z => {
    if (!z.geometry) return null
    let geo
    try { geo = JSON.parse(z.geometry) } catch { return null }
    const positions = geo.coordinates[0].map(([lng, lat]) => [lat, lng])

    return (
      <Polygon
        key={`damage-${z.prediction_id}`}
        positions={positions}
        pathOptions={{
          color: '#06b6d4',
          weight: 3,
          dashArray: '6 4',
          fillColor: '#06b6d4',
          fillOpacity: 0.25,
        }}>
        <Popup>
          <div style={{fontSize:'12px'}}>
            <div><b>AI-DETECTED FLOOD EXTENT</b></div>
            <div>Source: Sentinel-2 NDWI</div>
            <div>{z.recommended_action}</div>
          </div>
        </Popup>
      </Polygon>
    )
  })
}