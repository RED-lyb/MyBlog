/** 已登录观众的展示名称 */
export function resolveViewerIdentity(authStore) {
  if (!authStore?.isAuthenticated) {
    return null
  }
  const displayName = String(authStore.username || `用户${authStore.userId || ''}`).trim()
  return { displayName: displayName || '观众' }
}
