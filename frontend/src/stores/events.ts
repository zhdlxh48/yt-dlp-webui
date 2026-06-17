import { writable } from 'svelte/store'
import type { AppEvent } from '@/types'

export const connected = writable(false)
export const events = writable<AppEvent[]>([])
export const logs = writable<string[]>([])

export function connectEvents(): void {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const socket = new WebSocket(`${protocol}//${location.host}/ws/events`)

  socket.addEventListener('open', () => connected.set(true))
  socket.addEventListener('close', () => {
    connected.set(false)
    window.setTimeout(connectEvents, 1500)
  })
  socket.addEventListener('message', (message) => {
    const event = JSON.parse(message.data) as AppEvent
    events.update((items) => [event, ...items].slice(0, 200))
    if (event.type === 'job.log' || event.type === 'system.log') {
      const line = String(event.payload.line ?? '')
      logs.update((items) => [line, ...items].slice(0, 500))
    }
  })
}
