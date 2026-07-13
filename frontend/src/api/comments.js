import api from './client'

export function fetchComments(promptId) {
  return api.get(`/prompts/${promptId}/comments`).then((r) => r.data)
}

export function createComment(promptId, content) {
  return api.post(`/prompts/${promptId}/comments`, { content }).then((r) => r.data)
}

export function updateComment(commentId, content) {
  return api.patch(`/comments/${commentId}`, { content }).then((r) => r.data)
}

export function deleteComment(commentId) {
  return api.delete(`/comments/${commentId}`)
}
