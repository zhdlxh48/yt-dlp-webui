import { writable } from 'svelte/store'
import type { AppEvent, JobProgress, LogEntry } from '@/types'

const MAX_EVENTS = 200
const MAX_LOGS = 300

export const connected = writable(false)
export const events = writable<AppEvent[]>([])
export const logs = writable<LogEntry[]>([])
export const jobProgress = writable<JobProgress[]>([])

export function clearLogs(): void {
  logs.set([])
}

let logSequence = 0

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
    rememberEvent(event)
    routeEvent(event)
  })
}

function rememberEvent(event: AppEvent): void {
  events.update((items) => [event, ...items].slice(0, MAX_EVENTS))
}

function routeEvent(event: AppEvent): void {
  if (event.type === 'job.progress_line') {
    upsertProgress(event)
    return
  }

  if (event.type === 'job.finished' || event.type === 'job.error') {
    removeProgress(String(event.payload.id ?? ''))
  }

  if (event.type === 'system.log') {
    appendLog(String(event.payload.line ?? ''))
  }
}

function appendLog(line: string): void {
  if (!line.trim() || isNoisyYtdlpProgress(line)) return

  const entry: LogEntry = {
    id: `log-${++logSequence}`,
    line,
  }
  logs.update((items) => [...items, entry].slice(-MAX_LOGS))
}

function upsertProgress(event: AppEvent): void {
  const progress = progressFromEvent(event)
  if (!progress) return
  const progressKey = keyForProgress(progress)

  jobProgress.update((items) => {
    const index = items.findIndex((item) => keyForProgress(item) === progressKey)
    if (index === -1) return [...items, progress]

    const next = [...items]
    next[index] = progress
    return next
  })
}

function removeProgress(jobId: string): void {
  if (!jobId) return
  jobProgress.update((items) => items.filter((item) => item.jobId !== jobId))
}

function progressFromEvent(event: AppEvent): JobProgress | null {
  const jobId = String(event.payload.job_id ?? '')
  const streamId = String(event.payload.stream_id ?? 'main')
  const line = String(event.payload.line ?? '')
  if (!jobId || !line.trim()) return null

  return {
    jobId,
    streamId,
    title: String(event.payload.title ?? ''),
    line,
    percent: numberOrNull(event.payload.percent),
    speed: String(event.payload.speed ?? ''),
    eta: String(event.payload.eta ?? ''),
    downloaded: String(event.payload.downloaded ?? ''),
    elapsed: String(event.payload.elapsed ?? ''),
    fragment: numberOrNull(event.payload.fragment),
    fragmentTotal: numberOrNull(event.payload.fragment_total),
    updatedAt: event.timestamp,
  }
}

function keyForProgress(progress: JobProgress): string {
  return `${progress.jobId}:${progress.streamId}`
}

function numberOrNull(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null
}

function isNoisyYtdlpProgress(line: string): boolean {
  const normalized = line.trim().replace(/^\d+:\s+/, '')
  return normalized.startsWith('[download]')
    && (
      /\d+(?:\.\d+)?%/.test(normalized)
      || /\(frag\s+\d+\/\d+\)/.test(normalized)
    )
}
