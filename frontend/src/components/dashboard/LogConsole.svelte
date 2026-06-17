<script lang="ts">
  import { Plug } from '@lucide/svelte'
  import { ko as t } from '@/i18n/ko'

  export let logs: string[]
</script>

<div class="rounded-box bg-neutral p-4 text-neutral-content shadow-sm">
  <div class="mb-3 flex items-center gap-2">
    <Plug size={16} />
    <h2 class="text-base font-semibold">{t.logs}</h2>
  </div>
  <div class="max-h-[480px] space-y-1 overflow-y-auto font-mono text-xs">
    {#each logs as line}
      <p class="log-line">{line}</p>
    {:else}
      <p class="opacity-60">로그 대기 중</p>
    {/each}
  </div>
</div>
