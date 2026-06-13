const SESSION_RTC_SUFFIX_KEY = 'cinema_rtc_session_suffix'

/** VolcEngine userId 仅允许 [0-9a-zA-Z_\\-@.] */
function isValidRtcUserId(id) {
  return /^[0-9a-zA-Z_\-@.]{1,128}$/.test(id)
}

function getSessionRtcSuffix() {
  let suffix = sessionStorage.getItem(SESSION_RTC_SUFFIX_KEY)
  if (!suffix) {
    suffix = Math.random().toString(36).slice(2, 8)
    sessionStorage.setItem(SESSION_RTC_SUFFIX_KEY, suffix)
  }
  return suffix
}

/**
 * 已登录观众 RTC 身份：展示用用户名，进房 id 带标签页后缀避免刷新/多开重复进房
 */
export function resolveLoggedInViewerIdentity(authStore) {
  if (!authStore?.isAuthenticated) {
    return null
  }

  const displayName = String(authStore.username || `用户${authStore.userId || ''}`).trim().slice(0, 64)
  const uid = authStore.userId != null ? String(authStore.userId) : '0'
  const suffix = getSessionRtcSuffix()
  let rtcUserId = `u${uid}_${suffix}`

  if (!isValidRtcUserId(rtcUserId)) {
    rtcUserId = `u${uid}_${suffix}`.replace(/[^0-9a-zA-Z_\-@.]/g, '_').slice(0, 128)
  }

  return { rtcUserId, displayName: displayName || rtcUserId }
}
