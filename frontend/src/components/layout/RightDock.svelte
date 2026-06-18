<script lang="ts">
  import { Activity, Terminal, Trash2, X } from '@lucide/svelte'
  import { fly } from 'svelte/transition'
  import type { JobProgress, LogEntry } from '@/types'
  import { clearLogs } from '@/stores/events'
  import { ko as t } from '@/i18n/ko'

  // Props in Svelte 5 Runes
  interface Props {
    progressItems: JobProgress[]
    logs: LogEntry[]
  }
  let { progressItems, logs }: Props = $props()

  // Reactive state in Svelte 5 Runes
  let activePanel: 'progress' | 'logs' | null = $state(null)
  let consoleEl: HTMLDivElement | undefined = $state()

  function togglePanel(panel: 'progress' | 'logs') {
    if (activePanel === panel) {
      activePanel = null
    } else {
      activePanel = panel
    }
  }

  function closePanel() {
    activePanel = null
  }

  // Auto-scroll for Log Console when logs update
  $effect(() => {
    if (activePanel === 'logs' && consoleEl && logs) {
      setTimeout(() => {
        if (consoleEl) {
          consoleEl.scrollTop = consoleEl.scrollHeight
        }
      }, 50)
    }
  })

  // Helper functions for progress
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

  // Parse log line into timestamp and content
  function parseLogLine(line: string) {
    const cleanLine = line.replace(/^(?:\$>\s*|>\s*|\$\s*)/, '')
    const match = cleanLine.match(/^\[(\d{2}:\d{2}:\d{2})\]\s*(.*)$/)
    if (match) {
      return { time: match[1], content: match[2] }
    }
    return { time: '-', content: cleanLine }
  }

  function streamLabel(item: JobProgress): string {
    return item.streamId === 'main' ? '작업' : `트랙 ${item.streamId}`
  }
</script>

<div class="h-full flex-none w-12 relative z-40">
  <!-- Sliding Panel (Absolute positioning to prevent squishing the main area) -->
  {#if activePanel}
    <div
      transition:fly={{ x: 200, duration: 200 }}
      class="absolute right-12 top-0 h-full w-96 flex flex-col border-l border-base-200/80 bg-base-100 shadow-2xl z-30 overflow-hidden"
    >
      <!-- Panel Header -->
      <div class="p-4 border-b border-base-200 flex items-center justify-between bg-base-100 shrink-0">
        <div class="flex items-center gap-2">
          {#if activePanel === 'progress'}
            <Activity size={18} class="text-primary animate-pulse" />
            <h2 class="text-md font-bold tracking-tight text-base-content">다운로드 진행</h2>
            <span class="badge badge-neutral badge-sm font-semibold">{progressItems.length}</span>
          {:else}
            <Terminal size={18} class="text-success animate-pulse" />
            <h2 class="text-md font-bold tracking-tight text-base-content">{t.logs}</h2>
            <span class="badge badge-neutral badge-sm font-semibold">{logs.length}</span>
          {/if}
        </div>

        <div class="flex items-center gap-1.5">
          {#if activePanel === 'logs'}
            <button
              class="btn btn-xs btn-outline btn-error gap-1 px-2.5"
              onclick={clearLogs}
              title="로그 비우기"
            >
              <Trash2 size={12} />
              <span>비우기</span>
            </button>
          {/if}
          <button
            class="btn btn-xs btn-circle btn-ghost hover:bg-base-200"
            onclick={closePanel}
            title="닫기"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      <!-- Panel Body -->
      <div
        bind:this={consoleEl}
        class="flex-1 overflow-y-auto bg-base-200/10 select-text"
        class:scrollbar-thin={activePanel === 'logs'}
        class:scrollbar-thumb-base-300={activePanel === 'logs'}
      >
        {#if activePanel === 'progress'}
          <!-- Progress Panel Content -->
          <div class="p-4 space-y-3">
            {#each progressItems as item (item.jobId + ':' + item.streamId)}
              {@const value = progressValue(item)}
              <div class="rounded-xl border border-base-200 bg-base-100 p-3.5 shadow-sm transition-all duration-200 hover:border-base-300">
                <div class="flex items-center justify-between gap-3">
                  <div class="min-w-0">
                    <span class="block truncate text-sm font-bold text-base-content" title={item.title}>
                      {item.title || '작업'}
                    </span>
                    <span class="mt-1 inline-flex rounded bg-base-200 px-2 py-0.5 text-[10px] font-semibold text-base-content/75">
                      {streamLabel(item)}
                    </span>
                  </div>
                  {#if value !== null}
                    <span class="text-xs font-mono tabular-nums font-bold opacity-75">{value}%</span>
                  {/if}
                </div>

                {#if value !== null}
                  <progress class="progress progress-primary h-2 w-full mt-2" value={value} max="100"></progress>
                {/if}

                <div class="mt-2 truncate font-mono text-[11px] text-base-content/70" title={detailText(item)}>
                  {detailText(item) || item.line}
                </div>
              </div>
            {:else}
              <div class="flex flex-col items-center justify-center rounded-xl border border-dashed border-base-300 p-10 text-center bg-base-100/50 my-4">
                <p class="text-sm text-base-content/50">표시할 다운로드 진행이 없습니다.</p>
              </div>
            {/each}
          </div>
        {:else if activePanel === 'logs'}
          <!-- Logs Panel Content (Table-like, matches active theme colors) -->
          <table class="table table-xs table-zebra w-full text-[11px]">
            <thead class="sticky top-0 z-10">
              <tr class="bg-base-200 text-base-content/80 font-bold border-b border-base-200">
                <th class="w-24 text-center font-mono border-r border-base-200/50 bg-base-200 py-2">시간</th>
                <th class="bg-base-200 py-2">로그 내용</th>
              </tr>
            </thead>
            <tbody>
              {#each logs as entry (entry.id)}
                {@const parsed = parseLogLine(entry.line)}
                <tr class="hover:bg-base-200/50 transition-colors align-top border-b border-base-200/40">
                  <td class="font-mono text-center opacity-70 border-r border-base-200/50 py-2">{parsed.time}</td>
                  <td class="whitespace-pre-wrap break-all font-mono py-2">{parsed.content}</td>
                </tr>
              {:else}
                <tr>
                  <td colspan="2" class="opacity-50 text-center py-20 italic">수신된 로그가 없습니다.</td>
                </tr>
              {/each}
            </tbody>
          </table>
        {/if}
      </div>
    </div>
  {/if}

  <!-- Slim Icon Toolbar (Always visible on the right, relative, z-50 to overlap panel animation) -->
  <div class="w-12 h-full bg-base-100 border-l border-base-200/80 flex flex-col items-center py-5 gap-4 select-none z-50 relative">
    <!-- Progress Indicator Button -->
    <button
      class="btn btn-ghost btn-circle w-10 h-10 p-0 flex items-center justify-center relative hover:scale-105 transition-all duration-200"
      class:bg-base-200={activePanel === 'progress'}
      onclick={() => togglePanel('progress')}
      title="다운로드 진행"
    >
      <Activity size={18} class={progressItems.length > 0 ? 'text-primary' : 'text-base-content/75'} />
      {#if progressItems.length > 0}
        <span class="badge badge-secondary badge-sm absolute -top-1 -right-1 font-extrabold shadow-sm scale-90">{progressItems.length}</span>
      {/if}
    </button>

    <!-- Logs Console Toggle Button -->
    <button
      class="btn btn-ghost btn-circle w-10 h-10 p-0 flex items-center justify-center relative hover:scale-105 transition-all duration-200"
      class:bg-base-200={activePanel === 'logs'}
      onclick={() => togglePanel('logs')}
      title="로그 콘솔"
    >
      <Terminal size={18} class="text-base-content/75" />
    </button>
  </div>
</div>
