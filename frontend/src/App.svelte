<script lang="ts">
  import { onMount } from 'svelte'
  import { Menu } from '@lucide/svelte'
  import { api } from '@/api/client'
  import type { FileInfo, JobInfo, LiveChannel, Settings, ToolStatus } from '@/types'
  import { connected, connectEvents, events, jobProgress, logs } from '@/stores/events'
  import Sidebar from '@/components/layout/Sidebar.svelte'
  import Dashboard from '@/components/dashboard/Dashboard.svelte'
  import SettingsForm from '@/components/settings/SettingsForm.svelte'
  import ToolsStatus from '@/components/settings/ToolsStatus.svelte'
  import FileList from '@/components/files/FileList.svelte'
  import ToolsModal from '@/components/common/ToolsModal.svelte'
  import LogConsole from '@/components/dashboard/LogConsole.svelte'

  let settings: Settings | null = null
  let tools: ToolStatus = { tools: [] }
  let jobs: JobInfo[] = []
  let files: FileInfo[] = []
  let activeTab: 'dashboard' | 'settings' | 'files' = 'dashboard'
  let busy = false
  let errorMessage = ''
  let downloadPercents: Record<string, number> = { 'yt-dlp': 0, ffmpeg: 0, deno: 0 }
  let drawerChecked = false

  $: if (activeTab) {
    drawerChecked = false
  }

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
    downloadPercents = { 'yt-dlp': 0, ffmpeg: 0, deno: 0 }
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

  async function stopJob(id: string, force = false) {
    await withBusy(async () => {
      await api.stopJob(id, force)
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

  async function handleEditChannel(id: string, name: string, handle: string, enabled: boolean) {
    if (!settings) return
    settings.live.channels = settings.live.channels.map((channel) => {
      if (channel.id === id) {
        return {
          ...channel,
          name,
          handle,
          url: `https://www.youtube.com/${handle}/live`,
          enabled,
        }
      }
      return channel
    })
    settings = settings
    await saveSettings()
  }

  async function handleDeleteChannel(id: string) {
    if (!settings) return
    settings.live.channels = settings.live.channels.filter((channel) => channel.id !== id)
    settings = settings
    await saveSettings()
  }

  async function handleToggleChannelMonitoring(channel: LiveChannel, force = false) {
    const activeJob = jobs.find(
      (job) => job.channel_id === channel.id && ['starting', 'running', 'stopping'].includes(job.status)
    )
    if (activeJob) {
      await stopJob(activeJob.id, force)
    } else {
      await startLive([channel.id])
    }
  }

  $: runningJobs = jobs.filter((job) => ['starting', 'running', 'stopping'].includes(job.status))
  $: installedCount = tools.tools.filter((tool) => tool.installed).length
  $: toolMessage = (() => {
    const statusEvent = $events.find((event) => event.type === 'tools.status')
    if (statusEvent && typeof statusEvent.payload === 'object' && statusEvent.payload !== null) {
      const payload = statusEvent.payload as any
      return payload.message || ''
    }
    return ''
  })()
  $: hasMissingTools = tools.tools.length > 0 && tools.tools.some((tool) => !tool.installed)
</script>

<svelte:head>
  <title>yt-dlp webui</title>
</svelte:head>

<div class="drawer lg:drawer-open min-h-screen bg-base-200">
  <input id="app-drawer" type="checkbox" class="drawer-toggle" bind:checked={drawerChecked} />

  <div class="drawer-content flex flex-col min-h-screen">
    <header class="navbar bg-base-100 border-b border-base-200/50 px-4 flex justify-between lg:hidden sticky top-0 z-30 shadow-sm">
      <div class="flex-none">
        <label for="app-drawer" class="btn btn-ghost btn-square drawer-button">
          <Menu size={20} />
        </label>
      </div>
      <div class="flex-1 justify-center pr-8">
        <span class="text-lg font-bold tracking-tight bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          yt-dlp webui
        </span>
      </div>
    </header>

    <main class="flex-1 p-4 lg:p-6 w-full space-y-6">
      {#if errorMessage}
        <div class="alert alert-error shadow-sm border border-error/20">
          <span>{errorMessage}</span>
        </div>
      {/if}

      {#if activeTab === 'dashboard'}
        <Dashboard
          {settings}
          {jobs}
          progressItems={$jobProgress}
          {busy}
          {installedCount}
          onStartLive={() => startLive()}
          onAddChannel={handleAddChannel}
          onEditChannel={handleEditChannel}
          onDeleteChannel={handleDeleteChannel}
          onToggleMonitoring={handleToggleChannelMonitoring}
          onDownload={startDownload}
          onStopJob={stopJob}
        />
      {/if}

      {#if activeTab === 'settings' && settings}
        <section class="grid gap-6 lg:grid-cols-[1.25fr_0.75fr] w-full items-start">
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
        <section>
          <FileList {files} />
        </section>
      {/if}
    </main>
  </div>

  <div class="drawer-side z-40">
    <label for="app-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
    <Sidebar
      bind:activeTab
      connected={$connected}
      runningJobsCount={runningJobs.length}
      channelsCount={settings?.live.channels.length || 0}
    />
  </div>
</div>

{#if hasMissingTools}
  <ToolsModal
    {tools}
    {busy}
    {downloadPercents}
    onInstallTools={installTools}
  />
{/if}

<LogConsole logs={$logs} />
