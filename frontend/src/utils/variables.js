const VAR_PATTERN = /\[([^\[\]\n]{1,50})\]/g

export function parseVariables(text) {
  const seen = new Set()
  for (const match of text.matchAll(VAR_PATTERN)) {
    const name = match[1].trim()
    if (name) seen.add(name)
  }
  return [...seen]
}

export function substituteVariables(text, values) {
  return text.replace(VAR_PATTERN, (whole, name) => {
    const filled = values[name.trim()]
    return filled ? filled : whole
  })
}
