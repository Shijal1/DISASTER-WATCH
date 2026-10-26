import { client } from './client.js'
export const listIncidents = () => client.get('/incidents').then(r => r.data)
export const getIncident = (id) => client.get(`/incidents/${id}`).then(r => r.data)
export const createIncident = (payload) => client.post('/incidents', payload).then(r => r.data)
export const updateIncident = (id, payload) => client.patch(`/incidents/${id}`, payload).then(r => r.data)
export const generatePredictions = (id) =>
  client.post(`/predictions/generate?incident_id=${id}`).then(r => r.data)
export const getPredictions = (id) =>
  client.get(`/predictions/${id}`).then(r => r.data)
export const startResponse = (id, operator = 'operator') =>
  client.post(`/incidents/${id}/start-response?operator=${operator}`).then(r => r.data)
export const resolveIncident = (id) =>
  client.post(`/incidents/${id}/resolve`).then(r => r.data)