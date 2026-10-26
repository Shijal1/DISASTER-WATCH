
import { client } from './client.js'

export const listCamps = () => client.get('/camps').then(r => r.data)
export const createCamp = (payload) => client.post('/camps', payload).then(r => r.data)
