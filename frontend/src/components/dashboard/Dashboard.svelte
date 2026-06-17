<script lang="ts">
  import type { JobInfo, JobProgress, LiveChannel, Settings } from '@/types'
  import ChannelList from './ChannelList.svelte'
  import GeneralDownload from './GeneralDownload.svelte'
  import JobList from './JobList.svelte'
  import ProgressPanel from './ProgressPanel.svelte'

  export let settings: Settings | null
  export let jobs: JobInfo[]
  export let progressItems: JobProgress[]
  export let busy: boolean
  export let installedCount: number
  export let onStartLive: () => Promise<void>
  export let onAddChannel: (name: string, handle: string) => Promise<void>
  export let onEditChannel: (id: string, name: string, handle: string, enabled: boolean) => Promise<void>
  export let onDeleteChannel: (id: string) => Promise<void>
  export let onToggleMonitoring: (channel: LiveChannel, force?: boolean) => Promise<void>
  export let onDownload: (url: string) => Promise<void>
  export let onStopJob: (id: string, force: boolean) => Promise<void>

  $: runningJobs = jobs.filter((job) => ['starting', 'running', 'stopping'].includes(job.status))
  $: downloadJobs = jobs.filter((job) => job.kind === 'download')
</script>

<section class="grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
  <div class="space-y-6">
    <ChannelList
      {settings}
      {jobs}
      {busy}
      {installedCount}
      {onStartLive}
      {onAddChannel}
      {onEditChannel}
      {onDeleteChannel}
      {onToggleMonitoring}
    />
    <div class="space-y-4">
      <GeneralDownload {busy} onDownload={onDownload} />
      {#if downloadJobs.length > 0}
        <JobList
          jobs={downloadJobs}
          runningJobs={runningJobs.filter((job) => job.kind === 'download')}
          onStopJob={onStopJob}
        />
      {/if}
    </div>
  </div>

  <aside class="space-y-6">
    <ProgressPanel {progressItems} />
  </aside>
</section>
