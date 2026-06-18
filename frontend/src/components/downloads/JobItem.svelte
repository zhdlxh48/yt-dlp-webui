<script lang="ts">
  import { Square } from '@lucide/svelte'
  import type { JobInfo } from '@/types'
  import { ko as t } from '@/i18n/ko'

  export let job: JobInfo
  export let isRunning: boolean
  export let onStop: (id: string, force: boolean) => Promise<void>

  $: isStopping = job.status === 'stopping'

  $: statusText = (() => {
    if (job.status === 'running') {
      if (job.kind === 'live') {
        return job.is_downloading ? '녹화 중' : '감시 중'
      }
      return '다운로드 중'
    }
    const map: Record<string, string> = {
      starting: '시작 중',
      stopping: '종료 중',
      finished: '완료',
      failed: '실패',
      stopped: '정지됨',
    }
    return map[job.status] || job.status
  })()
</script>

<div class="rounded-xl border border-base-200 p-3.5 bg-base-200/20 hover:bg-base-200/50 hover:border-base-300/80 transition-all duration-200 shadow-sm flex flex-col gap-2">
  <div class="flex items-start justify-between gap-3">
    <span class="truncate text-sm font-semibold text-base-content" title={job.title}>
      {job.title || '알 수 없는 동영상'}
    </span>
    <span
      class="badge badge-sm font-bold"
      class:badge-info={job.status === 'running' && !(job.kind === 'live' && job.is_downloading)}
      class:badge-success={job.status === 'finished' || (job.status === 'running' && job.kind === 'live' && job.is_downloading)}
      class:badge-error={job.status === 'failed' || job.status === 'stopped'}
      class:badge-neutral={['starting', 'pending', 'stopping'].includes(job.status)}
    >
      {statusText}
    </span>
  </div>

  <div class="flex items-center justify-between text-xs mt-1">
    <span class="opacity-70 font-medium tracking-wide capitalize">{job.kind}</span>
    {#if isRunning}
      <div class="flex items-center gap-1.5">
        <button
          class="btn btn-xs btn-error btn-outline gap-1"
          disabled={isStopping}
          on:click={() => onStop(job.id, false)}
          title="ffmpeg 병합을 기다리는 안전 종료"
        >
          <Square size={10} class="fill-current" /> {t.stop}
        </button>
        <button
          class="btn btn-xs btn-error gap-1"
          on:click={() => onStop(job.id, true)}
          title="프로세스 트리를 즉시 종료"
        >
          <Square size={10} class="fill-current" /> {t.forceStop}
        </button>
      </div>
    {/if}
  </div>
</div>
