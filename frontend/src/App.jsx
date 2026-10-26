
import { Routes, Route, NavLink } from 'react-router-dom'
import MapPage from './pages/MapPage.jsx'
import SOSPage from './pages/SOSPage.jsx'
import AdminPage from './pages/AdminPage.jsx'
import Header from './components/common/Header.jsx'

export default function App() {
  return (
    <div className="h-full flex flex-col bg-slate-950 text-slate-100">
      <Header />
      <nav className="flex gap-1 px-4 py-2 bg-slate-900 border-b border-slate-800 text-sm">
        <NavLink to="/" end className={({isActive}) =>
          `px-3 py-1 rounded ${isActive ? 'bg-slate-700' : 'hover:bg-slate-800'}`}>Map</NavLink>
        <NavLink to="/sos" className={({isActive}) =>
          `px-3 py-1 rounded ${isActive ? 'bg-slate-700' : 'hover:bg-slate-800'}`}>SOS</NavLink>
        <NavLink to="/admin" className={({isActive}) =>
          `px-3 py-1 rounded ${isActive ? 'bg-slate-700' : 'hover:bg-slate-800'}`}>Admin</NavLink>
      </nav>
      <main className="flex-1 overflow-hidden">
        <Routes>
          <Route path="/" element={<MapPage />} />
          <Route path="/sos" element={<SOSPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </main>
    </div>
  )
}
