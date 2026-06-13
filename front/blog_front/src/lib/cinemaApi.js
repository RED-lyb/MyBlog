import apiClient from './api.js'

/** 统一影院 API 前缀，避免 VITE_API_URL 为空时请求落到前端路由 */
export function cinemaApiBase() {
  const raw = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/'
  return raw.endsWith('/') ? raw : `${raw}/`
}

export function cinemaApiUrl(path) {
  const p = path.replace(/^\//, '')
  return `${cinemaApiBase()}cinema/${p}`
}

export async function fetchCinemaStreamStatus() {
  const url = cinemaApiUrl('stream/status/')
  const response = await apiClient.get(url)
  return { url, response }
}

export async function fetchCinemaList() {
  const url = cinemaApiUrl('list/')
  const response = await apiClient.get(url)
  return { url, response }
}
