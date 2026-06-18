<script lang="ts">
  import type { JobInfo, LiveChannel } from '@/types'
  import { formatYoutubeHandle } from '@/utils/youtube'

  export let channel: LiveChannel
  export let jobs: JobInfo[]
  export let busy: boolean
  export let installedCount: number
  export let isEditing: boolean

  export let onSaveEdit: (id: string, name: string, handle: string, enabled: boolean) => Promise<void>
  export let onCancelEdit: () => void
  export let onStartEdit: (channel: LiveChannel) => void
  export let onDelete: (id: string) => Promise<void>
  export let onToggleMonitoring: (channel: LiveChannel, force?: boolean) => Promise<void>

  let editName = ''
  let editHandle = ''
  let editEnabled = true

  $: if (isEditing) {
    editName = channel.name
    editHandle = channel.handle || ''
    editEnabled = channel.enabled
  }

  $: activeJob = jobs.find(
    (job) => job.channel_id === channel.id && ['starting', 'running', 'stopping'].includes(job.status)
  )
  $: isStopping = activeJob?.status === 'stopping'

  async function handleSave() {
    const handle = formatYoutubeHandle(editHandle)
    if (!handle) return
    await onSaveEdit(channel.id, editName.trim(), handle, editEnabled)
  }
</script>

{#if isEditing}
  <tr class="align-middle">
    <td class="whitespace-nowrap">
      <input class="input input-sm input-bordered w-full font-medium" bind:value={editName} placeholder="채널 이름" />
    </td>
    <td class="whitespace-nowrap">
      <input class="input input-sm input-bordered w-full font-mono text-xs" bind:value={editHandle} placeholder="@handle" />
    </td>
    <td class="text-center whitespace-nowrap">
      <input type="checkbox" class="checkbox checkbox-sm checkbox-primary" bind:checked={editEnabled} />
    </td>
    <td class="text-center whitespace-nowrap"><span class="text-xs opacity-40">-</span></td>
    <td class="text-right whitespace-nowrap space-x-1.5">
      <button class="btn btn-sm btn-success text-success-content" disabled={busy} on:click={handleSave}>저장</button>
      <button class="btn btn-sm btn-ghost" on:click={onCancelEdit}>취소</button>
    </td>
  </tr>
{:else}
  <tr class="hover:bg-base-200/40 transition-colors align-middle">
    <td class="font-semibold text-base-content max-w-[150px] truncate">{channel.name || '-'}</td>
    <td class="font-mono text-xs opacity-75 whitespace-nowrap">{channel.handle || '-'}</td>
    <td class="text-center whitespace-nowrap">
      <span class="badge badge-sm font-semibold transition-all" class:badge-success={channel.enabled} class:badge-ghost={!channel.enabled} class:opacity-60={!channel.enabled}>
        {channel.enabled ? 'ON' : 'OFF'}
      </span>
    </td>
    <td class="text-center whitespace-nowrap">
      {#if activeJob}
        {@const isDownloading = activeJob.is_downloading}
        <span
          class="badge badge-sm gap-1.5 font-bold border-none shadow-sm"
          class:badge-success={!isStopping && isDownloading}
          class:badge-info={!isStopping && !isDownloading}
          class:badge-warning={isStopping}
          class:animate-pulse={!isStopping}
        >
          <span class="size-1.5 rounded-full bg-current"></span>
          {isStopping ? '종료 중' : (isDownloading ? '녹화 중' : '감시 중')}
        </span>
      {:else}
        <span class="badge badge-ghost badge-sm opacity-60 text-xs font-medium">대기</span>
      {/if}
    </td>
    <td class="text-right whitespace-nowrap space-x-1.5">
      {#if activeJob}
        <div class="inline-flex gap-1 align-middle">
          <button
            class="btn btn-xs btn-error btn-outline shadow-sm"
            disabled={busy || installedCount < 1 || isStopping}
            on:click={() => onToggleMonitoring(channel, false)}
            title="ffmpeg 병합을 기다리는 안전 종료"
          >
            종료
          </button>
          <button
            class="btn btn-xs btn-error shadow-sm"
            disabled={busy || installedCount < 1}
            on:click={() => onToggleMonitoring(channel, true)}
            title="프로세스 트리를 즉시 종료"
          >
            강제 종료
          </button>
        </div>
      {:else}
        <button
          class="btn btn-sm btn-outline btn-primary transition-all duration-200 shadow-sm"
          disabled={busy || installedCount < 1}
          on:click={() => onToggleMonitoring(channel, false)}
        >
          감시
        </button>
      {/if}
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
