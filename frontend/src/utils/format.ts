/**
 * 파일 바이트(Byte) 크기를 더 직관적인 단위(KB, MB, GB)의 문자열로 변환합니다.
 * @param size 파일 바이트 크기
 */
export function formatSize(size: number): string {
  if (size < 1024) return `${size} B`
  if (size < 1024 ** 2) return `${(size / 1024).toFixed(1)} KB`
  if (size < 1024 ** 3) return `${(size / 1024 ** 2).toFixed(1)} MB`
  return `${(size / 1024 ** 3).toFixed(2)} GB`
}
