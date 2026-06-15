import { ElMessageBox } from 'element-plus'

/**
 * 显示游客提示对话框（优化版）
 * 只有"去登录"按钮，关闭时返回来源页面
 * @param {Object} router - Vue Router 实例
 * @param {string} fallbackPath - 如果无法获取来源，则跳转到此路径（默认 '/'）
 * @param {Object} options - 自定义文案
 */
export function showGuestDialog(router, fallbackPath = '/', options = {}) {
  const {
    title = '游客须知',
    message = `您当前正在以游客身份访问，仅可进行博客文档内容阅读，<br/>
        无个人主页，无法撰写与上传内容，无法与其他用户进行互动，
        如需获得完整体验，请进行登录<br/>`,
    confirmButtonText = '去登录',
  } = options

  // 获取来源路径（从 sessionStorage 或 document.referrer）
  let returnPath = fallbackPath
  
  try {
    // 优先从 sessionStorage 获取（由路由守卫保存）
    const savedPath = sessionStorage.getItem('guest_from_path')
    if (savedPath && savedPath !== window.location.pathname && savedPath !== '/login') {
      returnPath = savedPath
    } else {
      // 如果没有保存的路径，尝试从 referrer 获取
      const referrer = document.referrer
      if (referrer) {
        const referrerUrl = new URL(referrer)
        const referrerPath = referrerUrl.pathname
        // 确保 referrer 是同一个域名
        if (referrerUrl.origin === window.location.origin && 
            referrerPath !== window.location.pathname && 
            referrerPath !== '/login') {
          returnPath = referrerPath
        }
      }
    }
  } catch {
    // 解析失败，使用 fallbackPath
  }

  ElMessageBox.alert(
    message,
    title,
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText,
      showCancelButton: false,
      type: 'info',
      center: true,
      closeOnClickModal: true,
      closeOnPressEscape: true,
    }
  )
    .then(() => {
      // 点击"去登录"按钮，清除保存的来源路径
      sessionStorage.removeItem('guest_from_path')
      router.push({ path: '/login' })
    })
    .catch(() => {
      // 点击关闭按钮或其他区域关闭对话框，返回来源页面
      sessionStorage.removeItem('guest_from_path')
      if (returnPath && returnPath !== window.location.pathname) {
        router.push({ path: returnPath })
      } else if (returnPath === fallbackPath && fallbackPath !== window.location.pathname) {
        router.push({ path: fallbackPath })
      }
    })
}

/** 同频影院：游客访问时提示登录 */
export function showCinemaLoginDialog(router, fallbackPath = '/home') {
  showGuestDialog(router, fallbackPath, {
    title: '需要登录',
    message: `同频影院仅对已登录用户开放。<br/>请登录账号后再进入放映厅观看。`,
    confirmButtonText: '去登录',
  })
}

/**
 * 保存当前路径到 sessionStorage（在路由守卫中调用）
 * 用于游客模式下关闭对话框时返回
 */
export function saveGuestFromPath() {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('guest_from_path', window.location.pathname)
  }
}

