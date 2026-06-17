<script lang="ts">
  import { Play } from '@lucide/svelte'
  import type { Settings, JobInfo, LiveChannel } from '@/types'
  import { ko as t } from '@/i18n/ko'
  import { formatYoutubeHandle } from '@/utils/youtube'
  import ChannelRow from './ChannelRow.svelte'

  export let settings: Settings | null
  export let jobs: JobInfo[]
  export let busy: boolean
  export let installedCount: number

  // 부모 콜백
  export let onStartLive: () => Promise<void>
  export let onAddChannel: (name: string, handle: string) => Promise<void>
  export let onEditChannel: (id: string, name: string, handle: string, enabled: boolean) => Promise<void>
  export let onDeleteChannel: (id: string) => Promise<void>
  export let onToggleMonitoring: (channel: LiveChannel) => Promise<void>

  // 추가 및 편집을 위한 로컬 상태
  let isAdding = false
  let newName = ''
  let newHandle = ''
  let editingChannelId: string | null = null

  function startAddChannel() {
    isAdding = true
    newName = ''
    newHandle = ''
  }

  function cancelAddChannel() {
    isAdding = false
  }

  async function handleAddChannel() {
    const handle = formatYoutubeHandle(newHandle)
    if (!handle) return
    await onAddChannel(newName.trim(), handle)
    isAdding = false
  }

  function startEditChannel(channel: LiveChannel) {
    editingChannelId = channel.id
  }

  function cancelEditChannel() {
    editingChannelId = null
  }

  async function handleEditChannel(id: string, name: string, handle: string, enabled: boolean) {
    await onEditChannel(id, name, handle, enabled)
    editingChannelId = null
  }
</script>

<div class="card bg-base-100 border border-base-200/50 shadow-sm transition-all duration-200 hover:shadow-md">
  <div class="card-body p-5 lg:p-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <div class="flex items-center gap-2">
        <h2 class="card-title text-lg font-bold tracking-tight text-base-content">{t.liveChannels}</h2>
        <span class="badge badge-neutral badge-sm font-semibold">{settings?.live.channels.length || 0}</span>
      </div>
      <div class="flex items-center gap-2">
        <button class="btn btn-sm btn-outline btn-secondary gap-1.5" disabled={busy || isAdding} on:click={startAddChannel}>
          + 채널 추가
        </button>
        <button class="btn btn-sm btn-primary gap-1.5" disabled={busy || installedCount < 1} on:click={onStartLive}>
          <Play size={14} class="fill-current" /> 전체 감시 시작
        </button>
      </div>
    </div>

    {#if (settings?.live.channels.length || isAdding)}
      <div class="overflow-x-auto rounded-lg border border-base-200/60">
        <table class="table table-zebra table-md w-full">
          <thead>
            <tr class="bg-base-200/50 text-base-content/70">
              <th>이름</th>
              <th>유튜브 핸들</th>
              <th>사용 여부</th>
              <th>상태</th>
              <th class="text-right">작업</th>
            </tr>
          </thead>
          <tbody>
            {#each settings?.live.channels || [] as channel}
              <ChannelRow
                {channel}
                {jobs}
                {busy}
                {installedCount}
                isEditing={editingChannelId === channel.id}
                onSaveEdit={handleEditChannel}
                onCancelEdit={cancelEditChannel}
                onStartEdit={startEditChannel}
                onDelete={onDeleteChannel}
                onToggleMonitoring={onToggleMonitoring}
              />
            {/each}

            {#if isAdding}
              <tr class="bg-base-200/30">
                <td>
                  <input class="input input-sm input-bordered w-full" bind:value={newName} placeholder="채널 이름" />
                </td>
                <td>
                  <input class="input input-sm input-bordered w-full" bind:value={newHandle} placeholder="@handle" />
                </td>
                <td>
                  <span class="text-xs opacity-60">ON</span>
                </td>
                <td>-</td>
                <td class="text-right space-x-1.5">
                  <button class="btn btn-sm btn-success text-success-content" disabled={busy} on:click={handleAddChannel}>저장</button>
                  <button class="btn btn-sm btn-ghost" on:click={cancelAddChannel}>취소</button>
                </td>
              </tr>
            {/if}
          </tbody>
        </table>
      </div>
    {:else}
      <div class="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-base-300 p-10 text-center bg-base-50/20">
        <p class="mb-4 text-sm text-base-content/60">등록된 라이브 채널이 없습니다. 채널을 추가하여 감시를 시작하세요.</p>
        <button class="btn btn-md btn-primary px-6" on:click={startAddChannel}>첫 채널 추가하기</button>
      </div>
    {/if}
  </div>
</div>
