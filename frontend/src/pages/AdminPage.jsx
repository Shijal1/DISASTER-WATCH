
import { useEffect, useState } from 'react'
import { listAssets, createAsset } from '../api/assets.js'
import { listCamps, createCamp } from '../api/camps.js'

export default function AdminPage() {
  const [assets, setAssets] = useState([])
  const [camps, setCamps] = useState([])

  const refresh = async () => {
    setAssets(await listAssets())
    setCamps(await listCamps())
  }
  useEffect(() => { refresh() }, [])

  const addAsset = async () => {
    await createAsset({
      type: 'ambulance',
      label: `Ambulance ${assets.length + 1}`,
      latitude: 28.61 + (Math.random() - 0.5) * 0.5,
      longitude: 77.20 + (Math.random() - 0.5) * 0.5,
    })
    refresh()
  }

  const addCamp = async () => {
    await createCamp({
      name: `Relief Camp ${camps.length + 1}`,
      latitude: 28.61 + (Math.random() - 0.5) * 0.5,
      longitude: 77.20 + (Math.random() - 0.5) * 0.5,
      capacity: 500,
      current_population: 100,
    })
    refresh()
  }

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <h1 className="text-xl font-semibold">Administrator Dashboard</h1>

      <section>
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-semibold">Assets ({assets.length})</h2>
          <button onClick={addAsset} className="text-xs px-3 py-1 rounded bg-blue-600 hover:bg-blue-700">+ Add ambulance</button>
        </div>
        <ul className="text-xs space-y-1">
          {assets.map(a => (
            <li key={a.asset_id} className="bg-slate-900 rounded px-3 py-2 flex justify-between">
              <span>{a.type} — {a.label || `#${a.asset_id}`}</span>
              <span className={a.availability ? 'text-green-400' : 'text-orange-400'}>{a.status}</span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-semibold">Relief Camps ({camps.length})</h2>
          <button onClick={addCamp} className="text-xs px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-700">+ Add camp</button>
        </div>
        <ul className="text-xs space-y-1">
          {camps.map(c => (
            <li key={c.camp_id} className="bg-slate-900 rounded px-3 py-2 flex justify-between">
              <span>{c.name}</span>
              <span>{c.current_population}/{c.capacity}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
