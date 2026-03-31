export const UPLOAD_POLL_INTERVAL_MS = 2500
export const UPLOAD_POLL_MAX_ATTEMPTS = 40
export const UPLOAD_PROGRESS_MIN = 14
export const UPLOAD_PROGRESS_MAX = 94
export const MAIN_INPUT_MIN_HEIGHT = 44
export const MAIN_INPUT_MAX_HEIGHT = 180

export const EMOJI_OPTIONS = ['📘', '🧠', '⭐', '✅', '❌', '📌', '📝', '👍', '🔥', '💡']

export const GREETING_MATCHERS = [
  {
    terms: ['hi', 'hello', 'hey', 'hii', 'heyy'],
    response: 'Hello! How can I assist you today? 😊'
  },
  {
    terms: [
      'Assalam o alaikum',
      'Assalamu alaikum',
      'Aslam o alaikum',
      'Assalam',
      'Assalam o alikum',
      'Salam',
      'assalam o alaikum',
      'assalamu alaikum',
      'aslam o alaikum',
      'assalam',
      'assalam o alikum',
      'salam',
      'aoa',
      'Aoa',
      'slm'
    ],
    response: 'Wa Alaikum Assalam! How can I help you today? 🤝'
  }
]

export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

export const clamp = (value, min, max) => Math.max(min, Math.min(max, value))

export const normalizeIntentText = (value) => {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export const compactIntentText = (value) => normalizeIntentText(value).replace(/\s+/g, '')

export const getGreetingResponse = (value) => {
  const normalized = normalizeIntentText(value)
  if (!normalized) return null

  const compact = compactIntentText(normalized)
  for (const matcher of GREETING_MATCHERS) {
    for (const term of matcher.terms) {
      const normalizedTerm = normalizeIntentText(term)
      if (!normalizedTerm) continue

      if (normalized === normalizedTerm || compact === compactIntentText(normalizedTerm)) {
        return matcher.response
      }
    }
  }

  return null
}

export const getProgressForAttempt = (attempt) => {
  const raw = UPLOAD_PROGRESS_MIN + (attempt * 9)
  return clamp(raw, UPLOAD_PROGRESS_MIN, UPLOAD_PROGRESS_MAX)
}

export const isRequestCancelledError = (error) => {
  const name = String(error?.name || '').toLowerCase()
  const code = String(error?.code || '').toLowerCase()
  const message = String(error?.message || '').toLowerCase()
  return (
    name.includes('cancel')
    || code.includes('cancel')
    || message.includes('canceled')
    || message.includes('aborted')
  )
}

export const escapeHtml = (value) => {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

export const formatMessage = (text) => {
  if (!text) return ''

  const normalized = String(text).replace(/\r\n?/g, '\n').trim()
  const escaped = escapeHtml(normalized)
  const withBold = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  const lines = withBold.split('\n')

  let html = ''
  let inUl = false
  let inOl = false

  const closeLists = () => {
    if (inUl) {
      html += '</ul>'
      inUl = false
    }
    if (inOl) {
      html += '</ol>'
      inOl = false
    }
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()

    if (!line) {
      closeLists()
      html += '<div class="chat-gap"></div>'
      continue
    }

    const headingMatch = line.match(/^#{1,3}\s+(.+)$/)
    if (headingMatch) {
      closeLists()
      html += `<div class="chat-heading">${headingMatch[1]}</div>`
      continue
    }

    const bulletMatch = line.match(/^[-*]\s+(.+)$/)
    if (bulletMatch) {
      if (inOl) {
        html += '</ol>'
        inOl = false
      }
      if (!inUl) {
        html += '<ul class="chat-list">'
        inUl = true
      }
      html += `<li>${bulletMatch[1]}</li>`
      continue
    }

    const numberedMatch = line.match(/^\d+[.)]\s+(.+)$/)
    if (numberedMatch) {
      if (inUl) {
        html += '</ul>'
        inUl = false
      }
      if (!inOl) {
        html += '<ol class="chat-list chat-list-numbered">'
        inOl = true
      }
      html += `<li>${numberedMatch[1]}</li>`
      continue
    }

    closeLists()
    html += `<p class="chat-paragraph">${line}</p>`
  }

  closeLists()
  return html
}
