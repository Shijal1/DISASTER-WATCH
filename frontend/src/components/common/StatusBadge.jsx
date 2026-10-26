
import { useEffect, useState } from 'react'
import { client } from '../../api/client.js'

export default function StatusBadge() {
  const [ok, setOk] = useState(false)

  useEffect(() => {
    const check = async () => {
      try { await client.get('/health'); setOk(true) } catch { setOk(false) }
    }
    check()
    const id = setInterval(check, 10000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className={`w-2 h-2 rounded-full ${ok ? 'bg-green-500' : 'bg-red-500'}`} />
      <span className="text-slate-400">{ok ? 'Backend online' : 'Backend offline'}</span>
    </div>
  )
}
