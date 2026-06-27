import { computed, ref } from 'vue'

import { fetchMe, login as apiLogin, register as apiRegister } from '../api/auth'
import type { TokenResponse, UserPublic } from '../api/auth'
import { useSidebar } from './useSidebar'
import { useTheme } from './useTheme'

const TOKEN_KEY = 'ccd-token'
const USER_KEY = 'ccd-user'

const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
const currentUser = ref<UserPublic | null>(readCachedUser())

const isAuthenticated = computed(
  () => token.value !== null && currentUser.value !== null,
)

function readCachedUser(): UserPublic | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserPublic
  } catch {
    return null
  }
}

function applySession(res: TokenResponse): void {
  token.value = res.access_token
  currentUser.value = res.user
  localStorage.setItem(TOKEN_KEY, res.access_token)
  localStorage.setItem(USER_KEY, JSON.stringify(res.user))
  const uid = String(res.user.id)
  useTheme().loadThemeFor(uid)
  useSidebar().loadSidebarFor(uid)
}

export function useAuth() {
  async function login(username: string, password: string): Promise<UserPublic> {
    const res = await apiLogin(username, password)
    applySession(res)
    return res.user
  }

  async function register(username: string, password: string): Promise<void> {
    // 仅创建账户，不自动登录 —— 注册后引导用户去登录页登录
    await apiRegister(username, password)
  }

  function logout(): void {
    token.value = null
    currentUser.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    useTheme().loadThemeFor(null)
    useSidebar().loadSidebarFor(null)
  }

  async function bootstrap(): Promise<void> {
    // 1) 同步恢复缓存（立即按用户键载入偏好，避免闪烁）
    const cached = readCachedUser()
    if (cached && token.value) {
      currentUser.value = cached
      const uid = String(cached.id)
      useTheme().loadThemeFor(uid)
      useSidebar().loadSidebarFor(uid)
    }
    // 2) 异步校验 token；失效则登出
    if (token.value) {
      try {
        const me = await fetchMe()
        currentUser.value = me
        localStorage.setItem(USER_KEY, JSON.stringify(me))
      } catch {
        logout()
      }
    }
  }

  return { token, currentUser, isAuthenticated, login, register, logout, bootstrap }
}
