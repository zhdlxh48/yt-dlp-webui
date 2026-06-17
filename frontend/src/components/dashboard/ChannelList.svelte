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

<div class="rounded-box bg-base-100 p-4 shadow-sm">
  <div class="mb-3 flex items-center justify-between gap-4">
    <h2 class="text-base font-semibold">{t.liveChannels}</h2>
    <div class="flex items-center gap-2">
      <button class="btn btn-xs btn-outline" disabled={busy || isAdding} on:click={startAddChannel}>
        채널 추가
      </button>
      <button class="btn btn-xs btn-primary" disabled={busy || installedCount < 1} on:click={onStartLive}>
        <Play size={12} /> 전체 감시 시작
      </button>
    </div>
  </div>

  {#if (settings?.live.channels.length || isAdding)}
    <div class="overflow-x-auto">
      <table class="table table-sm w-full">
        <thead>
          <tr>
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
            <tr class="bg-base-200">
              <td>
                <input class="input input-xs input-bordered w-full" bind:value={newName} placeholder="채널 이름" />
              </td>
              <td>
                <input class="input input-xs input-bordered w-full" bind:value={newHandle} placeholder="@handle" />
              </td>
              <td>
                <span class="text-xs opacity-60">ON</span>
              </td>
              <td>-</td>
              <td class="text-right space-x-1">
                <button class="btn btn-xs btn-success" disabled={busy} on:click={handleAddChannel}>저장</button>
                <button class="btn btn-xs btn-ghost" on:click={cancelAddChannel}>취소</button>
              </td>
            </tr>
          {/if}
        </tbody>
      </table>
    </div>
  {:else}
    <div class="rounded border border-dashed border-base-300 p-8 text-center text-sm opacity-70">
      <p class="mb-2">등록된 채널이 없습니다.</p>
      <button class="btn btn-sm btn-primary" on:click={startAddChannel}>채널 추가하기</button>
    </div>
  {/if}
</div>
