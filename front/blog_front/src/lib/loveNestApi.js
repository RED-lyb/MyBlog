import apiClient from './api.js'

export function loveNestApiBase() {
  const raw = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/'
  return raw.endsWith('/') ? raw : `${raw}/`
}

export function loveNestApiUrl(path) {
  const p = path.replace(/^\//, '')
  return `${loveNestApiBase()}love_nest/${p}`
}

export async function fetchLoveNestConfig() {
  const response = await apiClient.get(loveNestApiUrl('config/'))
  return response
}

export async function fetchLoveNestPhotos(params = {}) {
  const response = await apiClient.get(loveNestApiUrl('photos/'), { params })
  return response
}

export async function fetchLoveNestDecorPhotos() {
  const response = await apiClient.get(loveNestApiUrl('photos/decor/'))
  return response
}

export async function checkLoveNestEditor() {
  const response = await apiClient.get(loveNestApiUrl('editor/check/'))
  return response
}

export async function uploadLoveNestPhoto(formData) {
  const response = await apiClient.post(loveNestApiUrl('photos/upload/'), formData)
  return response
}

export async function updateLoveNestPhoto(photoId, payload) {
  const response = await apiClient.put(loveNestApiUrl(`photos/${photoId}/update/`), payload)
  return response
}

export async function deleteLoveNestPhoto(photoId) {
  const response = await apiClient.delete(loveNestApiUrl(`photos/${photoId}/delete/`))
  return response
}

export async function updateLoveNestConfig(payload) {
  const response = await apiClient.put(loveNestApiUrl('config/update/'), payload)
  return response
}

export async function updateLoveNestMembers(payload) {
  const response = await apiClient.put(loveNestApiUrl('config/members/'), payload)
  return response
}

export async function fetchLoveNestDiaries(params = {}) {
  const response = await apiClient.get(loveNestApiUrl('diaries/'), { params })
  return response
}

export async function createLoveNestDiary(payload) {
  const response = await apiClient.post(loveNestApiUrl('diaries/create/'), payload)
  return response
}

export async function updateLoveNestDiary(diaryId, payload) {
  const isFormData = typeof FormData !== 'undefined' && payload instanceof FormData
  const response = isFormData
    ? await apiClient.post(loveNestApiUrl(`diaries/${diaryId}/update/`), payload)
    : await apiClient.put(loveNestApiUrl(`diaries/${diaryId}/update/`), payload)
  return response
}

export async function deleteLoveNestDiary(diaryId) {
  const response = await apiClient.delete(loveNestApiUrl(`diaries/${diaryId}/delete/`))
  return response
}

export async function fetchLoveNestMilestones() {
  const response = await apiClient.get(loveNestApiUrl('milestones/'))
  return response
}

export async function createLoveNestMilestone(payload) {
  const response = await apiClient.post(loveNestApiUrl('milestones/create/'), payload)
  return response
}

export async function updateLoveNestMilestone(milestoneId, payload) {
  const response = await apiClient.put(loveNestApiUrl(`milestones/${milestoneId}/update/`), payload)
  return response
}

export async function deleteLoveNestMilestone(milestoneId) {
  const response = await apiClient.delete(loveNestApiUrl(`milestones/${milestoneId}/delete/`))
  return response
}

export async function fetchLoveNestTravel() {
  const response = await apiClient.get(loveNestApiUrl('travel/'))
  return response
}

export async function fetchLoveNestTravelCity(cityId) {
  const response = await apiClient.get(loveNestApiUrl(`travel/${cityId}/`))
  return response
}

export async function createLoveNestTravelCity(payload) {
  const response = await apiClient.post(loveNestApiUrl('travel/create/'), payload)
  return response
}

export async function updateLoveNestTravelCity(cityId, payload) {
  const response = await apiClient.put(loveNestApiUrl(`travel/${cityId}/update/`), payload)
  return response
}

export async function deleteLoveNestTravelCity(cityId) {
  const response = await apiClient.delete(loveNestApiUrl(`travel/${cityId}/delete/`))
  return response
}

export function resolveStaticUrl(path) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  const apiBase = loveNestApiBase().replace(/\/api\/?$/, '')
  return `${apiBase}${path.startsWith('/') ? path : `/${path}`}`
}
