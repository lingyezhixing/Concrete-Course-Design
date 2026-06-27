import { ref } from 'vue'

const STORAGE_KEY = 'ccd-theme'

function readIsDark(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored === null ? true : stored === 'dark'
}

function applyClass(isDark: boolean): void {
  document.documentElement.classList.toggle('dark', isDark)
}

export function useTheme() {
  const isDark = ref(readIsDark())
  applyClass(isDark.value)

  function toggle() {
    isDark.value = !isDark.value
    localStorage.setItem(STORAGE_KEY, isDark.value ? 'dark' : 'light')
    applyClass(isDark.value)
  }

  return { isDark, toggle }
}
