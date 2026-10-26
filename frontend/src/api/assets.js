
import { client } from './client.js'

export const listAssets = () => client.get('/assets').then(r => r.data)
export const createAsset = (payload) => client.post('/assets', payload).then(r => r.data)
export const assignAsset = (assetId, incidentId) => client.post(`/assets/${assetId}/assign?incident_id=${incidentId}`).then(r => r.data)
export const autoAssign = (incidentId) => client.post(`/predictions/${incidentId}/auto-assign`).then(r => r.data)
