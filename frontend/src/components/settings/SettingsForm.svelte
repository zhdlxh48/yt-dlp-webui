<script lang="ts">
  import { Save } from '@lucide/svelte'
  import type { Settings } from '@/types'
  import { ko as t } from '@/i18n/ko'

  export let settings: Settings
  export let busy: boolean

  // 부모 콜백 함수
  export let onSave: () => Promise<void>
</script>

<div class="card bg-base-100 border border-base-200/50 shadow-sm transition-all duration-200 hover:shadow-md">
  <div class="card-body p-5 lg:p-6">
    <div class="flex items-center justify-between border-b border-base-200/60 pb-3 mb-6">
      <h2 class="card-title text-lg font-bold tracking-tight text-base-content">{t.settings}</h2>
      <button class="btn btn-sm btn-primary gap-1.5 font-semibold shadow-sm" disabled={busy} on:click={onSave}>
        {#if busy}
          <span class="loading loading-spinner loading-xs"></span>
        {:else}
          <Save size={14} />
        {/if}
        {t.save}
      </button>
    </div>

    <div class="space-y-6">
      <!-- Section 1: Paths & Authentication -->
      <div>
        <h3 class="text-sm font-extrabold tracking-tight text-base-content border-l-4 border-primary pl-3 mb-4 uppercase">
          경로 및 인증 설정
        </h3>
        <div class="grid gap-4 grid-cols-[repeat(auto-fit,minmax(240px,1fr))]">
          <label class="form-control w-full">
            <span class="label-text font-semibold text-base-content/80 mb-1">{t.downloadsDir}</span>
            <input class="input input-bordered w-full focus:input-primary text-sm font-mono" bind:value={settings.paths.downloads_dir} placeholder="C:\downloads" />
          </label>
          <label class="form-control w-full">
            <span class="label-text font-semibold text-base-content/80 mb-1">cookies.txt 파일 경로</span>
            <input class="input input-bordered w-full focus:input-primary text-sm font-mono" bind:value={settings.auth.cookies_file} placeholder="선택 사항" />
          </label>
        </div>
      </div>

      <div class="divider my-1"></div>

      <!-- Section 2: Download Options -->
      <div>
        <h3 class="text-sm font-extrabold tracking-tight text-base-content border-l-4 border-primary pl-3 mb-4 uppercase">
          다운로드 상세 설정
        </h3>
        <div class="grid gap-4 grid-cols-[repeat(auto-fit,minmax(240px,1fr))]">
          <label class="form-control w-full">
            <span class="label-text font-semibold text-base-content/80 mb-1">yt-dlp 추가 아규먼트 (줄바꿈 구분)</span>
            <textarea class="textarea textarea-bordered focus:textarea-primary text-sm font-mono min-h-24 w-full" bind:value={settings.download.extra_args} placeholder="--no-part&#10;--no-mtime"></textarea>
          </label>
          <label class="form-control w-full">
            <span class="label-text font-semibold text-base-content/80 mb-1">yt-dlp 포맷 셀렉터</span>
            <input class="input input-bordered w-full focus:input-primary text-sm font-mono" bind:value={settings.download.format_selector} />
            <div class="label py-1">
              <span class="label-text-alt opacity-65">기본값: bestvideo+bestaudio/best</span>
            </div>
          </label>
        </div>
      </div>

      <div class="divider my-1"></div>

      <!-- Section 3: App Behavior -->
      <div>
        <h3 class="text-sm font-extrabold tracking-tight text-base-content border-l-4 border-primary pl-3 mb-4 uppercase">
          애플리케이션 환경 설정
        </h3>
        <div class="grid gap-3 grid-cols-[repeat(auto-fit,minmax(280px,1fr))]">
          <label class="label cursor-pointer justify-start gap-4 rounded-xl border border-base-200/50 hover:bg-base-200/20 p-3 transition-colors">
            <input class="toggle toggle-primary toggle-sm shrink-0" type="checkbox" bind:checked={settings.app.open_browser_on_start} />
            <div class="flex flex-col min-w-0">
              <span class="label-text font-semibold">시작 시 브라우저 열기</span>
              <span class="text-xs opacity-60 mt-0.5 whitespace-pre-wrap">서버 구동 시 WebUI 화면을 브라우저에 표시합니다.</span>
            </div>
          </label>

          <label class="label cursor-pointer justify-start gap-4 rounded-xl border border-base-200/50 hover:bg-base-200/20 p-3 transition-colors">
            <input class="toggle toggle-primary toggle-sm shrink-0" type="checkbox" bind:checked={settings.app.start_monitoring_on_launch} />
            <div class="flex flex-col min-w-0">
              <span class="label-text font-semibold">앱 시작 시 감시 자동 시작</span>
              <span class="text-xs opacity-60 mt-0.5 whitespace-pre-wrap">프로그램 실행 시 라이브 모니터링을 자동으로 개시합니다.</span>
            </div>
          </label>

          <label class="label cursor-pointer justify-start gap-4 rounded-xl border border-base-200/50 hover:bg-base-200/20 p-3 transition-colors">
            <input class="toggle toggle-primary toggle-sm shrink-0" type="checkbox" bind:checked={settings.tools.auto_install_tools} />
            <div class="flex flex-col min-w-0">
              <span class="label-text font-semibold">필수 도구 자동 업데이트</span>
              <span class="text-xs opacity-60 mt-0.5 whitespace-pre-wrap">필요 시 도구를 백그라운드에서 자동 설치합니다.</span>
            </div>
          </label>

          <label class="label cursor-pointer justify-start gap-4 rounded-xl border border-base-200/50 hover:bg-base-200/20 p-3 transition-colors">
            <input class="toggle toggle-primary toggle-sm shrink-0" type="checkbox" bind:checked={settings.startup.enabled} />
            <div class="flex flex-col min-w-0">
              <span class="label-text font-semibold">윈도우 시작 시 자동 실행</span>
              <span class="text-xs opacity-60 mt-0.5 whitespace-pre-wrap">윈도우 로그인 시 트레이 앱으로 즉시 자동 구동합니다.</span>
            </div>
          </label>
        </div>
      </div>
    </div>
  </div>
</div>
