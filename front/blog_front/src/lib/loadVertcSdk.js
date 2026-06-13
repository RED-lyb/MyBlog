/** 懒加载火山 Web RTC SDK（与 BasicDemo 4.66 同源，见 public/vendor/vertc-4.66.min.js） */
let loadPromise = null

export function loadVertcSdk() {
  if (typeof window !== 'undefined' && window.VERTC) {
    return Promise.resolve(window.VERTC)
  }
  if (!loadPromise) {
    loadPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = `${import.meta.env.BASE_URL}vendor/vertc-4.66.min.js`
      script.async = true
      script.onload = () => {
        if (window.VERTC) {
          resolve(window.VERTC)
        } else {
          reject(new Error('VERTC SDK 加载失败'))
        }
      }
      script.onerror = () => reject(new Error('无法加载 VERTC SDK 脚本'))
      document.head.appendChild(script)
    })
  }
  return loadPromise
}
