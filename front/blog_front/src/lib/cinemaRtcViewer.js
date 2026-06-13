/**
 * 同频影院观众端：仅订阅远端音视频，不采集、不发布
 */
import { loadVertcSdk } from './loadVertcSdk.js'

export class CinemaRtcViewer {
  constructor(handlers = {}) {
    this.handlers = handlers
    this.VERTC = null
    this.engine = null
    this.publisherUserId = ''
    this.renderDom = null
    this.autoPlayFailUsers = new Set()
    this._onUserPublishStream = this._onUserPublishStream.bind(this)
    this._onUserStartVideoCapture = this._onUserStartVideoCapture.bind(this)
    this._onUserUnpublishStream = this._onUserUnpublishStream.bind(this)
    this._onUserJoined = this._onUserJoined.bind(this)
    this._onUserLeave = this._onUserLeave.bind(this)
    this._onAutoplayFailed = this._onAutoplayFailed.bind(this)
    this._onError = this._onError.bind(this)
  }

  get isJoined() {
    return !!this.engine
  }

  async _ensureSdk() {
    if (!this.VERTC) {
      this.VERTC = await loadVertcSdk()
    }
    return this.VERTC
  }

  async join({ appId, roomId, userId, token, publisherUserId, renderDom }) {
    await this.leave()
    const VERTC = await this._ensureSdk()
    this.publisherUserId = publisherUserId || ''
    this.renderDom = renderDom
    this.engine = VERTC.createEngine(appId)
    this._bindEvents()
    await this.engine.joinRoom(
      token,
      roomId,
      { userId },
      {
        isAutoPublish: false,
        isAutoSubscribeAudio: true,
        isAutoSubscribeVideo: true,
      }
    )
    this.handlers.onRoomJoined?.()
  }

  async subscribePublisher(remoteUserId) {
    if (!this.engine || !this.renderDom) return false
    if (this.publisherUserId && remoteUserId !== this.publisherUserId) return false

    const VERTC = this.VERTC
    await this.engine.subscribeStream(remoteUserId, VERTC.MediaType.AUDIO_AND_VIDEO)
    await this.engine.setRemoteVideoPlayer(VERTC.StreamIndex.STREAM_INDEX_MAIN, {
      userId: remoteUserId,
      renderDom: this.renderDom,
    })
    this.handlers.onPublisherStream?.(remoteUserId)
    return true
  }

  async playFailedUsers() {
    if (!this.engine || this.autoPlayFailUsers.size === 0) return
    for (const uid of this.autoPlayFailUsers) {
      try {
        await this.engine.play(uid)
      } catch (e) {
        console.warn('RTC play retry failed', uid, e)
      }
    }
    this.autoPlayFailUsers.clear()
    this.handlers.onAutoplayRecovered?.()
  }

  async leave() {
    if (!this.engine) return
    this._unbindEvents()
    try {
      await this.engine.leaveRoom()
    } catch (e) {
      console.warn('leaveRoom', e)
    }
    try {
      if (this.VERTC) {
        this.VERTC.destroyEngine(this.engine)
      }
    } catch (e) {
      console.warn('destroyEngine', e)
    }
    this.engine = null
    this.autoPlayFailUsers.clear()
    this.handlers.onRoomLeft?.()
  }

  _bindEvents() {
    if (!this.engine || !this.VERTC) return
    const { events } = this.VERTC
    this.engine.on(events.onUserPublishStream, this._onUserPublishStream)
    this.engine.on(events.onUserStartVideoCapture, this._onUserStartVideoCapture)
    this.engine.on(events.onUserUnpublishStream, this._onUserUnpublishStream)
    this.engine.on(events.onUserJoined, this._onUserJoined)
    this.engine.on(events.onUserLeave, this._onUserLeave)
    this.engine.on(events.onAutoplayFailed, this._onAutoplayFailed)
    this.engine.on(events.onError, this._onError)
  }

  _unbindEvents() {
    if (!this.engine || !this.VERTC) return
    const { events } = this.VERTC
    this.engine.off(events.onUserPublishStream, this._onUserPublishStream)
    this.engine.off(events.onUserStartVideoCapture, this._onUserStartVideoCapture)
    this.engine.off(events.onUserUnpublishStream, this._onUserUnpublishStream)
    this.engine.off(events.onUserJoined, this._onUserJoined)
    this.engine.off(events.onUserLeave, this._onUserLeave)
    this.engine.off(events.onAutoplayFailed, this._onAutoplayFailed)
    this.engine.off(events.onError, this._onError)
  }

  async _onUserPublishStream(stream) {
    const VERTC = this.VERTC
    const { userId, mediaType } = stream
    if (!(mediaType & VERTC.MediaType.VIDEO)) return
    await this.subscribePublisher(userId)
  }

  async _onUserStartVideoCapture(event) {
    const { userId } = event
    await this.subscribePublisher(userId)
  }

  _onUserJoined(event) {
    const userId = event?.userInfo?.userId
    if (!userId) return
    this.handlers.onUserJoined?.(userId)
    if (this.publisherUserId && userId === this.publisherUserId) {
      this.subscribePublisher(userId).catch((e) => console.warn('[cinema] subscribe on join', e))
    }
  }

  _onUserUnpublishStream(stream) {
    const VERTC = this.VERTC
    const { userId, mediaType } = stream
    if (mediaType & VERTC.MediaType.VIDEO && userId === this.publisherUserId) {
      this.handlers.onPublisherUnpublish?.(userId)
    }
  }

  _onUserLeave(event) {
    const userId = event?.userInfo?.userId
    if (userId && userId === this.publisherUserId) {
      this.handlers.onPublisherLeave?.(userId)
    }
  }

  _onAutoplayFailed(event) {
    if (event?.userId) {
      this.autoPlayFailUsers.add(event.userId)
    }
    this.handlers.onAutoplayFailed?.(event)
  }

  _onError(event) {
    if (event?.errorCode === this.VERTC?.ErrorCode?.DUPLICATE_LOGIN) {
      this.handlers.onDuplicateLogin?.()
      return
    }
    this.handlers.onError?.(event)
  }
}

export async function fetchCinemaToken(roomId, userId) {
  const axios = (await import('./api.js')).default
  const { cinemaApiUrl } = await import('./cinemaApi.js')
  if (!userId) {
    throw new Error('请先登录后再观看')
  }
  const res = await axios.post(cinemaApiUrl('get/token'), {
    room_id: roomId,
    user_id: userId,
  })
  const body = res.data || {}
  if (res.status !== 200 || !body.data) {
    throw new Error(body.message || body.error || '获取 RTC Token 失败')
  }
  return {
    token: body.data,
    user_id: body.user_id,
    room_id: body.room_id,
  }
}
