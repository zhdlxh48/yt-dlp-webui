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
  <tr class="align-middle">
    <td>
      <input class="input input-sm input-bordered w-full font-medium" bind:value={editName} placeholder="채널 이름" />
    </td>
    <td>
      <input class="input input-sm input-bordered w-full font-mono text-xs" bind:value={editHandle} placeholder="@handle" />
    </td>
    <td class="text-center">
      <input type="checkbox" class="checkbox checkbox-sm checkbox-primary" bind:checked={editEnabled} />
    </td>
    <td><span class="text-xs opacity-40">-</span></td>
    <td class="text-right space-x-1.5">
      <button class="btn btn-sm btn-success text-success-content" disabled={busy} on:click={handleSave}>저장</button>
      <button class="btn btn-sm btn-ghost" on:click={onCancelEdit}>취소</button>
    </td>
  </tr>
{:else}
  <tr class="hover:bg-base-200/40 transition-colors align-middle">
    <td class="font-semibold text-base-content">{channel.name || '-'}</td>
    <td class="font-mono text-xs opacity-75">{channel.handle || '-'}</td>
    <td>
      <span class="badge badge-sm font-semibold transition-all" class:badge-success={channel.enabled} class:badge-ghost={!channel.enabled} class:opacity-60={!channel.enabled}>
        {channel.enabled ? 'ON' : 'OFF'}
      </span>
    </td>
    <td>
      {#if activeJob}
        <span class="badge badge-success badge-sm gap-1.5 font-bold animate-pulse text-success-content border-none shadow-sm shadow-success/25">
          <span class="size-1.5 rounded-full bg-white"></span>
          녹화 중
        </span>
      {:else}
        <span class="badge badge-ghost badge-sm opacity-60 text-xs font-medium">대기</span>
      {/if}
    </td>
    <td class="text-right space-x-1.5">
      <button
        class="btn btn-sm transition-all duration-200 shadow-sm"
        class:btn-primary={!activeJob}
        class:btn-error={activeJob}
        class:btn-outline={!activeJob}
        disabled={busy || installedCount < 1}
        on:click={() => onToggleMonitoring(channel)}
      >
        {activeJob ? '정지' : '감시'}
      </button>
      <button
        class="btn btn-sm btn-ghost hover:bg-base-200/80"
        disabled={busy || !!activeJob}
        on:click={() => onStartEdit(channel)}
      >
        수정
      </button>
      <button
        class="btn btn-sm btn-ghost text-error hover:bg-error/10"
        disabled={busy || !!activeJob}
        on:click={() => onDelete(channel.id)}
      >
        삭제
      </button>
    </td>
  </tr>
{/if}
