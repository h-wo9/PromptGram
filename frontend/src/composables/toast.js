import { reactive } from 'vue'

let seq = 0
export const toasts = reactive([])

export function showToast(message, type = 'success', duration = 2400) {
  const id = ++seq
  toasts.push({ id, message, type })
  setTimeout(() => {
    const i = toasts.findIndex((t) => t.id === id)
    if (i !== -1) toasts.splice(i, 1)
  }, duration)
}
