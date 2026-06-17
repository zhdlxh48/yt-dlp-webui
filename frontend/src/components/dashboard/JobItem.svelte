<script lang="ts">
  import { Square } from '@lucide/svelte'
  import type { JobInfo } from '@/types'
  import { ko as t } from '@/i18n/ko'

  export let job: JobInfo
  export let isRunning: boolean

  // 부모 콜백 함수
  export let onStop: (id: string) => Promise<void>
</script>

<div class="rounded-xl border border-base-200 p-3.5 bg-base-200/20 hover:bg-base-200/50 hover:border-base-300/80 transition-all duration-200 shadow-sm flex flex-col gap-2">
  <div class="flex items-start justify-between gap-3">
    <span class="truncate text-sm font-semibold text-base-content" title={job.title}>
      {job.title || '알 수 없는 동영상'}
    </span>
    <span
      class="badge badge-sm font-bold uppercase"
      class:badge-info={job.status === 'running'}
      class:badge-success={job.status === 'finished'}
      class:badge-error={job.status === 'failed' || job.status === 'stopped'}
      class:badge-neutral={['starting', 'pending', 'stopping'].includes(job.status)}
    >
      {job.status}
    </span>
  </div>
  
  <div class="flex items-center justify-between text-xs mt-1">
    <span class="opacity-70 font-medium tracking-wide capitalize">{job.kind}</span>
    {#if isRunning}
      <button class="btn btn-xs btn-error btn-outline gap-1" on:click={() => onStop(job.id)}>
        <Square size={10} class="fill-current" /> {t.stop}
      </button>
    {/if}
  </div>
</div>
