const DEFAULT_API = '/api'

export function getApiUrl() {
  return localStorage.getItem('sre_api_url') || DEFAULT_API
}

export function setApiUrl(url) {
  localStorage.setItem('sre_api_url', url.replace(/\/$/, ''))
}

async function request(path, options = {}) {
  const response = await fetch(`${getApiUrl()}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })

  const text = await response.text()
  let data = {}
  try {
    data = text ? JSON.parse(text) : {}
  } catch {
    data = { detail: text }
  }

  if (!response.ok) {
    throw new Error(data.detail || `Request failed (${response.status})`)
  }

  return data
}

export const api = {
  health: () => request('/health'),
  createIncident: (payload) => request('/incident', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  approve: (threadId, payload) => request(`/incident/${threadId}/approve`, {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  cloudwatchScan: (region) => request('/cloudwatch/incidents', {
    method: 'POST',
    body: JSON.stringify({ region_name: region }),
  }),
  getIncident: (threadId) => request(`/incident/${threadId}`),
}
