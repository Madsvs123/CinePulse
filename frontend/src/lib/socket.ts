import { getAccessToken } from './api'
import type { NotificationItem } from './types'

export function connectNotifications(onMessage: (item: NotificationItem) => void) {
  const token = getAccessToken()
  if (!token) return () => undefined
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/notifications/?token=${token}`)
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'notification') onMessage(data as NotificationItem)
  }
  return () => socket.close()
}
