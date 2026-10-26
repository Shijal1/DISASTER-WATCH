
import { Radio } from 'lucide-react'
import StatusBadge from './StatusBadge.jsx'

export default function Header() {
  return (
    <header className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800">
      <div className="flex items-center gap-2">
        <Radio className="w-5 h-5 text-red-500" />
        <h1 className="font-semibold tracking-wide">DISASTERWATCH</h1>
        <span className="text-xs text-slate-400 ml-2">AI-Assisted Disaster Intelligence Platform</span>
      </div>
      <StatusBadge />
    </header>
  )
}
