/** "방금 전 / n분 전 / n시간 전 / n일 전 / 날짜" 상대 시간 표기 */
export function timeAgo(iso) {
  const then = new Date(iso)
  const diffSec = Math.max(0, (Date.now() - then.getTime()) / 1000)
  if (diffSec < 60) return '방금 전'
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}분 전`
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}시간 전`
  if (diffSec < 86400 * 7) return `${Math.floor(diffSec / 86400)}일 전`
  return then.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
}
