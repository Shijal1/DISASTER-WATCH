import { client } from './client.js'
export const listAlerts = (status = 'active') =>
  client.get(`/alerts?status=${status}`).then(r => r.data)
export const acknowledgeAlert = (alertId, acknowledgedBy = 'operator') =>
  client.post(`/alerts/${alertId}/acknowledge`, { acknowledged_by: acknowledgedBy }).then(r => r.data)
export const resolveAlert = (alertId) =>
  client.post(`/alerts/${alertId}/resolve`).then(r => r.data)