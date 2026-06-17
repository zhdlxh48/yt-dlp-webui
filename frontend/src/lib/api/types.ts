export type LiveChannel = {
  id: string
  name: string
  handle: string
  url: string
  enabled: boolean
}

export type Settings = {
  app: {
    language: string
    open_browser_on_start: boolean
    start_monitoring_on_launch: boolean
  }
  paths: {
    downloads_dir: string
    app_data_dir: string
  }
  tools: {
    yt_dlp_path: string
    ffmpeg_path: string
    deno_path: string
    auto_install_tools: boolean
  }
  live: {
    channels: LiveChannel[]
    wait_for_video_seconds: number
    live_from_start: boolean
    retry_policy: {
      retries: string
      fragment_retries: string
      socket_timeout: number
    }
  }
  download: {
    format_selector: string
    merge_output_format: string
    output_template: string
    extra_args: string
  }
  auth: {
    cookies_file: string
  }
  startup: {
    enabled: boolean
  }
}

export type ToolInfo = {
  name: 'yt-dlp' | 'ffmpeg' | 'deno'
  installed: boolean
  path: string
  version: string
}

export type ToolStatus = {
  tools: ToolInfo[]
}

export type JobInfo = {
  id: string
  kind: 'live' | 'download'
  title: string
  status: 'starting' | 'running' | 'stopping' | 'finished' | 'failed' | 'stopped'
  command: string[]
  started_at: string
  finished_at: string
  return_code: number | null
  channel_id?: string
}

export type FileInfo = {
  name: string
  path: string
  size: number
  modified_at: string
}

export type AppEvent = {
  type:
    | 'app.status'
    | 'job.started'
    | 'job.progress'
    | 'job.log'
    | 'job.finished'
    | 'job.error'
    | 'tools.status'
    | 'settings.updated'
    | 'system.log'
  payload: Record<string, unknown>
  timestamp: string
}

