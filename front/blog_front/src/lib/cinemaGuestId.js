const IDENTITY_KEY = 'cinema_guest_identity'

/** VolcEngine userId 仅允许 [0-9a-zA-Z_\\-@.]，中文用户名需映射 */
function isValidRtcUserId(id) {
  return /^[0-9a-zA-Z_\-@.]{1,128}$/.test(id)
}

/** 从 RTC user_id 推导展示名（与后端 guest 规则一致） */
export function displayNameFromRtcUserId(rtcUserId) {
  const s = String(rtcUserId || '')
  if (s.startsWith('guest_')) {
    return `游客${s.slice(6)}`
  }
  return s
}

export function readCachedGuestIdentity() {
  try {
    const raw = sessionStorage.getItem(IDENTITY_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (parsed?.rtcUserId && parsed?.displayName) return parsed
  } catch {
    // ignore
  }
  return null
}

export function cacheGuestIdentity(identity) {
  sessionStorage.setItem(IDENTITY_KEY, JSON.stringify(identity))
}

/** 清除本标签页缓存的游客身份（下次进房向后端申请新序号） */
export function resetCinemaGuestIdentity() {
  sessionStorage.removeItem(IDENTITY_KEY)
}

/** 已登录观众的 RTC 身份（游客请走 get/token 由后端分配） */
export function resolveLoggedInViewerIdentity(authStore) {
  if (!authStore?.isAuthenticated || !authStore.username) {
    return null
  }
  const name = String(authStore.username).trim().slice(0, 64)
  if (isValidRtcUserId(name)) {
    return { rtcUserId: name, displayName: name }
  }
  const uid = authStore.userId != null ? String(authStore.userId) : '0'
  const rtcUserId = `u${uid}`
  return { rtcUserId, displayName: name }
}
