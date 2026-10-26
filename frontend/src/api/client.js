
import axios from 'axios'

export const client = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export const WS_URL = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/events`
