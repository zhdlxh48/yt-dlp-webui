<script lang="ts">
  import { Wrench } from '@lucide/svelte'
  import type { ToolStatus } from '@/types'

  export let tools: ToolStatus
  export let busy: boolean
  export let downloadPercents: Record<string, number>

  // 부모 콜백 함수
  export let onInstallTools: (force: boolean) => Promise<void>
</script>

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
      <button class="btn btn-primary w-full" disabled={busy} on:click={() => onInstallTools(false)}>
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
