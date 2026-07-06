const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const REQUEST_TIMEOUT_MS = 10000

export class TrustCheckApiError extends Error {}

export async function checkContent(content, category) {
  // AbortController timeout: without this, a hung backend hangs the UI
  // in a permanent "Checking..." state (security-review finding).
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let response
  try {
    response = await fetch(`${API_BASE}/check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, category }),
      signal: controller.signal,
    })
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new TrustCheckApiError('The check timed out. Please try again.')
    }
    throw new TrustCheckApiError(
      'Could not reach the TrustCheck API. Is the backend running on http://localhost:8000?',
    )
  } finally {
    clearTimeout(timer)
  }

  if (response.status === 429) {
    throw new TrustCheckApiError(
      'Too many checks in a short time - please wait a minute and try again.',
    )
  }

  if (!response.ok) {
    throw new TrustCheckApiError(`TrustCheck API returned an error (status ${response.status}).`)
  }

  return response.json()
}
