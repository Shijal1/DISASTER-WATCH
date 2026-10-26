
import { useUIStore } from '../../store/uiStore.js'

const LABELS = { incidents: 'Incidents', riskZones: 'Risk zones', assets: 'Assets' }

export default function LayerControl() {
  const { layers, toggleLayer } = useUIStore()
  return (
    <div className="absolute bottom-4 left-4 z-[1000] bg-slate-900/90 backdrop-blur rounded-lg p-3 text-xs space-y-1 shadow-lg border border-slate-700">
      <div className="font-semibold mb-1 text-slate-300">Layers</div>
      {Object.entries(layers).map(([key, on]) => (
        <label key={key} className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={on} onChange={() => toggleLayer(key)} className="accent-red-500" />
          <span>{LABELS[key]}</span>
        </label>
      ))}
    </div>
  )
}
