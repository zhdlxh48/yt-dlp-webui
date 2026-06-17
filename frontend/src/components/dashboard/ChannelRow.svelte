<script lang="ts">
  import type { LiveChannel, JobInfo } from '@/types'
  import { formatYoutubeHandle } from '@/utils/youtube'

  export let channel: LiveChannel
  export let jobs: JobInfo[]
  export let busy: boolean
  export let installedCount: number
  export let isEditing: boolean

  // 부모 콜백 함수
  export let onSaveEdit: (id: string, name: string, handle: string, enabled: boolean) => Promise<void>
  export let onCancelEdit: () => void
  export let onStartEdit: (channel: LiveChannel) => void
  export let onDelete: (id: string) => Promise<void>
  export let onToggleMonitoring: (channel: LiveChannel) => Promise<void>

  // 수정 중인 임시 로컬 상태
  let editName = ''
  let editHandle = ''
  let editEnabled = true

  // 수정 모드가 활성화되면 값을 동기화합니다.
  $: if (isEditing) {
    editName = channel.name
    editHandle = channel.handle || ''
    editEnabled = channel.enabled
  }

  // 이 채널에 대해 활성화된 작업(모니터링)이 있는지 확인합니다.
  $: activeJob = jobs.find(
    (job) => job.channel_id === channel.id && ['starting', 'running', 'stopping'].includes(job.status)
  )

  async function handleSave() {
    const handle = formatYoutubeHandle(editHandle)
    if (!handle) return
    await onSaveEdit(channel.id, editName.trim(), handle, editEnabled)
  }
</script>

{#if isEditing}
  <tr>
    <td>
      <input class="input input-xs input-bordered w-full" bind:value={editName} placeholder="채널 이름" />
    </td>
    <td>
      <input class="input input-xs input-bordered w-full" bind:value={editHandle} placeholder="@handle" />
    </td>
    <td>
      <input type="checkbox" class="checkbox checkbox-xs" bind:checked={editEnabled} />
    </td>
    <td>-</td>
    <td class="text-right space-x-1">
      <button class="btn btn-xs btn-success" disabled={busy} on:click={handleSave}>저장</button>
      <button class="btn btn-xs btn-ghost" on:click={onCancelEdit}>취소</button>
    </td>
  </tr>
{:else}
  <tr>
    <td class="font-medium">{channel.name || '-'}</td>
    <td class="text-xs opacity-80">{channel.handle || '-'}</td>
    <td>
      <span class="badge badge-sm" class:badge-success={channel.enabled} class:badge-ghost={!channel.enabled}>
        {channel.enabled ? 'ON' : 'OFF'}
      </span>
    </td>
    <td>
      {#if activeJob}
        <span class="badge badge-success badge-xs gap-1 animate-pulse">
          <span class="size-1 rounded-full bg-white"></span>
          감시 중
        </span>
      {:else}
        <span class="opacity-60 text-xs">대기</span>
      {/if}
    </td>
    <td class="text-right space-x-1">
      <button
        class="btn btn-xs"
        class:btn-primary={!activeJob}
        class:btn-error={activeJob}
        disabled={busy || installedCount < 1}
        on:click={() => onToggleMonitoring(channel)}
      >
        {activeJob ? '정지' : '감시 시작'}
      </button>
      <button
        class="btn btn-xs btn-outline"
        disabled={busy || !!activeJob}
        on:click={() => onStartEdit(channel)}
      >
        수정
      </button>
      <button
        class="btn btn-xs btn-ghost text-error"
        disabled={busy || !!activeJob}
        on:click={() => onDelete(channel.id)}
      >
        삭제
      </button>
    </td>
  </tr>
{/if}
