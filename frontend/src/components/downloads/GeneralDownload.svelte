<script lang="ts">
  import { Download } from '@lucide/svelte'
  import { ko as t } from '@/i18n/ko'

  export let busy: boolean

  // 부모 콜백 함수
  export let onDownload: (url: string) => Promise<void>

  // 입력 URL 로컬 상태
  let downloadUrl = ''

  async function handleDownload() {
    const url = downloadUrl.trim()
    if (!url) return
    await onDownload(url)
    downloadUrl = ''
  }
</script>

<div class="card bg-base-100 border border-base-200/50 shadow-sm transition-all duration-200 hover:shadow-md">
  <div class="card-body p-5 lg:p-6">
    <h2 class="card-title text-lg font-bold tracking-tight text-base-content mb-1">{t.generalDownload}</h2>
    <p class="text-sm opacity-70 mb-4">유튜브 영상 또는 재생목록 URL을 입력하여 바로 다운로드합니다.</p>
    <div class="join w-full shadow-sm">
      <input class="input join-item input-bordered w-full focus:outline-primary font-mono text-sm" bind:value={downloadUrl} placeholder="https://www.youtube.com/watch?v=..." />
      <button class="btn join-item btn-primary gap-1.5 px-6 font-semibold" disabled={busy || !downloadUrl.trim()} on:click={handleDownload}>
        <Download size={16} /> {t.download}
      </button>
    </div>
  </div>
</div>
