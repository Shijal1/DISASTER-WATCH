
import { client } from './client.js'

export const submitSOS = (payload) => client.post('/sos', payload).then(r => r.data)
