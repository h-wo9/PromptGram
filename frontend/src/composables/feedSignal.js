// keep-alive된 FeedView에게 "데이터가 바뀌었으니 다시 불러라"를 알리는 플래그.
// 뒤로가기(스크롤 복원)는 캐시를 유지하고, 게시/수정/삭제 후에만 새로고침한다.
export const feedStale = { value: false }
