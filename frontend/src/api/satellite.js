import { client } from './client.js'

export const getSatelliteStatus = () => client.get('/satellite/status').then(r => r.data)
export const detectFloodDamage = (incidentId) =>
  client.post(`/satellite/detect-flood/${incidentId}`).then(r => r.data)