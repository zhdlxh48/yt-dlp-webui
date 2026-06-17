<script lang="ts">
  import type { JobInfo } from '@/types'
  import { ko as t } from '@/i18n/ko'
  import JobItem from './JobItem.svelte'

  export let jobs: JobInfo[]
  export let runningJobs: JobInfo[]
  export let onStopJob: (id: string, force: boolean) => Promise<void>
</script>

<div class="card bg-base-100 border border-base-200/50 shadow-sm transition-all duration-200 hover:shadow-md">
  <div class="card-body p-5 lg:p-6">
    <div class="flex items-center justify-between gap-3 mb-4">
      <h2 class="card-title text-lg font-bold tracking-tight text-base-content">{t.jobs}</h2>
      <span class="badge badge-neutral badge-sm font-semibold">{jobs.length}</span>
    </div>
    <div class="space-y-3 max-h-[320px] overflow-y-auto pr-1">
      {#each jobs as job}
        <JobItem
          {job}
          isRunning={runningJobs.some((item) => item.id === job.id)}
          onStop={onStopJob}
        />
      {:else}
        <div class="flex flex-col items-center justify-center rounded-xl border border-dashed border-base-300 p-8 text-center bg-base-50/10">
          <p class="text-sm text-base-content/50">진행 중인 작업이 없습니다.</p>
        </div>
      {/each}
    </div>
  </div>
</div>
