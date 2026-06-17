/**
 * 유튜브 라이브 채널의 핸들명에 '@' 기호가 없을 경우 자동으로 접두사로 추가해 줍니다.
 * @param handle 유튜브 채널 핸들명
 */
export function formatYoutubeHandle(handle: string): string {
  const trimmed = handle.trim()
  if (!trimmed) return ''
  return trimmed.startsWith('@') ? trimmed : '@' + trimmed
}
