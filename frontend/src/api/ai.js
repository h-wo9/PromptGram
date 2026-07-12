import api from './client'

export function tunePrompt(promptText) {
  return api.post('/ai/tune', { prompt_text: promptText }).then((r) => r.data)
}

export function suggestTags(promptText) {
  return api.post('/ai/suggest-tags', { prompt_text: promptText }).then((r) => r.data)
}
