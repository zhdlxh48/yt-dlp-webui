<script lang="ts">
  import { Terminal, Trash2, X } from '@lucide/svelte'
  import { afterUpdate } from 'svelte'
  import { fly } from 'svelte/transition'
  import { ko as t } from '@/i18n/ko'
  import { clearLogs } from '@/stores/events'
  import type { LogEntry } from '@/types'

  export let logs: LogEntry[]

  let isOpen = false
  let consoleEl: HTMLDivElement

  afterUpdate(() => {
    if (isOpen && consoleEl) {
      consoleEl.scrollTo({
        top: consoleEl.scrollHeight,
        behavior: 'smooth',
      })
    }
  })
</script>

<!-- Floating Toggle Button -->
<button
  class="fixed bottom-6 right-6 z-50 btn btn-square btn-secondary shadow-xl hover:scale-105 transition-all duration-200"
  on:click={() => (isOpen = !isOpen)}
  title="로그 콘솔"
  aria-label="Toggle log console"
>
  {#if isOpen}
    <X size={20} />
  {:else}
    <Terminal size={20} />
  {/if}
</button>

<!-- Fly-out Log Panel -->
{#if isOpen}
  <div
    transition:fly={{ y: 50, duration: 300 }}
    class="card bg-slate-950 border border-slate-800 text-slate-100 shadow-2xl fixed bottom-24 right-6 w-[480px] max-w-[calc(100vw-3rem)] h-[480px] z-40 flex flex-col overflow-hidden"
  >
    <div class="card-body p-4 flex flex-col h-full overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between gap-2 border-b border-slate-800 pb-3 mb-4 flex-shrink-0">
        <div class="flex items-center gap-2 text-slate-300">
          <Terminal size={18} class="text-success animate-pulse" />
          <h2 class="text-md font-bold font-mono tracking-tight">{t.logs}</h2>
          <span class="badge badge-sm badge-ghost font-mono opacity-60">{logs.length}</span>
        </div>
        
        <div class="flex items-center gap-2">
          <!-- Clear Button -->
          <button
            class="btn btn-xs btn-outline btn-error gap-1"
            on:click={clearLogs}
            title="로그 비우기"
          >
            <Trash2 size={12} />
            <span>비우기</span>
          </button>
          
          <!-- Close Button -->
          <button
            class="btn btn-xs btn-circle btn-ghost text-slate-400 hover:text-white"
            on:click={() => (isOpen = false)}
            title="닫기"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      <!-- Console Scroll Area -->
      <div
        bind:this={consoleEl}
        class="flex-1 space-y-1.5 overflow-y-auto font-mono text-xs text-slate-300/90 leading-relaxed pr-1 select-text scrollbar-thin scrollbar-thumb-slate-800"
      >
        {#each logs as entry (entry.id)}
          <p
            class="log-line whitespace-pre-wrap break-all hover:bg-slate-900/50 px-1 py-0.5 rounded transition-colors"
          >
            <span class="text-success/70 mr-1.5">$&gt;</span>{entry.line}
          </p>
        {:else}
          <p class="opacity-50 text-center py-20 italic">수신된 로그가 없습니다.</p>
        {/each}
      </div>
    </div>
  </div>
{/if}
