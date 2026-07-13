const VAR_PATTERN = /\[([^\[\]\n]{1,50})\]/g

export function parseVariables(text) {
  const seen = new Set()
  for (const match of text.matchAll(VAR_PATTERN)) {
    const name = match[1].trim()
    if (name) seen.add(name)
  }
  return [...seen]
}

/** [변수] 하이라이트 렌더용으로 텍스트를 {text, isVar} 조각으로 분리 */
export function splitVariableSegments(text) {
  const parts = []
  const regex = /\[([^\[\]\n]{1,50})\]/g
  let last = 0
  for (const m of text.matchAll(regex)) {
    if (m.index > last) parts.push({ text: text.slice(last, m.index), isVar: false })
    parts.push({ text: m[0], isVar: true })
    last = m.index + m[0].length
  }
  if (last < text.length) parts.push({ text: text.slice(last), isVar: false })
  return parts
}

export function substituteVariables(text, values) {
  return text.replace(VAR_PATTERN, (whole, name) => {
    const filled = values[name.trim()]
    return filled ? filled : whole
  })
}
