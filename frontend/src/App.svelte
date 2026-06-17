<script lang="ts">
  import { onMount } from 'svelte'
  import {
    Activity,
    Download,
    FolderOpen,
    Play,
    Plug,
    Save,
    Settings as SettingsIcon,
    Square,
    Trash2,
    Wrench,
  } from '@lucide/svelte'
  import { api } from './lib/api/client'
  import type { FileInfo, JobInfo, LiveChannel, Settings, ToolStatus } from './lib/api/types'
  import { connected, connectEvents, logs } from './lib/stores/events'
  import { ko as t } from './lib/i18n/ko'

  let settings: Settings | null = null
  let tools: ToolStatus = { tools: [] }
  let jobs: JobInfo[] = []
  let files: FileInfo[] = []
  let activeTab: 'dashboard' | 'settings' | 'files' = 'dashboard'
  let downloadUrl = ''
  let busy = false
  let errorMessage = ''

  onMount(() => {
    connectEvents()
    void refreshAll()
    const id = window.setInterval(refreshRuntime, 5000)
    return () => window.clearInterval(id)
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

  async function installTools() {
    await withBusy(async () => {
      tools = await api.installTools()
    })
  }

  async function startLive() {
    await withBusy(async () => {
      await api.startLive()
      jobs = await api.jobs()
    })
  }

  async function startDownload() {
    const url = downloadUrl.trim()
    if (!url) return
    await withBusy(async () => {
      await api.startDownload(url)
      downloadUrl = ''
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

  function addChannel() {
    if (!settings) return
    const channel: LiveChannel = {
      id: crypto.randomUUID(),
      name: '',
      url: '',
      enabled: true,
    }
    settings.live.channels = [...settings.live.channels, channel]
    settings = settings
  }

  function removeChannel(id: string) {
    if (!settings) return
    settings.live.channels = settings.live.channels.filter((channel) => channel.id !== id)
    settings = settings
  }

  function formatSize(size: number) {
    if (size < 1024) return `${size} B`
    if (size < 1024 ** 2) return `${(size / 1024).toFixed(1)} KB`
    if (size < 1024 ** 3) return `${(size / 1024 ** 2).toFixed(1)} MB`
    return `${(size / 1024 ** 3).toFixed(2)} GB`
  }

  $: runningJobs = jobs.filter((job) => ['starting', 'running', 'stopping'].includes(job.status))
  $: installedCount = tools.tools.filter((tool) => tool.installed).length
</script>

<svelte:head>
  <title>yt-dlp webui</title>
</svelte:head>

<main class="min-h-screen bg-base-200 text-base-content">
  <div class="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-4 lg:px-6">
    <header class="navbar rounded-box bg-base-100 shadow-sm">
      <div class="flex-1 gap-3">
        <div class="flex size-10 items-center justify-center rounded bg-primary text-primary-content">
          <Download size={22} />
        </div>
        <div>
          <h1 class="text-lg font-semibold leading-tight">{t.appName}</h1>
          <div class="flex items-center gap-2 text-xs opacity-70">
            <span class:badge-success={$connected} class:badge-warning={!$connected} class="badge badge-xs"></span>
            {$connected ? t.websocketOnline : t.websocketOffline}
          </div>
        </div>
      </div>
      <nav class="tabs tabs-box">
        <button class:tab-active={activeTab === 'dashboard'} class="tab" on:click={() => (activeTab = 'dashboard')}>
          <Activity size={16} /> {t.dashboard}
        </button>
        <button class:tab-active={activeTab === 'settings'} class="tab" on:click={() => (activeTab = 'settings')}>
          <SettingsIcon size={16} /> {t.settings}
        </button>
        <button class:tab-active={activeTab === 'files'} class="tab" on:click={() => (activeTab = 'files')}>
          <FolderOpen size={16} /> {t.files}
        </button>
      </nav>
    </header>

    {#if errorMessage}
      <div class="alert alert-error mt-4">
        <span>{errorMessage}</span>
      </div>
    {/if}

    {#if activeTab === 'dashboard'}
      <section class="grid gap-4 py-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div class="space-y-4">
          <div class="rounded-box bg-base-100 p-4 shadow-sm">
            <div class="mb-3 flex items-center justify-between">
              <h2 class="text-base font-semibold">{t.tools}</h2>
              <button class="btn btn-sm btn-primary" disabled={busy} on:click={installTools}>
                <Wrench size={16} /> {t.installTools}
              </button>
            </div>
            <div class="grid gap-2 md:grid-cols-3">
              {#each tools.tools as tool}
                <div class="rounded border border-base-300 p-3">
                  <div class="flex items-center justify-between">
                    <span class="font-medium">{tool.name}</span>
                    <span class:badge-success={tool.installed} class:badge-ghost={!tool.installed} class="badge">
                      {tool.installed ? 'OK' : '없음'}
                    </span>
                  </div>
                  <p class="mt-2 truncate text-xs opacity-70" title={tool.path}>{tool.version || tool.path}</p>
                </div>
              {/each}
              {#if tools.tools.length === 0}
                <div class="rounded border border-base-300 p-3 text-sm opacity-70">도구 상태를 불러오는 중</div>
              {/if}
            </div>
          </div>

          <div class="rounded-box bg-base-100 p-4 shadow-sm">
            <div class="mb-3 flex items-center justify-between">
              <h2 class="text-base font-semibold">{t.liveChannels}</h2>
              <button class="btn btn-sm btn-primary" disabled={busy || installedCount < 1} on:click={startLive}>
                <Play size={16} /> {t.startMonitoring}
              </button>
            </div>
            {#if settings?.live.channels.length}
              <div class="overflow-x-auto">
                <table class="table table-sm">
                  <thead>
                    <tr><th>{t.enabled}</th><th>{t.name}</th><th>{t.url}</th></tr>
                  </thead>
                  <tbody>
                    {#each settings.live.channels as channel}
                      <tr>
                        <td>{channel.enabled ? 'ON' : 'OFF'}</td>
                        <td>{channel.name || '-'}</td>
                        <td class="max-w-[360px] truncate">{channel.url}</td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            {:else}
              <div class="rounded border border-dashed border-base-300 p-4 text-sm opacity-70">등록된 채널 없음</div>
            {/if}
          </div>

          <div class="rounded-box bg-base-100 p-4 shadow-sm">
            <h2 class="mb-3 text-base font-semibold">{t.generalDownload}</h2>
            <div class="join w-full">
              <input class="input join-item input-bordered w-full" bind:value={downloadUrl} placeholder="https://..." />
              <button class="btn join-item btn-primary" disabled={busy || !downloadUrl.trim()} on:click={startDownload}>
                <Download size={16} /> {t.download}
              </button>
            </div>
          </div>
        </div>

        <aside class="space-y-4">
          <div class="rounded-box bg-base-100 p-4 shadow-sm">
            <h2 class="mb-3 text-base font-semibold">{t.jobs}</h2>
            <div class="space-y-2">
              {#each jobs as job}
                <div class="rounded border border-base-300 p-3">
                  <div class="flex items-center justify-between gap-2">
                    <span class="truncate text-sm font-medium">{job.title}</span>
                    <span class="badge">{job.status}</span>
                  </div>
                  <div class="mt-2 flex items-center justify-between text-xs opacity-70">
                    <span>{job.kind}</span>
                    {#if runningJobs.some((item) => item.id === job.id)}
                      <button class="btn btn-xs" on:click={() => stopJob(job.id)}>
                        <Square size={12} /> {t.stop}
                      </button>
                    {/if}
                  </div>
                </div>
              {:else}
                <div class="rounded border border-dashed border-base-300 p-4 text-sm opacity-70">작업 없음</div>
              {/each}
            </div>
          </div>

          <div class="rounded-box bg-neutral p-4 text-neutral-content shadow-sm">
            <div class="mb-3 flex items-center gap-2">
              <Plug size={16} />
              <h2 class="text-base font-semibold">{t.logs}</h2>
            </div>
            <div class="max-h-[480px] space-y-1 overflow-y-auto font-mono text-xs">
              {#each $logs as line}
                <p class="log-line">{line}</p>
              {:else}
                <p class="opacity-60">로그 대기 중</p>
              {/each}
            </div>
          </div>
        </aside>
      </section>
    {/if}

    {#if activeTab === 'settings' && settings}
      <section class="grid gap-4 py-4 lg:grid-cols-2">
        <div class="rounded-box bg-base-100 p-4 shadow-sm">
          <div class="mb-3 flex items-center justify-between">
            <h2 class="text-base font-semibold">{t.settings}</h2>
            <button class="btn btn-sm btn-primary" disabled={busy} on:click={saveSettings}>
              <Save size={16} /> {t.save}
            </button>
          </div>
          <div class="grid gap-3">
            <label class="form-control">
              <span class="label-text">{t.downloadsDir}</span>
              <input class="input input-bordered" bind:value={settings.paths.downloads_dir} />
            </label>
            <label class="form-control">
              <span class="label-text">cookies.txt</span>
              <input class="input input-bordered" bind:value={settings.auth.cookies_file} />
            </label>
            <label class="form-control">
              <span class="label-text">Format</span>
              <input class="input input-bordered" bind:value={settings.download.format_selector} />
            </label>
            <label class="form-control">
              <span class="label-text">Extra yt-dlp args</span>
              <textarea class="textarea textarea-bordered min-h-24" bind:value={settings.download.extra_args}></textarea>
            </label>
            <div class="grid gap-2 md:grid-cols-2">
              <label class="label cursor-pointer justify-start gap-3">
                <input class="toggle toggle-primary" type="checkbox" bind:checked={settings.app.open_browser_on_start} />
                <span class="label-text">시작 시 브라우저 열기</span>
              </label>
              <label class="label cursor-pointer justify-start gap-3">
                <input class="toggle toggle-primary" type="checkbox" bind:checked={settings.app.start_monitoring_on_launch} />
                <span class="label-text">앱 시작 시 감시</span>
              </label>
              <label class="label cursor-pointer justify-start gap-3">
                <input class="toggle toggle-primary" type="checkbox" bind:checked={settings.tools.auto_install_tools} />
                <span class="label-text">도구 자동 설치</span>
              </label>
              <label class="label cursor-pointer justify-start gap-3">
                <input class="toggle toggle-primary" type="checkbox" bind:checked={settings.startup.enabled} />
                <span class="label-text">로그인 시 자동 실행</span>
              </label>
            </div>
          </div>
        </div>

        <div class="rounded-box bg-base-100 p-4 shadow-sm">
          <div class="mb-3 flex items-center justify-between">
            <h2 class="text-base font-semibold">{t.liveChannels}</h2>
            <button class="btn btn-sm" on:click={addChannel}>
              <Play size={16} /> {t.addChannel}
            </button>
          </div>
          <div class="space-y-3">
            {#each settings.live.channels as channel}
              <div class="rounded border border-base-300 p-3">
                <div class="grid gap-2 md:grid-cols-[0.7fr_1.5fr_auto]">
                  <input class="input input-sm input-bordered" bind:value={channel.name} placeholder={t.name} />
                  <input class="input input-sm input-bordered" bind:value={channel.url} placeholder="https://youtube.com/@channel/live" />
                  <button class="btn btn-sm btn-ghost" on:click={() => removeChannel(channel.id)} title={t.remove}>
                    <Trash2 size={16} />
                  </button>
                </div>
                <label class="label mt-2 cursor-pointer justify-start gap-3">
                  <input class="checkbox checkbox-sm" type="checkbox" bind:checked={channel.enabled} />
                  <span class="label-text">{t.enabled}</span>
                </label>
              </div>
            {:else}
              <div class="rounded border border-dashed border-base-300 p-4 text-sm opacity-70">등록된 채널 없음</div>
            {/each}
          </div>
        </div>
      </section>
    {/if}

    {#if activeTab === 'files'}
      <section class="py-4">
        <div class="rounded-box bg-base-100 p-4 shadow-sm">
          <h2 class="mb-3 text-base font-semibold">{t.files}</h2>
          <div class="overflow-x-auto">
            <table class="table table-sm">
              <thead>
                <tr><th>파일</th><th>크기</th><th>수정</th><th>경로</th></tr>
              </thead>
              <tbody>
                {#each files as file}
                  <tr>
                    <td>{file.name}</td>
                    <td>{formatSize(file.size)}</td>
                    <td>{new Date(file.modified_at).toLocaleString()}</td>
                    <td class="max-w-[360px] truncate" title={file.path}>{file.path}</td>
                  </tr>
                {:else}
                  <tr><td colspan="4" class="opacity-70">파일 없음</td></tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    {/if}
  </div>
</main>

