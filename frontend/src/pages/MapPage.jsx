import { useEffect, useState, useCallback } from 'react'
import MapView from '../components/map/MapView.jsx'
import IncidentPanel from '../components/panels/IncidentPanel.jsx'
import AlertPanel from '../components/panels/AlertPanel.jsx'
import SatellitePanel from '../components/panels/SatellitePanel.jsx'
import LayerControl from '../components/map/LayerControl.jsx'
import { useIncidentStore } from '../store/incidentStore.js'
import { useAssetStore } from '../store/assetStore.js'
import { useWebSocket } from '../hooks/useWebSocket.js'
export default function MapPage() {
  const refreshIncidents = useIncidentStore(s => s.refresh)
  const refreshAssets = useAssetStore(s => s.refresh)
  const [lastEvent, setLastEvent] = useState(null)
  useEffect(() => { refreshIncidents(); refreshAssets() }, [])
  const onEvent = useCallback((msg) => {
    setLastEvent(msg)
    if (msg.type === 'sos_created' || msg.type === 'feed_incident') {
      refreshIncidents()
      refreshAssets()
    }
    if (msg.type === 'predictions_generated') refreshIncidents()
  }, [])
  useWebSocket(onEvent)
  return (
    <div className="h-full flex">
      <div className="flex-1 relative">
        <MapView />
        <LayerControl />
      </div>
      <aside className="w-96 border-l border-slate-800 bg-slate-900 overflow-y-auto">
        <IncidentPanel />
        <SatellitePanel />
        <AlertPanel lastEvent={lastEvent} />
      </aside>
    </div>
  )
}