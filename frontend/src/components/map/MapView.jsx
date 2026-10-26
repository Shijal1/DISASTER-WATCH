import { useEffect } from 'react'
import { MapContainer, TileLayer, LayersControl, useMap } from 'react-leaflet'
import IncidentMarkers from './IncidentMarkers.jsx'
import RiskZones from './RiskZones.jsx'
import DamageZones from './DamageZones.jsx'
import AssetMarkers from './AssetMarkers.jsx'
import SatelliteOverlay from './SatelliteOverlay.jsx'
import { useUIStore } from '../../store/uiStore.js'
import { useIncidentStore } from '../../store/incidentStore.js'

const CENTER = [20, 0]

function MapFocusController() {
  const map = useMap()
  const incidents = useIncidentStore(s => s.incidents)
  const selectedId = useIncidentStore(s => s.selectedId)

  useEffect(() => {
    if (!selectedId) return
    const inc = incidents.find(i => i.incident_id === selectedId)
    if (!inc) return
    map.flyTo([inc.latitude, inc.longitude], Math.max(map.getZoom(), 8), { duration: 1.2 })
  }, [selectedId, incidents, map])

  return null
}

export default function MapView() {
  const layers = useUIStore(s => s.layers)
  const satelliteLayer = useUIStore(s => s.satelliteLayer)

  return (
    <MapContainer center={CENTER} zoom={3} className="h-full w-full">
      <LayersControl position="topright">
        <LayersControl.BaseLayer checked name="Standard (OSM)">
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                     attribution="&copy; OpenStreetMap" />
        </LayersControl.BaseLayer>
        <LayersControl.BaseLayer name="Satellite (ArcGIS)">
          <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                     attribution="Tiles &copy; Esri" />
        </LayersControl.BaseLayer>
        <LayersControl.BaseLayer name="Terrain (OpenTopoMap)">
          <TileLayer url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
                     attribution="&copy; OpenTopoMap" />
        </LayersControl.BaseLayer>
      </LayersControl>

      <MapFocusController />
      <SatelliteOverlay layer={satelliteLayer} opacity={0.7} />
      {layers.incidents && <IncidentMarkers />}
      {layers.riskZones && <RiskZones />}
      <DamageZones />
      {layers.assets && <AssetMarkers />}
    </MapContainer>
  )
}