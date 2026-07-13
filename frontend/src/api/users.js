import api from './client'

export function fetchUserProfile(id) {
  return api.get(`/users/${id}`).then((r) => r.data)
}

export function fetchUserPrompts(id) {
  return api.get(`/users/${id}/prompts`).then((r) => r.data)
}

export function toggleFollow(id) {
  return api.post(`/users/${id}/follow`).then((r) => r.data)
}

export function fetchFollowers(id) {
  return api.get(`/users/${id}/followers`).then((r) => r.data)
}

export function fetchFollowing(id) {
  return api.get(`/users/${id}/following`).then((r) => r.data)
}
