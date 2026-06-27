import { ref } from 'vue'
import type { Ref } from 'vue'
import { getHealth } from '../api'

export function useHealth(intervalMs = 5000): {
  isOnline: Ref<boolean>
  start: () => void
  stop: () => void
} {
  const isOnline = ref(false)
  let timer: ReturnType<typeof setInterval> | null = null

  async function check(): Promise<void> {
    try {
      await getHealth()
      isOnline.value = true
    } catch {
      isOnline.value = false
    }
  }

  function start(): void {
    if (timer !== null) return
    void check()
    timer = setInterval(() => void check(), intervalMs)
  }

  function stop(): void {
    if (timer === null) return
    clearInterval(timer)
    timer = null
  }

  return { isOnline, start, stop }
}
