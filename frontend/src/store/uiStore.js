import { create } from 'zustand'

export const useUIStore = create((set) => ({
  layers: { incidents: true, riskZones: true, assets: true },
  satelliteLayer: null,
  damageZones: [],
  toggleLayer(key) {
    set((s) => ({ layers: { ...s.layers, [key]: !s.layers[key] } }))
  },
  setSatelliteLayer(layer) {
    set({ satelliteLayer: layer })
  },
  addDamageZone(pred) {
    set((s) => ({ damageZones: [...s.damageZones, pred] }))
  },
  clearDamageZones() {
    set({ damageZones: [] })
  },
}))