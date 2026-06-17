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

<div class="rounded-box bg-base-100 p-4 shadow-sm">
  <h2 class="mb-3 text-base font-semibold">{t.generalDownload}</h2>
  <div class="join w-full">
    <input class="input join-item input-bordered w-full" bind:value={downloadUrl} placeholder="https://..." />
    <button class="btn join-item btn-primary" disabled={busy || !downloadUrl.trim()} on:click={handleDownload}>
      <Download size={16} /> {t.download}
    </button>
  </div>
</div>
