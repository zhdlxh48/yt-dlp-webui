<script lang="ts">
  import type { ToolStatus } from '@/types'
  import { ko as t } from '@/i18n/ko'
  import ToolItem from './ToolItem.svelte'

  export let tools: ToolStatus
  export let busy: boolean
  export let downloadPercents: Record<string, number>
  export let toolMessage: string
  export let hasRunningJobs: boolean

  // 부모 콜백 함수
  export let onOpenToolsFolder: () => Promise<void>
  export let onInstallTools: (force: boolean) => Promise<void>
</script>

<div class="rounded-box bg-base-100 p-4 shadow-sm mt-4">
  <div class="mb-3 flex items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <h2 class="text-base font-semibold">{t.tools}</h2>
      {#if toolMessage}
        <span class="text-xs text-primary animate-pulse">{toolMessage}</span>
      {/if}
    </div>
    <div class="flex items-center gap-2">
      <button class="btn btn-xs btn-outline" disabled={busy} on:click={onOpenToolsFolder}>
        설치 위치 열기
      </button>
      <button 
        class="btn btn-xs btn-error" 
        disabled={busy || hasRunningJobs} 
        on:click={() => onInstallTools(true)}
        title={hasRunningJobs ? "감시 작업이 진행 중일 때는 재설정할 수 없습니다." : ""}
      >
        재설치
      </button>
    </div>
  </div>

  <div class="grid gap-2">
    {#each tools.tools as tool}
      <ToolItem
        {tool}
        {busy}
        downloadPercent={downloadPercents[tool.name] || 0}
      />
    {:else}
      <div class="rounded border border-base-300 p-3 text-sm opacity-70">도구 상태를 불러오는 중</div>
    {/each}
  </div>
</div>
