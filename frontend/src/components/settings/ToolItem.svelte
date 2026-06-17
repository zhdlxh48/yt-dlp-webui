<script lang="ts">
  import type { ToolInfo } from '@/types'

  export let tool: ToolInfo
  export let busy: boolean
  export let downloadPercent: number
</script>

<div class="rounded border border-base-300 p-3 bg-base-200/50">
  <div class="flex items-center justify-between">
    <span class="font-medium text-sm">{tool.name}</span>
    <span class:badge-success={tool.installed} class:badge-ghost={!tool.installed} class="badge badge-sm">
      {tool.installed ? 'OK' : '없음'}
    </span>
  </div>
  <p class="mt-1 truncate text-xs opacity-70" title={tool.path}>{tool.version || tool.path}</p>
  
  {#if busy && !tool.installed && downloadPercent > 0}
    <div class="flex items-center gap-2 mt-2">
      <progress class="progress progress-primary w-full h-1.5" value={downloadPercent} max="100"></progress>
      <span class="text-xs font-mono opacity-80">{downloadPercent}%</span>
    </div>
  {/if}
</div>
