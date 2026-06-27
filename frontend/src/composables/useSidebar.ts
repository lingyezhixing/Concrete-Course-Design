import { ref } from 'vue'

const STORAGE_KEY = 'ccd-sidebar'

export function useSidebar() {
  const isCollapsed = ref(localStorage.getItem(STORAGE_KEY) === 'collapsed')

  function toggle() {
    isCollapsed.value = !isCollapsed.value
    localStorage.setItem(STORAGE_KEY, isCollapsed.value ? 'collapsed' : 'expanded')
  }

  return { isCollapsed, toggle }
}
