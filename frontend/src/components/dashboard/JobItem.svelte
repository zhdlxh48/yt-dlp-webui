<script lang="ts">
  import { Square } from '@lucide/svelte'
  import type { JobInfo } from '@/types'
  import { ko as t } from '@/i18n/ko'

  export let job: JobInfo
  export let isRunning: boolean

  // 부모 콜백 함수
  export let onStop: (id: string) => Promise<void>
</script>

<div class="rounded border border-base-300 p-3 bg-base-50">
  <div class="flex items-center justify-between gap-2">
    <span class="truncate text-sm font-medium" title={job.title}>{job.title}</span>
    <span class="badge badge-sm">{job.status}</span>
  </div>
  <div class="mt-2 flex items-center justify-between text-xs opacity-70">
    <span>{job.kind}</span>
    {#if isRunning}
      <button class="btn btn-xs" on:click={() => onStop(job.id)}>
        <Square size={12} /> {t.stop}
      </button>
    {/if}
  </div>
</div>
