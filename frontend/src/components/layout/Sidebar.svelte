<script lang="ts">
  import { Download, FolderOpen, Settings as SettingsIcon, Palette, Tv } from '@lucide/svelte'
  import { ko as t } from '@/i18n/ko'
  import { activeTheme, themes } from '@/stores/theme'

  export let activeTab: 'live' | 'downloads' | 'settings' | 'files'
  export let connected: boolean
  export let runningLiveJobsCount: number
  export let runningDownloadJobsCount: number
  export let channelsCount: number

  let dropdownOpen = false
</script>

<aside class="flex h-full w-72 flex-col bg-base-100 border-r border-base-200/60 p-4 text-base-content shadow-sm transition-all duration-300">
  <!-- Brand Logo & Name -->
  <div class="flex items-center gap-3 px-2 py-4">
    <div class="flex size-10 items-center justify-center rounded-xl bg-linear-to-tr from-primary to-secondary text-primary-content shadow-md shadow-primary/20">
      <Download size={22} class="animate-bounce" />
    </div>
    <div>
      <h1 class="text-xl font-bold tracking-tight bg-linear-to-r from-primary to-secondary bg-clip-text text-transparent">
        {t.appName}
      </h1>
      <div class="flex items-center gap-1.5 text-xs font-semibold opacity-80 mt-0.5">
        <span class:bg-success={connected} class:bg-warning={!connected} class="size-2 rounded-full inline-block animate-ping"></span>
        <span class="opacity-70">{connected ? t.websocketOnline : t.websocketOffline}</span>
      </div>
    </div>
  </div>

  <!-- Navigation Menu -->
  <nav class="mt-8 flex-1">
    <ul class="menu menu-md w-full gap-1 p-0">
      <li>
        <button
          class="flex items-center gap-3 rounded-lg py-3 px-4 transition-all duration-200"
          class:active={activeTab === 'live'}
          on:click={() => (activeTab = 'live')}
        >
          <Tv size={18} />
          <span class="font-medium">{t.liveChannels}</span>
          {#if runningLiveJobsCount > 0}
            <span class="badge badge-sm badge-secondary ml-auto">{runningLiveJobsCount}</span>
          {/if}
        </button>
      </li>
      <li>
        <button
          class="flex items-center gap-3 rounded-lg py-3 px-4 transition-all duration-200"
          class:active={activeTab === 'downloads'}
          on:click={() => (activeTab = 'downloads')}
        >
          <Download size={18} />
          <span class="font-medium">{t.generalDownload}</span>
          {#if runningDownloadJobsCount > 0}
            <span class="badge badge-sm badge-primary ml-auto">{runningDownloadJobsCount}</span>
          {/if}
        </button>
      </li>
      <li>
        <button
          class="flex items-center gap-3 rounded-lg py-3 px-4 transition-all duration-200"
          class:active={activeTab === 'files'}
          on:click={() => (activeTab = 'files')}
        >
          <FolderOpen size={18} />
          <span class="font-medium">{t.files}</span>
        </button>
      </li>
      <li>
        <button
          class="flex items-center gap-3 rounded-lg py-3 px-4 transition-all duration-200"
          class:active={activeTab === 'settings'}
          on:click={() => (activeTab = 'settings')}
        >
          <SettingsIcon size={18} />
          <span class="font-medium">{t.settings}</span>
        </button>
      </li>
    </ul>
  </nav>

  <!-- Sidebar Stats Panel (Using DaisyUI Stats) -->
  <div class="stats stats-vertical shadow-sm border border-base-200/50 w-full bg-base-200/30 rounded-xl my-4">
    <div class="stat p-3">
      <div class="stat-title text-xs font-semibold opacity-70">모니터링 채널</div>
      <div class="stat-value text-xl font-extrabold text-primary mt-0.5">{channelsCount}</div>
    </div>
    <div class="stat p-3 border-t border-base-200/50">
      <div class="stat-title text-xs font-semibold opacity-70">실행 중 작업</div>
      <div class="stat-value text-xl font-extrabold text-secondary mt-0.5">{runningLiveJobsCount + runningDownloadJobsCount}</div>
    </div>
  </div>

  <!-- Theme Selector (Custom dropdown with color swatches) -->
  <div class="form-control w-full mt-auto">
    <label class="label py-1">
      <span class="label-text flex items-center gap-1.5 text-xs font-semibold opacity-70">
        <Palette size={14} class="text-primary" />
        화면 테마 설정
      </span>
    </label>
    <details class="dropdown dropdown-top w-full" bind:open={dropdownOpen}>
      <summary
        class="btn bg-base-200 border border-base-300 hover:bg-base-300 text-base-content btn-sm w-full flex items-center justify-between px-3 shadow-sm font-semibold rounded-lg list-none"
      >
        <span class="capitalize">{themes.find(t => t.name === $activeTheme)?.label || $activeTheme}</span>
        <div class="flex gap-1 items-center">
          <div class="flex gap-0.5 shrink-0 mr-1.5">
            <span class="size-2 rounded-full border border-base-content/10" style="background-color: {themes.find(t => t.name === $activeTheme)?.primary}"></span>
            <span class="size-2 rounded-full border border-base-content/10" style="background-color: {themes.find(t => t.name === $activeTheme)?.secondary}"></span>
            <span class="size-2 rounded-full border border-base-content/10" style="background-color: {themes.find(t => t.name === $activeTheme)?.accent}"></span>
          </div>
          <span class="text-[10px] opacity-60">▲</span>
        </div>
      </summary>
      <div
        role="menu"
        class="dropdown-content bg-base-200 border border-base-300 rounded-xl z-50 w-full p-2 shadow-xl mb-2 grid grid-cols-2 gap-1.5"
      >
        {#each themes as theme}
          <button
            class="flex flex-col items-stretch p-2.5 rounded-lg border transition-all duration-200 text-left gap-1.5 cursor-pointer shadow-xs w-full theme-preview-{theme.name}"
            class:ring-2={$activeTheme === theme.name}
            class:ring-primary={$activeTheme === theme.name}
            class:ring-offset-1={$activeTheme === theme.name}
            on:click={() => {
              activeTheme.set(theme.name)
              dropdownOpen = false
            }}
          >
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold truncate">{theme.label}</span>
              {#if $activeTheme === theme.name}
                <span class="size-1.5 rounded-full" style="background-color: {theme.primary}"></span>
              {/if}
            </div>
            <div class="flex gap-0.5 h-3.5 w-full rounded overflow-hidden opacity-95">
              <div style="background-color: {theme.primary}" class="flex-1"></div>
              <div style="background-color: {theme.secondary}" class="flex-1"></div>
              <div style="background-color: {theme.accent}" class="flex-1"></div>
              <div style="background-color: {theme.neutral}" class="flex-1"></div>
            </div>
          </button>
        {/each}
      </div>
    </details>
  </div>
</aside>
