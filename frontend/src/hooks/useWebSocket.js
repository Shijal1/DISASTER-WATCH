
import { useEffect } from 'react'
import { WS_URL } from '../api/client.js'

export function useWebSocket(onEvent) {
  useEffect(() => {
    let ws
    let closed = false

    const connect = () => {
      ws = new WebSocket(WS_URL)
      ws.onmessage = (e) => {
        try { onEvent?.(JSON.parse(e.data)) } catch (err) { console.warn(err) }
      }
      ws.onclose = () => { if (!closed) setTimeout(connect, 2000) }
    }

    connect()
    return () => { closed = true; ws?.close() }
  }, [onEvent])
}
