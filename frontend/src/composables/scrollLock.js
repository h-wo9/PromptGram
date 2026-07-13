// 스크롤 잠금 시 스크롤바가 사라지며 레이아웃이 옆으로 밀리는 것을
// 스크롤바 폭만큼 padding-right로 보정한다.
export function lockScroll() {
  const html = document.documentElement
  if (html.style.overflow === 'hidden') return
  const scrollbarWidth = window.innerWidth - html.clientWidth
  html.style.overflow = 'hidden'
  if (scrollbarWidth > 0) html.style.paddingRight = `${scrollbarWidth}px`
}

export function unlockScroll() {
  const html = document.documentElement
  html.style.overflow = ''
  html.style.paddingRight = ''
}
