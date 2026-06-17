<script lang="ts">
  import { Save } from '@lucide/svelte'
  import type { Settings } from '@/types'
  import { ko as t } from '@/i18n/ko'

  export let settings: Settings
  export let busy: boolean

  // 부모 콜백 함수
  export let onSave: () => Promise<void>
</script>

<div class="rounded-box bg-base-100 p-4 shadow-sm">
  <div class="mb-3 flex items-center justify-between">
    <h2 class="text-base font-semibold">{t.settings}</h2>
    <button class="btn btn-sm btn-primary" disabled={busy} on:click={onSave}>
      <Save size={16} /> {t.save}
    </button>
  </div>
  <div class="grid gap-3">
    <label class="form-control">
      <span class="label-text">{t.downloadsDir}</span>
      <input class="input input-bordered" bind:value={settings.paths.downloads_dir} />
    </label>
    <label class="form-control">
      <span class="label-text">cookies.txt</span>
      <input class="input input-bordered" bind:value={settings.auth.cookies_file} />
    </label>
    <label class="form-control">
      <span class="label-text">Format</span>
      <input class="input input-bordered" bind:value={settings.download.format_selector} />
    </label>
    <label class="form-control">
      <span class="label-text">Extra yt-dlp args</span>
      <textarea class="textarea textarea-bordered min-h-24" bind:value={settings.download.extra_args}></textarea>
    </label>
    <div class="grid gap-2 md:grid-cols-2">
      <label class="label cursor-pointer justify-start gap-3">
        <input class="toggle toggle-primary" type="checkbox" bind:checked={settings.app.open_browser_on_start} />
        <span class="label-text">시작 시 브라우저 열기</span>
      </label>
      <label class="label cursor-pointer justify-start gap-3">
        <input class="toggle toggle-primary" type="checkbox" bind:checked={settings.app.start_monitoring_on_launch} />
        <span class="label-text">앱 시작 시 감시</span>
      </label>
      <label class="label cursor-pointer justify-start gap-3">
        <input class="toggle toggle-primary" type="checkbox" bind:checked={settings.tools.auto_install_tools} />
        <span class="label-text">도구 자동 설치</span>
      </label>
      <label class="label cursor-pointer justify-start gap-3">
        <input class="toggle toggle-primary" type="checkbox" bind:checked={settings.startup.enabled} />
        <span class="label-text">로그인 시 자동 실행</span>
      </label>
    </div>
  </div>
</div>
