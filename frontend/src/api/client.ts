import type { FileInfo, JobInfo, Settings, ToolStatus } from '@/types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })
  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || response.statusText)
  }
  return response.json() as Promise<T>
}

export const api = {
  settings: () => request<Settings>('/api/settings'),
  saveSettings: (settings: Settings) =>
    request<Settings>('/api/settings', { method: 'PUT', body: JSON.stringify(settings) }),
  tools: () => request<ToolStatus>('/api/tools'),
  installTools: (force = false) => request<ToolStatus>(`/api/tools/install?force=${force}`, { method: 'POST' }),
  openToolsFolder: () => request<void>('/api/tools/open-folder', { method: 'POST' }),
  jobs: () => request<JobInfo[]>('/api/jobs'),
  startLive: (channelIds: string[] = []) =>
    request<JobInfo[]>('/api/jobs/live/start', {
      method: 'POST',
      body: JSON.stringify({ channel_ids: channelIds }),
    }),
  startDownload: (url: string) =>
    request<JobInfo>('/api/jobs/download/start', {
      method: 'POST',
      body: JSON.stringify({ url }),
    }),
  stopJob: (id: string) => request<JobInfo>(`/api/jobs/${id}/stop`, { method: 'POST' }),
  files: () => request<FileInfo[]>('/api/files'),
}
