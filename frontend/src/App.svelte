<script lang="ts">
  import { onMount } from 'svelte'
  import { api } from '@/api/client'
  import type { FileInfo, JobInfo, LiveChannel, Settings, ToolStatus } from '@/types'
  import { connected, connectEvents, logs, events } from '@/stores/events'

  // 레이아웃 및 뷰 컴포넌트 임포트
  import Header from '@/components/layout/Header.svelte'
  import ChannelList from '@/components/dashboard/ChannelList.svelte'
  import GeneralDownload from '@/components/dashboard/GeneralDownload.svelte'
  import JobList from '@/components/dashboard/JobList.svelte'
  import LogConsole from '@/components/dashboard/LogConsole.svelte'
  import SettingsForm from '@/components/settings/SettingsForm.svelte'
  import ToolsStatus from '@/components/settings/ToolsStatus.svelte'
  import FileList from '@/components/files/FileList.svelte'
  import ToolsModal from '@/components/common/ToolsModal.svelte'

  let settings: Settings | null = null
  let tools: ToolStatus = { tools: [] }
  let jobs: JobInfo[] = []
  let files: FileInfo[] = []
  let activeTab: 'dashboard' | 'settings' | 'files' = 'dashboard'
  let busy = false
  let errorMessage = ''
  let downloadPercents: Record<string, number> = { 'yt-dlp': 0, 'ffmpeg': 0, 'deno': 0 }

  onMount(() => {
    connectEvents()
    void refreshAll()
    const id = window.setInterval(refreshRuntime, 5000)

    const unsubscribe = events.subscribe((evtList) => {
      const statusEvent = evtList[0]
      if (statusEvent && statusEvent.type === 'tools.status') {
        const payload = statusEvent.payload as any
        if (payload.tool && typeof payload.percent === 'number') {
          downloadPercents[payload.tool] = payload.percent >= 0 ? payload.percent : 0
          downloadPercents = { ...downloadPercents }
        }
      }
    })

    return () => {
      window.clearInterval(id)
      unsubscribe()
    }
  })

  async function refreshAll() {
    await withBusy(async () => {
      settings = await api.settings()
      await refreshRuntime()
    })
  }

  async function refreshRuntime() {
    const [toolStatus, jobList, fileList] = await Promise.all([
      api.tools(),
      api.jobs(),
      api.files(),
    ])
    tools = toolStatus
    jobs = jobList
    files = fileList
  }

  async function withBusy(action: () => Promise<void>) {
    busy = true
    errorMessage = ''
    try {
      await action()
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : String(error)
    } finally {
      busy = false
    }
  }

  async function installTools(force = false) {
    downloadPercents = { 'yt-dlp': 0, 'ffmpeg': 0, 'deno': 0 }
    await withBusy(async () => {
      tools = await api.installTools(force)
    })
  }

  async function openToolsFolder() {
    try {
      await api.openToolsFolder()
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : String(error)
    }
  }

  async function startLive(channelIds: string[] = []) {
    await withBusy(async () => {
      await api.startLive(channelIds)
      jobs = await api.jobs()
    })
  }

  async function startDownload(url: string) {
    await withBusy(async () => {
      await api.startDownload(url)
      jobs = await api.jobs()
    })
  }

  async function stopJob(id: string) {
    await withBusy(async () => {
      await api.stopJob(id)
      jobs = await api.jobs()
    })
  }

  async function saveSettings() {
    if (!settings) return
    await withBusy(async () => {
      settings = await api.saveSettings(settings)
      files = await api.files()
    })
  }

  // 라이브 채널 추가
  async function handleAddChannel(name: string, handle: string) {
    if (!settings) return
    const channel: LiveChannel = {
      id: crypto.randomUUID(),
      name,
      handle,
      url: `https://www.youtube.com/${handle}/live`,
      enabled: true,
    }
    settings.live.channels = [...settings.live.channels, channel]
    settings = settings
    await saveSettings()
  }

  // 라이브 채널 수정
  async function handleEditChannel(id: string, name: string, handle: string, enabled: boolean) {
    if (!settings) return
    settings.live.channels = settings.live.channels.map((c) => {
      if (c.id === id) {
        return {
          ...c,
          name,
          handle,
          url: `https://www.youtube.com/${handle}/live`,
          enabled,
        }
      }
      return c
    })
    settings = settings
    await saveSettings()
  }

  // 라이브 채널 삭제
  async function handleDeleteChannel(id: string) {
    if (!settings) return
    settings.live.channels = settings.live.channels.filter((c) => c.id !== id)
    settings = settings
    await saveSettings()
  }

  // 개별 채널 모니터링/정지 제어
  async function handleToggleChannelMonitoring(channel: LiveChannel) {
    const activeJob = jobs.find(
      (job) => job.channel_id === channel.id && ['starting', 'running', 'stopping'].includes(job.status)
    )
    if (activeJob) {
      await stopJob(activeJob.id)
    } else {
      await startLive([channel.id])
    }
  }

  $: runningJobs = jobs.filter((job) => ['starting', 'running', 'stopping'].includes(job.status))
  $: installedCount = tools.tools.filter((tool) => tool.installed).length
  $: toolMessage = (() => {
    const statusEvent = $events.find((e) => e.type === 'tools.status')
    if (statusEvent && typeof statusEvent.payload === 'object' && statusEvent.payload !== null) {
      const payload = statusEvent.payload as any
      return payload.message || ''
    }
    return ''
  })()
  $: hasMissingTools = tools.tools.length > 0 && tools.tools.some((t) => !t.installed)
</script>

<svelte:head>
  <title>yt-dlp webui</title>
</svelte:head>

<main class="min-h-screen bg-base-200 text-base-content">
  <div class="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-4 lg:px-6">
    <Header bind:activeTab connected={$connected} />

    {#if errorMessage}
      <div class="alert alert-error mt-4">
        <span>{errorMessage}</span>
      </div>
    {/if}

    {#if activeTab === 'dashboard'}
      <section class="grid gap-4 py-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div class="space-y-4">
          <ChannelList
            {settings}
            {jobs}
            {busy}
            {installedCount}
            onStartLive={() => startLive()}
            onAddChannel={handleAddChannel}
            onEditChannel={handleEditChannel}
            onDeleteChannel={handleDeleteChannel}
            onToggleMonitoring={handleToggleChannelMonitoring}
          />
          <GeneralDownload {busy} onDownload={startDownload} />
        </div>

        <aside class="space-y-4">
          <JobList {jobs} {runningJobs} onStopJob={stopJob} />
          <LogConsole logs={$logs} />
        </aside>
      </section>
    {/if}

    {#if activeTab === 'settings' && settings}
      <section class="py-4 max-w-2xl mx-auto w-full">
        <SettingsForm bind:settings {busy} onSave={saveSettings} />
        <ToolsStatus
          {tools}
          {busy}
          {downloadPercents}
          {toolMessage}
          hasRunningJobs={runningJobs.length > 0}
          onOpenToolsFolder={openToolsFolder}
          onInstallTools={installTools}
        />
      </section>
    {/if}

    {#if activeTab === 'files'}
      <section class="py-4">
        <FileList {files} />
      </section>
    {/if}
  </div>
</main>

{#if hasMissingTools}
  <ToolsModal
    {tools}
    {busy}
    {downloadPercents}
    onInstallTools={installTools}
  />
{/if}
