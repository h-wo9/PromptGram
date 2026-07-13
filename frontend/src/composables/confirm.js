import { reactive } from 'vue'

export const confirmState = reactive({
  open: false,
  title: '',
  body: '',
  confirmText: '확인',
  danger: false,
  _resolve: null,
})

export function confirmDialog({ title, body = '', confirmText = '확인', danger = false }) {
  return new Promise((resolve) => {
    Object.assign(confirmState, { open: true, title, body, confirmText, danger, _resolve: resolve })
  })
}

export function settleConfirm(result) {
  confirmState.open = false
  confirmState._resolve?.(result)
  confirmState._resolve = null
}
