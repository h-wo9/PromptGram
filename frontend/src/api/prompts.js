import api from './client'

export function createPrompt(payload) {
  return api.post('/prompts', payload).then((r) => r.data)
}

export function getPrompt(id) {
  return api.get(`/prompts/${id}`).then((r) => r.data)
}

export function updatePrompt(id, payload) {
  return api.patch(`/prompts/${id}`, payload).then((r) => r.data)
}

export function deletePrompt(id) {
  return api.delete(`/prompts/${id}`)
}

export function fetchFeed({ cursor, sort, tag } = {}) {
  return api
    .get('/prompts', { params: { cursor, sort, tag } })
    .then((r) => r.data)
}

export function toggleLike(id) {
  return api.post(`/prompts/${id}/like`).then((r) => r.data)
}

export function toggleBookmark(id) {
  return api.post(`/prompts/${id}/bookmark`).then((r) => r.data)
}

export function increaseCopyCount(id) {
  return api.post(`/prompts/${id}/copy`).then((r) => r.data)
}

export function fetchMyPrompts(params = {}) {
  return api.get('/users/me/prompts', { params }).then((r) => r.data)
}

export function fetchMyBookmarks(params = {}) {
  return api.get('/users/me/bookmarks', { params }).then((r) => r.data)
}
