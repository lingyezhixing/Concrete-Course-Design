import api from './index'

export interface UserPublic {
  id: number
  username: string
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: UserPublic
}

export async function register(
  username: string,
  password: string,
): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/auth/register', {
    username,
    password,
  })
  return data
}

export async function login(
  username: string,
  password: string,
): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/auth/login', {
    username,
    password,
  })
  return data
}

export async function fetchMe(): Promise<UserPublic> {
  const { data } = await api.get<UserPublic>('/auth/me')
  return data
}

export async function deleteAccount(): Promise<void> {
  await api.delete('/auth/account')
}
