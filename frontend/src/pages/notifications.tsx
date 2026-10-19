import { useEffect, useState } from 'react'
import { Button, Panel } from '../components/ui'
import { api } from '../lib/api'
import type { NotificationItem } from '../lib/types'

export function NotificationsPage() {
  const [items, setItems] = useState<NotificationItem[]>([])

  const load = () => {
    api<{ results: NotificationItem[] }>('/api/notifications/').then((data) => setItems(data.results))
  }

  useEffect(load, [])

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 className="cp-display">Notifications</h1>
        <Button
          kind="ghost"
          onClick={async () => {
            await api('/api/notifications/read/', { method: 'POST' })
            load()
          }}
        >
          Mark all read
        </Button>
      </div>
      {items.map((item) => (
        <Panel key={item.id}>
          <p className="cp-kicker">{item.kind.replaceAll('_', ' ')}</p>
          <h3>{item.title}</h3>
          <p className="cp-muted">{item.body}</p>
        </Panel>
      ))}
    </div>
  )
}
