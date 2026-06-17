<script lang="ts">
  import type { ToolInfo } from '@/types'

  export let tool: ToolInfo
  export let busy: boolean
  export let downloadPercent: number
</script>

<div class="rounded-xl border border-base-200 p-3.5 bg-base-200/20 hover:bg-base-200/40 transition-all duration-200 shadow-sm flex flex-col gap-2 min-w-0">
  <div class="flex items-center justify-between">
    <span class="font-bold text-sm text-base-content">{tool.name}</span>
    <span
      class="badge badge-sm font-bold shadow-sm"
      class:badge-success={tool.installed}
      class:badge-warning={!tool.installed}
      class:text-success-content={tool.installed}
      class:text-warning-content={!tool.installed}
    >
      {tool.installed ? '설치됨' : '미설치'}
    </span>
  </div>
  <p class="truncate text-xs font-mono opacity-70 leading-relaxed" title={tool.path}>
    {tool.version || tool.path || '경로 없음'}
  </p>
  
  {#if busy && !tool.installed && downloadPercent > 0}
    <div class="flex items-center gap-2 mt-1">
      <progress class="progress progress-primary w-full h-2 shadow-sm" value={downloadPercent} max="100"></progress>
      <span class="text-xs font-mono font-bold opacity-80 min-w-8 text-right">{downloadPercent}%</span>
    </div>
  {/if}
</div>
