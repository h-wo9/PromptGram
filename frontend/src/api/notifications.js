import api from './client'

export function fetchNotifications() {
  return api.get('/notifications').then((r) => r.data)
}

export function readNotification(id) {
  return api.patch(`/notifications/${id}/read`)
}

export function readAllNotifications() {
  return api.post('/notifications/read-all')
}
