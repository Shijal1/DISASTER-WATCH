
import { create } from 'zustand'
import { listIncidents, getPredictions } from '../api/incidents.js'

export const useIncidentStore = create((set) => ({
  incidents: [],
  predictions: {},
  selectedId: null,

  async refresh() {
    const incidents = await listIncidents()
    set({ incidents })
  },

  select(id) {
    set({ selectedId: id })
  },

  async loadPredictions(incidentId) {
    const zones = await getPredictions(incidentId)
    set((s) => ({ predictions: { ...s.predictions, [incidentId]: zones } }))
  },
}))
