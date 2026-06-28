import { ref } from 'vue'

const GLOBAL_KEY = 'ccd-sidebar'
const MOBILE_QUERY = '(max-width: 899px)'

// 当前作用域键：登录后为 ccd-sidebar:<userId>，未登录为全局
let currentKey = GLOBAL_KEY

const isCollapsed = ref(localStorage.getItem(currentKey) === 'collapsed')
const mobileOpen = ref(false)

// 窄屏跟踪：宽屏 sidebar 为常驻可折叠列；窄屏改为 overlay 抽屉。
// 防御性读取 matchMedia（测试环境 happy-dom 可能未实现）。
const supportsMatchMedia =
  typeof window !== 'undefined' && typeof window.matchMedia === 'function'
const mql = supportsMatchMedia ? window.matchMedia(MOBILE_QUERY) : null
const isMobile = ref(mql?.matches ?? false)
if (mql) {
  mql.addEventListener('change', (e) => {
    isMobile.value = e.matches
    if (!e.matches) mobileOpen.value = false // 回到宽屏时收起抽屉
  })
}

export function useSidebar() {
  function persist(): void {
    localStorage.setItem(
      currentKey,
      isCollapsed.value ? 'collapsed' : 'expanded',
    )
  }

  // 折叠按钮统一入口：宽屏切换常驻列折叠态；窄屏切换抽屉开合。
  function toggle(): void {
    if (isMobile.value) {
      mobileOpen.value = !mobileOpen.value
    } else {
      isCollapsed.value = !isCollapsed.value
      persist()
    }
  }

  function closeMobile(): void {
    mobileOpen.value = false
  }

  function loadSidebarFor(userId: string | null): void {
    currentKey = userId ? `${GLOBAL_KEY}:${userId}` : GLOBAL_KEY
    isCollapsed.value = localStorage.getItem(currentKey) === 'collapsed'
    mobileOpen.value = false
  }

  return { isCollapsed, mobileOpen, isMobile, toggle, closeMobile, loadSidebarFor }
}
