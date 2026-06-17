<script lang="ts">
  import type { JobInfo } from '@/types'
  import { ko as t } from '@/i18n/ko'
  import JobItem from './JobItem.svelte'

  export let jobs: JobInfo[]
  export let runningJobs: JobInfo[]

  // 부모 콜백 함수
  export let onStopJob: (id: string) => Promise<void>
</script>

<div class="rounded-box bg-base-100 p-4 shadow-sm">
  <h2 class="mb-3 text-base font-semibold">{t.jobs}</h2>
  <div class="space-y-2">
    {#each jobs as job}
      <JobItem
        {job}
        isRunning={runningJobs.some((item) => item.id === job.id)}
        onStop={onStopJob}
      />
    {:else}
      <div class="rounded border border-dashed border-base-300 p-4 text-sm opacity-70">작업 없음</div>
    {/each}
  </div>
</div>
