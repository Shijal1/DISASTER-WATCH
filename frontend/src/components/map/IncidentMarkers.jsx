import { Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import { useIncidentStore } from '../../store/incidentStore.js'
const COLORS = { CRITICAL: '#dc2626', HIGH: '#ea580c', MODERATE: '#eab308', LOW: '#16a34a', ESCALATED_CRITICAL: '#7f1d1d' }
function icon(inc) {
  // Emerging cluster: pulsing red
  if (inc.source === 'correlation') {
    return L.divIcon({
      className: '',
      html: `<div style="background:#dc2626;width:20px;height:20px;border-radius:50%;border:3px solid #fca5a5;box-shadow:0 0 12px #dc2626;animation:pulse 1.5s infinite"></div>
             <style>@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}</style>`,
      iconSize: [20, 20], iconAnchor: [10, 10],
    })
  }
  // Resolved: greyed out
  if (inc.status === 'resolved') {
    return L.divIcon({
      className: '',
      html: `<div style="background:#64748b;width:12px;height:12px;border-radius:50%;border:2px solid #cbd5e1;opacity:0.5"></div>`,
      iconSize: [12, 12], iconAnchor: [6, 6],
    })
  }
  // Responding: blue ring around the severity colour
  if (inc.status === 'responding') {
    const c = COLORS[inc.severity] || '#94a3b8'
    return L.divIcon({
      className: '',
      html: `<div style="background:${c};width:16px;height:16px;border-radius:50%;border:3px solid #3b82f6;box-shadow:0 0 8px #3b82f6"></div>`,
      iconSize: [16, 16], iconAnchor: [8, 8],
    })
  }
  // Default severity-coloured dot
  const c = COLORS[inc.severity] || '#94a3b8'
  return L.divIcon({
    className: '',
    html: `<div style="background:${c};width:14px;height:14px;border-radius:50%;border:2px solid white;box-shadow:0 0 6px rgba(0,0,0,0.5)"></div>`,
    iconSize: [14, 14], iconAnchor: [7, 7],
  })
}
export default function IncidentMarkers() {
  const incidents = useIncidentStore(s => s.incidents)
  const select = useIncidentStore(s => s.select)
  const load = useIncidentStore(s => s.loadPredictions)
  return incidents.map(inc => (
    <Marker key={inc.incident_id}
            position={[inc.latitude, inc.longitude]}
            icon={icon(inc)}
            eventHandlers={{ click: () => { select(inc.incident_id); load(inc.incident_id) } }}>
      <Popup>
        <div style={{fontSize:'12px'}}>
          <div>
            <b>{inc.type.toUpperCase()}</b>
            {inc.source === 'correlation' && <span style={{color:'#dc2626'}}> [EMERGING]</span>}
          </div>
          <div>Severity: <b>{inc.severity}</b></div>
          <div>Status: <b>{inc.status}</b></div>
          {inc.acknowledged_by && <div>Acknowledged by: {inc.acknowledged_by}</div>}
          {inc.responding_at && <div>Responding since: {new Date(inc.responding_at).toLocaleTimeString()}</div>}
          {inc.resolved_at && <div>Resolved: {new Date(inc.resolved_at).toLocaleTimeString()}</div>}
          <div>Source: {inc.source}</div>
          {inc.description && <div>{inc.description}</div>}
          <div style={{color:'#64748b'}}>{new Date(inc.created_at).toLocaleString()}</div>
        </div>
      </Popup>
    </Marker>
  ))
}