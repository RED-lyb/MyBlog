const TIMER_KEY = '__cinemaStreamStatusPollTimer'
const ACTIVE_KEY = '__cinemaStreamStatusPollActive'

/** 停止全局放映状态轮询（防止 HMR 叠加多个 interval） */
export function stopCinemaStreamPoll() {
  window[ACTIVE_KEY] = false
  const timer = window[TIMER_KEY]
  if (timer) {
    clearTimeout(timer)
    window[TIMER_KEY] = null
  }
}

/**
 * 启动全局放映状态轮询：上一次完成后等待 intervalMs 再发起下一次
 * @param {() => Promise<void>} tick
 * @param {number} intervalMs
 */
export function startCinemaStreamPoll(tick, intervalMs = 5000) {
  stopCinemaStreamPoll()
  window[ACTIVE_KEY] = true

  const schedule = (delay = intervalMs) => {
    if (!window[ACTIVE_KEY]) return
    window[TIMER_KEY] = setTimeout(async () => {
      if (!window[ACTIVE_KEY]) return
      try {
        await tick()
      } catch {
        // 由 tick 自行处理错误展示
      }
      schedule()
    }, delay)
  }

  schedule()
}

if (import.meta.hot) {
  import.meta.hot.dispose(() => {
    stopCinemaStreamPoll()
  })
}
