
import { Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import { useAssetStore } from '../../store/assetStore.js'

const icon = L.divIcon({
  className: '',
  html: `<div style="background:#3b82f6;width:12px;height:12px;border-radius:2px;border:2px solid white"></div>`,
  iconSize: [12, 12], iconAnchor: [6, 6],
})

export default function AssetMarkers() {
  const assets = useAssetStore(s => s.assets)
  return assets.map(a => (
    <Marker key={a.asset_id} position={[a.latitude, a.longitude]} icon={icon}>
      <Popup>
        <div style={{fontSize:'12px'}}>
          <div><b>{a.type}</b> — {a.label || `#${a.asset_id}`}</div>
          <div>Status: {a.status}</div>
          <div>Available: {a.availability ? 'yes' : 'no'}</div>
        </div>
      </Popup>
    </Marker>
  ))
}
