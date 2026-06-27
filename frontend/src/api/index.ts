import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export default api

export interface HealthResponse {
  status: string
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>('/health')
  return data
}
