<script lang="ts">
  import type { FileInfo } from '@/types'
  import { ko as t } from '@/i18n/ko'
  import { formatSize } from '@/utils/format'
  import { FileVideo, Clock, HardDrive } from '@lucide/svelte'

  export let files: FileInfo[]
</script>

<div class="card bg-base-100 border border-base-200/50 shadow-sm transition-all duration-200 hover:shadow-md">
  <div class="card-body p-5 lg:p-6">
    <div class="flex items-center justify-between border-b border-base-200/60 pb-3 mb-4">
      <div class="flex items-center gap-2">
        <h2 class="card-title text-lg font-bold tracking-tight text-base-content">{t.files}</h2>
        <span class="badge badge-neutral badge-sm font-semibold">{files.length}</span>
      </div>
    </div>

    <p class="text-sm opacity-70 mb-4">다운로드 완료 폴더 내에 저장된 녹화 및 비디오 파일 목록입니다.</p>

    {#if files.length > 0}
      <div class="overflow-x-auto rounded-lg border border-base-200/60">
        <table class="table table-zebra table-md w-full">
          <thead>
            <tr class="bg-base-200/50 text-base-content/70">
              <th class="min-w-[150px]">파일명</th>
              <th class="w-24 whitespace-nowrap">크기</th>
              <th class="w-48 whitespace-nowrap">다운로드 일시</th>
              <th class="min-w-[180px]">저장 경로</th>
            </tr>
          </thead>
          <tbody>
            {#each files as file}
              <tr class="hover:bg-base-200/40 transition-colors align-middle">
                <td class="max-w-[150px] sm:max-w-xs md:max-w-md">
                  <div class="flex items-center gap-2.5">
                    <FileVideo size={16} class="text-primary shrink-0" />
                    <span class="font-medium truncate block" title={file.name}>
                      {file.name}
                    </span>
                  </div>
                </td>
                <td class="w-24 whitespace-nowrap font-mono text-sm font-medium">
                  {formatSize(file.size)}
                </td>
                <td class="w-48 whitespace-nowrap text-xs opacity-75">
                  <div class="flex items-center gap-1.5 font-mono">
                    <Clock size={12} class="opacity-60" />
                    {new Date(file.modified_at).toLocaleString('ko-KR')}
                  </div>
                </td>
                <td class="max-w-[180px] md:max-w-xs truncate font-mono text-xs opacity-60" title={file.path}>
                  <div class="flex items-center gap-1.5">
                    <HardDrive size={12} class="opacity-60 shrink-0" />
                    <span class="truncate">{file.path}</span>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <div class="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-base-300 p-12 text-center bg-base-50/20">
        <p class="text-sm text-base-content/50">다운로드된 파일이 아직 존재하지 않습니다.</p>
      </div>
    {/if}
  </div>
</div>
