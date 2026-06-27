import { ref } from 'vue'

export type Theme = 'dark' | 'light' | 'warm'

const STORAGE_KEY = 'ccd-theme'
const DEFAULT_THEME: Theme = 'dark'
const VALID: ReadonlySet<Theme> = new Set(['dark', 'light', 'warm'])

function readTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored && VALID.has(stored as Theme) ? (stored as Theme) : DEFAULT_THEME
}

function applyTheme(next: Theme): void {
  document.documentElement.dataset.theme = next
}

// 模块级单例：所有 useTheme() 调用共享同一主题状态
const theme = ref<Theme>(readTheme())
applyTheme(theme.value)

export function useTheme() {
  function setTheme(next: Theme): void {
    theme.value = next
    localStorage.setItem(STORAGE_KEY, next)
    applyTheme(next)
  }
  return { theme, setTheme }
}
