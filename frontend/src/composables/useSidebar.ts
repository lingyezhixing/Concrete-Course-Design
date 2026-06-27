import { ref } from 'vue'

const GLOBAL_KEY = 'ccd-sidebar'

// 当前作用域键：登录后为 ccd-sidebar:<userId>，未登录为全局
let currentKey = GLOBAL_KEY

const isCollapsed = ref(localStorage.getItem(currentKey) === 'collapsed')

export function useSidebar() {
  function persist(): void {
    localStorage.setItem(
      currentKey,
      isCollapsed.value ? 'collapsed' : 'expanded',
    )
  }

  function toggle(): void {
    isCollapsed.value = !isCollapsed.value
    persist()
  }

  function loadSidebarFor(userId: string | null): void {
    currentKey = userId ? `${GLOBAL_KEY}:${userId}` : GLOBAL_KEY
    isCollapsed.value = localStorage.getItem(currentKey) === 'collapsed'
  }

  return { isCollapsed, toggle, loadSidebarFor }
}
