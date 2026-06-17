<script lang="ts">
  import { Terminal } from '@lucide/svelte'
  import { ko as t } from '@/i18n/ko'
  import { afterUpdate } from 'svelte'

  export let logs: string[]

  let consoleEl: HTMLDivElement

  afterUpdate(() => {
    if (consoleEl) {
      consoleEl.scrollTo({
        top: consoleEl.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
</script>

<div class="card bg-slate-950 border border-slate-800 text-slate-100 shadow-lg">
  <div class="card-body p-5 lg:p-6 flex flex-col h-[520px]">
    <div class="flex items-center justify-between gap-2 border-b border-slate-800 pb-3 mb-4">
      <div class="flex items-center gap-2 text-slate-300">
        <Terminal size={18} class="text-success" />
        <h2 class="text-md font-bold font-mono tracking-tight">{t.logs}</h2>
      </div>
      <div class="flex gap-1.5">
        <span class="size-2.5 rounded-full bg-error/40"></span>
        <span class="size-2.5 rounded-full bg-warning/40"></span>
        <span class="size-2.5 rounded-full bg-success/40"></span>
      </div>
    </div>
    
    <div
      bind:this={consoleEl}
      class="flex-1 space-y-1.5 overflow-y-auto font-mono text-xs text-slate-300/90 leading-relaxed pr-1 select-text scrollbar-thin scrollbar-thumb-slate-800"
    >
      {#each logs as line}
        <p class="log-line whitespace-pre-wrap break-all hover:bg-slate-900/50 px-1 py-0.5 rounded transition-colors">
          <span class="text-success/70 mr-1.5">$&gt;</span>{line}
        </p>
      {:else}
        <p class="opacity-50 text-center py-20 italic">수신된 로그가 없습니다.</p>
      {/each}
    </div>
  </div>
</div>
