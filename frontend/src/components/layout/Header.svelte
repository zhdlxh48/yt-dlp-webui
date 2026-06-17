<script lang="ts">
  import { Activity, Download, FolderOpen, Settings as SettingsIcon } from '@lucide/svelte'
  import { ko as t } from '@/i18n/ko'

  export let activeTab: 'dashboard' | 'settings' | 'files'
  export let connected: boolean
</script>

<header class="navbar rounded-box bg-base-100 shadow-sm">
  <div class="flex-1 gap-3">
    <div class="flex size-10 items-center justify-center rounded bg-primary text-primary-content">
      <Download size={22} />
    </div>
    <div>
      <h1 class="text-lg font-semibold leading-tight">{t.appName}</h1>
      <div class="flex items-center gap-2 text-xs opacity-70">
        <span class:badge-success={connected} class:badge-warning={!connected} class="badge badge-xs"></span>
        {connected ? t.websocketOnline : t.websocketOffline}
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
