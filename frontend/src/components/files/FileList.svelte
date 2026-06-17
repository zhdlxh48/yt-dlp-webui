<script lang="ts">
  import type { FileInfo } from '@/types'
  import { ko as t } from '@/i18n/ko'
  import { formatSize } from '@/utils/format'

  export let files: FileInfo[]
</script>

<div class="rounded-box bg-base-100 p-4 shadow-sm">
  <h2 class="mb-3 text-base font-semibold">{t.files}</h2>
  <div class="overflow-x-auto">
    <table class="table table-sm">
      <thead>
        <tr>
          <th>파일</th>
          <th>크기</th>
          <th>수정</th>
          <th>경로</th>
        </tr>
      </thead>
      <tbody>
        {#each files as file}
          <tr>
            <td>{file.name}</td>
            <td>{formatSize(file.size)}</td>
            <td>{new Date(file.modified_at).toLocaleString()}</td>
            <td class="max-w-[360px] truncate" title={file.path}>{file.path}</td>
          </tr>
        {:else}
          <tr>
            <td colspan="4" class="opacity-70">파일 없음</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
