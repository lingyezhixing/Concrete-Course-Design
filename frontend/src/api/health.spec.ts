import { describe, it, expect, vi, beforeEach } from 'vitest'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('axios', () => ({
  default: {
    create: () => ({
      get,
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    }),
  },
}))

import { getHealth } from './index'

describe('getHealth', () => {
  beforeEach(() => get.mockReset())

  it('calls /health and returns data', async () => {
    get.mockResolvedValue({ data: { status: 'ok' } })
    const result = await getHealth()
    expect(get).toHaveBeenCalledWith('/health')
    expect(result).toEqual({ status: 'ok' })
  })

  // Note: getHealth's error-propagation path (api.get rejects → getHealth rejects)
  // is covered by useHealth's "becomes offline when check throws" test, which
  // mocks '../api' directly. Testing it here would load the real axios module,
  // which interferes with vitest's unhandled-rejection detection.
})
