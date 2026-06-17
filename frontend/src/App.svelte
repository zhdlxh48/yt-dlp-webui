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
  import { connected, connectEvents, logs, events } from './lib/stores/events'
  import { ko as t } from './lib/i18n/ko'

  let settings: Settings | null = null
  let tools: ToolStatus = { tools: [] }
  let jobs: JobInfo[] = []
  let files: FileInfo[] = []
  let activeTab: 'dashboard' | 'settings' | 'files' = 'dashboard'
  let downloadUrl = ''
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

  // 수정 중인 채널 임시 보관
  let editingChannelId: string | null = null
  let editName = ''
  let editHandle = ''
  let editEnabled = true

  // 추가 중인 임시 채널 정보
  let isAdding = false
  let newName = ''
  let newHandle = ''

  function startAddChannel() {
    isAdding = true
    newName = ''
    newHandle = ''
  }

  function cancelAddChannel() {
    isAdding = false
  }

  async function saveAddChannel() {
    if (!settings) return
    const handle = newHandle.trim()
    if (!handle) return
    const formattedHandle = handle.startsWith('@') ? handle : '@' + handle
    const channel: LiveChannel = {
      id: crypto.randomUUID(),
      name: newName.trim(),
      handle: formattedHandle,
      url: `https://www.youtube.com/${formattedHandle}/live`,
      enabled: true,
    }
    settings.live.channels = [...settings.live.channels, channel]
    isAdding = false
    settings = settings
    await saveSettings()
  }

  function startEditChannel(channel: LiveChannel) {
    editingChannelId = channel.id
    editName = channel.name
    editHandle = channel.handle || ''
    editEnabled = channel.enabled
  }

  function cancelEditChannel() {
    editingChannelId = null
  }

  async function saveEditChannel(id: string) {
    if (!settings) return
    const handle = editHandle.trim()
    if (!handle) return
    const formattedHandle = handle.startsWith('@') ? handle : '@' + handle
    
    settings.live.channels = settings.live.channels.map((c) => {
      if (c.id === id) {
        return {
          ...c,
          name: editName.trim(),
          handle: formattedHandle,
          url: `https://www.youtube.com/${formattedHandle}/live`,
          enabled: editEnabled,
        }
      }
      return c
    })
    editingChannelId = null
    settings = settings
    await saveSettings()
  }

  async function deleteChannel(id: string) {
    if (!settings) return
    settings.live.channels = settings.live.channels.filter((c) => c.id !== id)
    settings = settings
    await saveSettings()
  }

  $: getChannelJob = (channelId: string) => {
    return jobs.find(
      (job) => job.channel_id === channelId && ['starting', 'running', 'stopping'].includes(job.status)
    )
  }

  async function toggleChannelMonitoring(channel: LiveChannel) {
    const activeJob = getChannelJob(channel.id)
    if (activeJob) {
      await withBusy(async () => {
        await api.stopJob(activeJob.id)
        jobs = await api.jobs()
      })
    } else {
      await withBusy(async () => {
        await api.startLive([channel.id])
        jobs = await api.jobs()
      })
    }
  }

  function formatSize(size: number) {
    if (size < 1024) return `${size} B`
    if (size < 1024 ** 2) return `${(size / 1024).toFixed(1)} KB`
    if (size < 1024 ** 3) return `${(size / 1024 ** 2).toFixed(1)} MB`
    return `${(size / 1024 ** 3).toFixed(2)} GB`
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
            <div class="mb-3 flex items-center justify-between gap-4">
              <h2 class="text-base font-semibold">{t.liveChannels}</h2>
              <div class="flex items-center gap-2">
                <button class="btn btn-xs btn-outline" disabled={busy || isAdding} on:click={startAddChannel}>
                  채널 추가
                </button>
                <button class="btn btn-xs btn-primary" disabled={busy || installedCount < 1} on:click={startLive}>
                  <Play size={12} /> 전체 감시 시작
                </button>
              </div>
            </div>
            {#if (settings?.live.channels.length || isAdding)}
              <div class="overflow-x-auto">
                <table class="table table-sm w-full">
                  <thead>
                    <tr>
                      <th>이름</th>
                      <th>유튜브 핸들</th>
                      <th>사용 여부</th>
                      <th>상태</th>
                      <th class="text-right">작업</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each settings?.live.channels || [] as channel}
                      {#if editingChannelId === channel.id}
                        <tr>
                          <td>
                            <input class="input input-xs input-bordered w-full" bind:value={editName} placeholder="채널 이름" />
                          </td>
                          <td>
                            <input class="input input-xs input-bordered w-full" bind:value={editHandle} placeholder="@handle" />
                          </td>
                          <td>
                            <input type="checkbox" class="checkbox checkbox-xs" bind:checked={editEnabled} />
                          </td>
                          <td>-</td>
                          <td class="text-right space-x-1">
                            <button class="btn btn-xs btn-success" disabled={busy} on:click={() => saveEditChannel(channel.id)}>저장</button>
                            <button class="btn btn-xs btn-ghost" on:click={cancelEditChannel}>취소</button>
                          </td>
                        </tr>
                      {:else}
                        <tr>
                          <td class="font-medium">{channel.name || '-'}</td>
                          <td class="text-xs opacity-80">{channel.handle || '-'}</td>
                          <td>
                            <span class="badge badge-sm" class:badge-success={channel.enabled} class:badge-ghost={!channel.enabled}>
                              {channel.enabled ? 'ON' : 'OFF'}
                            </span>
                          </td>
                          <td>
                            {#if getChannelJob(channel.id)}
                              <span class="badge badge-success badge-xs gap-1 animate-pulse">
                                <span class="size-1 rounded-full bg-white"></span>
                                감시 중
                              </span>
                            {:else}
                              <span class="opacity-60 text-xs">대기</span>
                            {/if}
                          </td>
                          <td class="text-right space-x-1">
                            <button 
                              class="btn btn-xs" 
                              class:btn-primary={!getChannelJob(channel.id)} 
                              class:btn-error={getChannelJob(channel.id)} 
                              disabled={busy || installedCount < 1} 
                              on:click={() => toggleChannelMonitoring(channel)}
                            >
                              {#if getChannelJob(channel.id)}
                                정지
                              {:else}
                                감시 시작
                              {/if}
                            </button>
                            <button 
                              class="btn btn-xs btn-outline" 
                              disabled={busy || getChannelJob(channel.id)} 
                              on:click={() => startEditChannel(channel)}
                            >
                              수정
                            </button>
                            <button 
                              class="btn btn-xs btn-ghost text-error" 
                              disabled={busy || getChannelJob(channel.id)} 
                              on:click={() => deleteChannel(channel.id)}
                            >
                              삭제
                            </button>
                          </td>
                        </tr>
                      {/if}
                    {/each}
                    {#if isAdding}
                      <tr class="bg-base-200">
                        <td>
                          <input class="input input-xs input-bordered w-full" bind:value={newName} placeholder="채널 이름" />
                        </td>
                        <td>
                          <input class="input input-xs input-bordered w-full" bind:value={newHandle} placeholder="@handle" />
                        </td>
                        <td>
                          <span class="text-xs opacity-60">ON</span>
                        </td>
                        <td>-</td>
                        <td class="text-right space-x-1">
                          <button class="btn btn-xs btn-success" disabled={busy} on:click={saveAddChannel}>저장</button>
                          <button class="btn btn-xs btn-ghost" on:click={cancelAddChannel}>취소</button>
                        </td>
                      </tr>
                    {/if}
                  </tbody>
                </table>
              </div>
            {:else}
              <div class="rounded border border-dashed border-base-300 p-8 text-center text-sm opacity-70">
                <p class="mb-2">등록된 채널이 없습니다.</p>
                <button class="btn btn-sm btn-primary" on:click={startAddChannel}>채널 추가하기</button>
              </div>
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
      <section class="py-4 max-w-2xl mx-auto w-full">
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

        <div class="rounded-box bg-base-100 p-4 shadow-sm mt-4">
          <div class="mb-3 flex items-center justify-between gap-4">
            <div class="flex items-center gap-3">
              <h2 class="text-base font-semibold">{t.tools}</h2>
              {#if toolMessage}
                <span class="text-xs text-primary animate-pulse">{toolMessage}</span>
              {/if}
            </div>
            <div class="flex items-center gap-2">
              <button class="btn btn-xs btn-outline" disabled={busy} on:click={openToolsFolder}>
                설치 위치 열기
              </button>
              <button 
                class="btn btn-xs btn-error" 
                disabled={busy || runningJobs.length > 0} 
                on:click={() => installTools(true)}
                title={runningJobs.length > 0 ? "감시 작업이 진행 중일 때는 재설정할 수 없습니다." : ""}
              >
                재설치
              </button>
            </div>
          </div>

          <div class="grid gap-2">
            {#each tools.tools as tool}
              <div class="rounded border border-base-300 p-3 bg-base-200/50">
                <div class="flex items-center justify-between">
                  <span class="font-medium text-sm">{tool.name}</span>
                  <span class:badge-success={tool.installed} class:badge-ghost={!tool.installed} class="badge badge-sm">
                    {tool.installed ? 'OK' : '없음'}
                  </span>
                </div>
                <p class="mt-1 truncate text-xs opacity-70" title={tool.path}>{tool.version || tool.path}</p>
                
                {#if busy && !tool.installed && downloadPercents[tool.name] > 0}
                  <div class="flex items-center gap-2 mt-2">
                    <progress class="progress progress-primary w-full h-1.5" value={downloadPercents[tool.name]} max="100"></progress>
                    <span class="text-xs font-mono opacity-80">{downloadPercents[tool.name]}%</span>
                  </div>
                {/if}
              </div>
            {/each}
            {#if tools.tools.length === 0}
              <div class="rounded border border-base-300 p-3 text-sm opacity-70">도구 상태를 불러오는 중</div>
            {/if}
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

{#if hasMissingTools}
  <dialog class="modal modal-open">
    <div class="modal-box max-w-md bg-base-100 shadow-xl border border-base-300">
      <h3 class="font-bold text-lg text-primary flex items-center gap-2">
        <Wrench size={20} />
        필수 도구 설치 필요
      </h3>
      <p class="py-4 text-sm opacity-80 leading-relaxed">
        이 프로그램의 원활한 이용을 위해서는 아래 필수 도구들의 설치가 필요합니다.
      </p>

      <div class="rounded-box border border-base-200 divide-y divide-base-200 max-h-60 overflow-y-auto mb-4 bg-base-200/50 p-2">
        {#each tools.tools as tool}
          <div class="p-3">
            <div class="flex items-center justify-between mb-2">
              <span class="font-semibold text-sm">{tool.name}</span>
              <span class:badge-success={tool.installed} class:badge-warning={!tool.installed} class="badge badge-sm">
                {tool.installed ? '설치 완료' : '미설치'}
              </span>
            </div>
            
            {#if !tool.installed}
              <div class="flex items-center gap-2 mt-1">
                <progress class="progress progress-primary w-full h-2" value={downloadPercents[tool.name] || 0} max="100"></progress>
                <span class="text-xs font-mono opacity-80 min-w-10 text-right">{downloadPercents[tool.name] || 0}%</span>
              </div>
            {/if}
          </div>
        {/each}
      </div>

      <div class="modal-action">
        <button class="btn btn-primary w-full" disabled={busy} on:click={() => installTools(false)}>
          {#if busy}
            <span class="loading loading-spinner loading-xs"></span>
            도구 설치 중...
          {:else}
            도구 설치 시작
          {/if}
        </button>
      </div>
    </div>
  </dialog>
{/if}

