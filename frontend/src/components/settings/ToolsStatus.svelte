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

<div class="card bg-base-100 border border-base-200/50 shadow-sm transition-all duration-200 hover:shadow-md">
  <div class="card-body p-5 lg:p-6">
    <div class="flex items-center justify-between gap-4 border-b border-base-200/60 pb-3 mb-4">
      <div class="flex items-center gap-2">
        <h2 class="card-title text-lg font-bold tracking-tight text-base-content">{t.tools}</h2>
        {#if toolMessage}
          <span class="badge badge-info badge-sm animate-pulse">{toolMessage}</span>
        {/if}
      </div>
      <div class="flex items-center gap-2">
        <button class="btn btn-sm btn-outline btn-secondary" disabled={busy} on:click={onOpenToolsFolder}>
          설치 위치 열기
        </button>
        <button 
          class="btn btn-sm btn-outline btn-error" 
          disabled={busy || hasRunningJobs} 
          on:click={() => onInstallTools(true)}
          title={hasRunningJobs ? "감시 작업이 진행 중일 때는 재설정할 수 없습니다." : ""}
        >
          재설치
        </button>
      </div>
    </div>

    <p class="text-sm opacity-70 mb-4">다운로드 백엔드 실행을 위한 바이너리 의존성 도구들의 상태입니다.</p>

    <div class="flex flex-col gap-3">
      {#each tools.tools as tool}
        <ToolItem
          {tool}
          {busy}
          downloadPercent={downloadPercents[tool.name] || 0}
        />
      {:else}
        <div class="col-span-full rounded-xl border border-dashed border-base-300 p-8 text-center text-sm opacity-70 bg-base-50/10">
          도구 상태를 불러오는 중...
        </div>
      {/each}
    </div>
  </div>
</div>
