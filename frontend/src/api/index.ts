import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

// 请求拦截：注入 Bearer token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ccd-token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：非鉴权端点 401 → 清登录态并跳登录页
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    const url: string = error?.config?.url ?? ''
    if (status === 401 && !url.includes('/auth/')) {
      localStorage.removeItem('ccd-token')
      localStorage.removeItem('ccd-user')
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default api

export interface HealthResponse {
  status: string
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>('/health')
  return data
}
