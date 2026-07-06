const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export class TrustCheckApiError extends Error {}

export async function checkContent(content, category) {
  let response
  try {
    response = await fetch(`${API_BASE}/check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, category }),
    })
  } catch (networkError) {
    throw new TrustCheckApiError(
      'Could not reach the TrustCheck API. Is the backend running on http://localhost:8000?',
    )
  }

  if (!response.ok) {
    throw new TrustCheckApiError(`TrustCheck API returned an error (status ${response.status}).`)
  }

  return response.json()
}
