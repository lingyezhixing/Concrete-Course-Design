import { ref } from 'vue'

export type Theme = 'dark' | 'light' | 'warm'

const GLOBAL_KEY = 'ccd-theme'
const DEFAULT_THEME: Theme = 'dark'
const VALID: ReadonlySet<Theme> = new Set(['dark', 'light', 'warm'])

// 当前作用域键：登录后为 ccd-theme:<userId>，未登录为全局 ccd-theme
let currentKey = GLOBAL_KEY

function readTheme(key: string): Theme {
  const stored = localStorage.getItem(key)
  return stored && VALID.has(stored as Theme) ? (stored as Theme) : DEFAULT_THEME
}

function applyTheme(next: Theme): void {
  document.documentElement.dataset.theme = next
}

// 模块级单例：所有 useTheme() 调用共享同一主题状态
const theme = ref<Theme>(readTheme(currentKey))
applyTheme(theme.value)

export function useTheme() {
  function setTheme(next: Theme): void {
    theme.value = next
    localStorage.setItem(currentKey, next)
    applyTheme(next)
  }

  function loadThemeFor(userId: string | null): void {
    currentKey = userId ? `${GLOBAL_KEY}:${userId}` : GLOBAL_KEY
    theme.value = readTheme(currentKey)
    applyTheme(theme.value)
  }

  return { theme, setTheme, loadThemeFor }
}
