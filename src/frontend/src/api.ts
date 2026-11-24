export type Loadable<T> =
  | { state: 'loading' }
  | { state: 'ready'; data: T }
  | { state: 'error'; message: string }

export type ApiHealth = {
  status: string
  service: string
  application_status: string
  booking_status: string
  booking_enabled: boolean
  wait_estimate_status: string
  centre_status: string
  database_status: string
}

type ApiErrorBody = { error?: { code?: string; message?: string } }

export async function getApi<T>(path: string, signal?: AbortSignal): Promise<Loadable<T>> {
  try {
    const response = await fetch(path, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal,
    })
    const raw = await response.text()
    let body: unknown = null

    if (raw.trim()) {
      try {
        body = JSON.parse(raw)
      } catch {
        throw new Error(`API returned an unreadable response (${response.status}). Check that the Aapurtikar backend is running on port 8001.`)
      }
    } else if (response.ok) {
      throw new Error('API returned an empty response. Check the backend route and server logs.')
    }

    if (!response.ok) {
      const errorBody = body as ApiErrorBody | null
      throw new Error(errorBody?.error?.message ?? `API request failed (${response.status}).`)
    }

    return { state: 'ready', data: body as T }
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error
    const message = error instanceof TypeError
      ? 'Cannot reach the Aapurtikar API. Start the backend at http://127.0.0.1:8001.'
      : error instanceof Error
        ? error.message
        : 'Unable to load API status.'
    return { state: 'error', message }
  }
}

export const apiPaths = {
  health: '/api/v1/health',
} as const
