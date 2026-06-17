<script lang="ts">
  import { Activity } from '@lucide/svelte'
  import type { JobProgress } from '@/types'

  export let progressItems: JobProgress[]

  function progressValue(item: JobProgress): number | null {
    if (item.percent !== null) return item.percent
    if (item.fragment !== null && item.fragmentTotal) {
      return Math.min(100, Math.round((item.fragment / item.fragmentTotal) * 100))
    }
    return null
  }

  function detailText(item: JobProgress): string {
    const parts = []
    if (item.downloaded) parts.push(item.downloaded)
    if (item.speed) parts.push(item.speed)
    if (item.eta) parts.push(`ETA ${item.eta}`)
    if (item.elapsed) parts.push(item.elapsed)
    if (item.fragment !== null && item.fragmentTotal !== null) {
      parts.push(`frag ${item.fragment}/${item.fragmentTotal}`)
    }
    return parts.join(' | ')
  }

  function streamLabel(item: JobProgress): string {
    return item.streamId === 'main' ? '작업' : `트랙 ${item.streamId}`
  }
</script>

<section class="card bg-base-100 border border-base-200/50 shadow-sm">
  <div class="card-body p-5 lg:p-6">
    <div class="flex items-center justify-between gap-3 mb-4">
      <div class="flex items-center gap-2">
        <Activity size={18} class="text-primary" />
        <h2 class="card-title text-lg font-bold tracking-tight text-base-content">다운로드 진행</h2>
      </div>
      <span class="badge badge-neutral badge-sm font-semibold">{progressItems.length}</span>
    </div>

    <div class="space-y-4">
      {#each progressItems as item (item.jobId + ':' + item.streamId)}
        {@const value = progressValue(item)}
        <div class="rounded-lg border border-base-200 bg-base-200/20 p-3">
          <div class="flex items-center justify-between gap-3">
            <div class="min-w-0">
              <span class="block truncate text-sm font-semibold" title={item.title}>{item.title || '작업'}</span>
              <span class="mt-1 inline-flex rounded bg-base-300/70 px-2 py-0.5 text-[11px] font-semibold text-base-content/70">
                {streamLabel(item)}
              </span>
            </div>
            {#if value !== null}
              <span class="text-xs font-mono tabular-nums opacity-70">{value}%</span>
            {/if}
          </div>

          {#if value !== null}
            <progress class="progress progress-primary h-2 w-full mt-2" value={value} max="100"></progress>
          {/if}

          <div class="mt-2 truncate font-mono text-xs text-base-content/70" title={detailText(item)}>
            {detailText(item) || item.line}
          </div>
        </div>
      {:else}
        <div class="rounded-lg border border-dashed border-base-300 p-6 text-center text-sm text-base-content/50">
          표시할 다운로드 진행이 없습니다.
        </div>
      {/each}
    </div>
  </div>
</section>
