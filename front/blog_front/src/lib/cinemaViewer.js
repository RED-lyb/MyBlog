import { MediaMTXWebRTCReader } from './mediamtxReader.js'

const WEBRTC_CONNECT_TIMEOUT_MS = 20000

function apiOrigin() {
  const raw = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/'
  const base = raw.endsWith('/') ? raw : `${raw}/`
  return new URL(base).origin
}

/** 将后端返回的相对代理路径或旧版 mediamtx 绝对地址解析为可请求的完整 URL */
function resolveStreamUrl(url) {
  if (!url || typeof window === 'undefined') return url

  if (url.startsWith('/api/cinema/mtx/')) {
    return `${apiOrigin()}${url}`
  }

  try {
    const parsed = new URL(url, window.location.origin)
    const host = parsed.hostname
    if (host !== '127.0.0.1' && host !== 'localhost') return url
    if (parsed.port === '8889') {
      return `${apiOrigin()}/api/cinema/mtx/webrtc${parsed.pathname}${parsed.search}`
    }
  } catch {
    // ignore
  }
  return url
}

function prepareLiveVideo(videoEl, { muted = true } = {}) {
  if (!videoEl) return
  videoEl.muted = muted
  videoEl.volume = 1
  videoEl.controls = false
  videoEl.disablePictureInPicture = true
  if ('disableRemotePlayback' in videoEl) {
    videoEl.disableRemotePlayback = true
  }
}

/**
 * 同频影院观众端：WebRTC(WHEP) 播放
 */
export class CinemaViewer {
  constructor(handlers = {}) {
    this.handlers = handlers
    this.webrtcReader = null
    this.videoEl = null
    this.remoteStream = null
    this._onVideoPlay = null
    this._hasVideoTrack = false
    this._needsUnmute = false
  }

  async play({ videoEl, playback }) {
    await this._teardown()
    if (!videoEl || !playback) return false

    this.videoEl = videoEl
    prepareLiveVideo(videoEl, { muted: true })
    return this._playWebRtc(playback.webrtc_whep_url || playback.play_url)
  }

  _attachRemoteTrack(evt) {
    if (!this.videoEl || !evt.track) return

    if (!this.remoteStream) {
      this.remoteStream = new MediaStream()
    }

    const exists = this.remoteStream
      .getTracks()
      .some((track) => track.id === evt.track.id)
    if (!exists) {
      this.remoteStream.addTrack(evt.track)
    }

    this.videoEl.srcObject = this.remoteStream
    prepareLiveVideo(this.videoEl, { muted: true })
  }

  _logTracks(label) {
    if (!this.remoteStream) return
    const summary = this.remoteStream
      .getTracks()
      .map((t) => `${t.kind}:${t.enabled}:${t.muted}`)
      .join(', ')
    console.info(`[cinema] ${label}: ${summary || 'no tracks'}`)
  }

  _playWebRtc(whepUrl) {
    const url = resolveStreamUrl(whepUrl)
    if (!url) return Promise.resolve(false)

    return new Promise((resolve) => {
      let settled = false
      const timer = setTimeout(() => {
        if (!settled) {
          console.warn('[cinema] webrtc connect timeout')
          this.handlers.onError?.('连接放映流超时')
          finish(false)
        }
      }, WEBRTC_CONNECT_TIMEOUT_MS)

      const finish = (ok) => {
        if (!settled) {
          settled = true
          clearTimeout(timer)
          resolve(ok)
        }
      }

      const markLive = () => {
        this.handlers.onStreamStart?.()
        if (this._needsUnmute) {
          this.handlers.onNeedUnmute?.()
        }
        finish(true)
      }

      this.remoteStream = new MediaStream()
      this._hasVideoTrack = false
      this._needsUnmute = true

      this.webrtcReader = new MediaMTXWebRTCReader({
        url,
        skipCodecProbe: true,
        retryPauseMs: 500,
        onError: (err) => {
          const msg = String(err || '')
          if (msg.includes('retrying')) {
            console.info('[cinema] webrtc retry:', msg)
            return
          }
          console.warn('[cinema] webrtc error:', msg)
          this.handlers.onError?.(msg)
          finish(false)
        },
        onTrack: (evt) => {
          if (!this.videoEl) {
            finish(false)
            return
          }

          this._attachRemoteTrack(evt)
          this._logTracks(`track ${evt.track.kind}`)

          if (evt.track.kind === 'audio') {
            this._needsUnmute = true
          }

          if (evt.track.kind === 'video' && !this._hasVideoTrack) {
            this._hasVideoTrack = true
            const playPromise = this.videoEl.play()
            if (playPromise?.then) {
              playPromise
                .then(() => markLive())
                .catch(() => {
                  this.handlers.onAutoplayFailed?.()
                  markLive()
                })
            } else {
              markLive()
            }
          }
        },
      })
    })
  }

  async _teardown() {
    if (this.webrtcReader) {
      this.webrtcReader.close()
      this.webrtcReader = null
    }
    if (this.videoEl && this._onVideoPlay) {
      this.videoEl.removeEventListener('play', this._onVideoPlay)
      this._onVideoPlay = null
    }
    if (this.remoteStream) {
      this.remoteStream.getTracks().forEach((track) => track.stop())
      this.remoteStream = null
    }
    this._hasVideoTrack = false
    this._needsUnmute = false
    if (this.videoEl) {
      this.videoEl.srcObject = null
      this.videoEl.removeAttribute('src')
      this.videoEl.load()
    }
  }

  async stop() {
    await this._teardown()
    this.handlers.onStreamStop?.()
  }

  async playWithUserGesture() {
    if (!this.videoEl) return false
    try {
      this._needsUnmute = false
      this.videoEl.muted = false
      this.videoEl.volume = 1
      await this.videoEl.play()
      this._logTracks('after unmute')
      this.handlers.onAutoplayRecovered?.()
      return true
    } catch (err) {
      console.warn('[cinema] unmute play failed:', err)
      return false
    }
  }
}
