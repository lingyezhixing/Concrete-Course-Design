import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

const { getHealth } = vi.hoisted(() => ({ getHealth: vi.fn() }))
vi.mock('../api', () => ({ getHealth }))

import { useHealth } from './useHealth'

describe('useHealth', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    getHealth.mockReset()
  })
  afterEach(() => vi.useRealTimers())

  it('starts offline, becomes online after a successful check', async () => {
    getHealth.mockResolvedValue({ status: 'ok' })
    const { isOnline, start, stop } = useHealth()
    expect(isOnline.value).toBe(false)
    start()
    await vi.waitFor(() => expect(isOnline.value).toBe(true))
    stop()
  })

  it('becomes offline when check throws', async () => {
    getHealth.mockRejectedValue(new Error('down'))
    const { isOnline, start, stop } = useHealth()
    start()
    await vi.waitFor(() => expect(isOnline.value).toBe(false))
    stop()
  })

  it('polls at the given interval', async () => {
    getHealth.mockResolvedValue({ status: 'ok' })
    const { start, stop } = useHealth(1000)
    start()
    await vi.waitFor(() => expect(getHealth).toHaveBeenCalled())
    const before = getHealth.mock.calls.length
    await vi.advanceTimersByTimeAsync(1000)
    expect(getHealth.mock.calls.length).toBeGreaterThan(before)
    stop()
  })

  it('stop() clears the interval', async () => {
    getHealth.mockResolvedValue({ status: 'ok' })
    const { start, stop } = useHealth(1000)
    start()
    await vi.waitFor(() => expect(getHealth).toHaveBeenCalled())
    stop()
    const after = getHealth.mock.calls.length
    await vi.advanceTimersByTimeAsync(5000)
    expect(getHealth.mock.calls.length).toBe(after)
  })
})
