#include "bytertc_video_ex.h"
#include "bytertc_room_ex.h"
#include "bytertc_room_event_handler_ex.h"
#include "util/thread_loop.h"
#include <atomic>
#include <memory>
#include <vector>

struct StuPushExternalVideoFrameInfo {
	int width = 1920;
	int height = 1080;
	int fps = 30;
	int total_frames = 0;
	int current_frame_index = 0;
	int first_key_frame_index = 0;
	std::vector<uint8_t>  h264_data;
	std::vector<uint64_t> h264_frame_offset;
	std::vector<int>      h264_frame_size;
	std::vector<bool>     h264_frame_is_key;
	Timer *timer = nullptr;

	int firstKeyFrameIndex() const {
		for (int i = 0; i < total_frames; ++i) {
			if (h264_frame_is_key[i]) {
				return i;
			}
		}
		return 0;
	}

	int nextKeyFrameIndex(int from) const {
		for (int i = from + 1; i < total_frames; ++i) {
			if (h264_frame_is_key[i]) {
				return i;
			}
		}
		for (int i = 0; i <= from; ++i) {
			if (h264_frame_is_key[i]) {
				return i;
			}
		}
		return 0;
	}

	/** 从当前位置向前找最近的关键帧，避免 onRequestKeyFrame 跳到文件后半段的 I 帧 */
	int keyFrameIndexAtOrBefore(int from) const {
		if (total_frames <= 0) {
			return 0;
		}
		int idx = from;
		if (idx >= total_frames) {
			idx = total_frames - 1;
		}
		if (idx < 0) {
			idx = 0;
		}
		while (idx >= 0) {
			if (h264_frame_is_key[idx]) {
				return idx;
			}
			--idx;
		}
		return firstKeyFrameIndex();
	}
};
class RTCVideoEngineWrapper:public bytertc::IRTCVideoEventHandler,
	public bytertc::IRTCVideoEventHandlerEx,
	public bytertc::IRTCRoomEventHandler,
	public bytertc::IRTCRoomEventHandlerEx,
	public bytertc::IExternalVideoEncoderEventHandler
{
public:
	RTCVideoEngineWrapper();
	~RTCVideoEngineWrapper();
	int init();
	int joinRoom();
	int destory();
	bool isPlaybackFinished() const;
	int maxPlaybackWaitMs() const;
	void forceEndPlayback();
	static RTCVideoEngineWrapper *instance();
protected:
	int initVideoConfig();
	int initAudioConfig();
	void alignAudioDurationToVideo();
	void resetPlaybackState();
	void startAudioPush();
	void stopAudioPush();
	void stopVideoPush();
	void markPlaybackComplete();
	void ensureVideoPushStarted();
	void disableAudioWithFallback(const char *reason);
	void pushExternalEncodedVideoFrame();
	void pushExternalAudioFrame();
protected:
	//bytertc::IRTCVideoEventHandler
	void onConnectionStateChanged(bytertc::ConnectionState state) override;
	void onPerformanceAlarms(bytertc::PerformanceAlarmMode mode, const char* room_id,
		bytertc::PerformanceAlarmReason reason, const bytertc::SourceWantedData& data) override;
	void onLocalAudioStateChanged(bytertc::LocalAudioStreamState state, bytertc::LocalAudioStreamError error) override;
	void onRemoteAudioStateChanged(
		const bytertc::RemoteStreamKey& key, bytertc::RemoteAudioState state, bytertc::RemoteAudioStateChangeReason reason) override;

	void onFirstLocalVideoFrameCaptured(bytertc::StreamIndex index, bytertc::VideoFrameInfo info) override;
	void onLocalVideoSizeChanged(bytertc::StreamIndex index, const bytertc::VideoFrameInfo& info) override;
	void onRemoteVideoSizeChanged(bytertc::RemoteStreamKey key, const bytertc::VideoFrameInfo& info) override;
	void onFirstRemoteVideoFrameRendered(const bytertc::RemoteStreamKey key, const bytertc::VideoFrameInfo& info) override;
	void onFirstRemoteVideoFrameDecoded(const bytertc::RemoteStreamKey key, const bytertc::VideoFrameInfo& info) override;
	void onMediaDeviceWarning(const char* device_id, bytertc::MediaDeviceType device_type,bytertc::MediaDeviceWarning device_warning) override;
	void onAudioDeviceStateChanged(const char* device_id, bytertc::RTCAudioDeviceType device_type,
		bytertc::MediaDeviceState device_state, bytertc::MediaDeviceError device_error)override;
	void onVideoDeviceStateChanged(const char* device_id, bytertc::RTCVideoDeviceType device_type,
		bytertc::MediaDeviceState device_state, bytertc::MediaDeviceError device_error)override;
protected:
		//bytertc::IRTCRoomEventHandler
	void onRoomStateChanged(const char* room_id, const char* uid, int state, const char* extra_info) override;
	void onWarning(int warn) override;
	void onError(int err) override ;
	void onLeaveRoom(const bytertc::RtcRoomStats& stats) override;
	void onRoomStats(const bytertc::RtcRoomStats& stats) override;
	void onUserJoined(const bytertc::UserInfo& userInfo, int elapsed) override;
	void onUserLeave(const char* uid, bytertc::UserOfflineReason reason);
	//void onUserPublishStream(const char* uid, bytertc::MediaStreamType type)override;
	//void onUserUnpublishStream(const char* uid, bytertc::MediaStreamType type,bytertc::StreamRemoveReason reason)override;
	void onUserPublishScreen(const char* uid, bytertc::MediaStreamType type);
	void onUserUnpublishScreen(const char* uid, bytertc::MediaStreamType type, bytertc::StreamRemoveReason reason);
	void onStreamRemove(const bytertc::MediaStreamInfo& bs, bytertc::StreamRemoveReason reason) override;
	void onStreamAdd(const bytertc::MediaStreamInfo& stream) override;
	void onStreamSubscribed(bytertc::SubscribeState stateCode, const char* stream_id, const bytertc::SubscribeConfig& info) override;
	void onStreamPublishSuccess(const char* user_id, bool is_screen) override;
	void onRoomMessageReceived(const char* uid, const char* message) override;
	void onRoomBinaryMessageReceived(const char* uid, int size, const uint8_t* message) override;
	void onUserMessageReceived(const char* uid, const char* message) override;
	void onUserBinaryMessageReceived(const char* uid, int size, const uint8_t* message) override;
	void onRoomMessageSendResult(int64_t msgid, int error) override;
	void onUserMessageSendResult(int64_t message_id, int error) override;
	void onStart(bytertc::StreamIndex index) override;
	void onStop(bytertc::StreamIndex index) override;
	void onRateUpdate(bytertc::StreamIndex index, int32_t video_index, bytertc::VideoRateInfo info) override;
	void onRequestKeyFrame(bytertc::StreamIndex index, int32_t video_index) override;
	void onActiveVideoLayer(bytertc::StreamIndex index, int32_t video_index, bool active) override;

protected:
	//bytertc::IRTCRoomEventHandlerEx
	virtual void onUserPublishStream(const bytertc::RemoteStreamKey& stream_key, bool is_screen, bytertc::MediaStreamType type) override;
	virtual void onUserUnpublishStream(
		const bytertc::RemoteStreamKey& stream_key, bytertc::MediaStreamType type, bytertc::StreamRemoveReason reason) override;
	virtual void onStreamStateChanged(
		const bytertc::StreamKey& stream_key, int state, const char* extra_info) override;
protected:	
	//IRTCVideoEventHandlerEx
	virtual void onAudioFrameSendStateChanged(
		const bytertc::StreamKey& stream_key, const char* meta_data, bytertc::FirstFrameSendState state)override;
	virtual void onVideoFrameSendStateChanged(
		const bytertc::StreamKey& stream_key, const char* meta_data, bytertc::FirstFrameSendState state) override;
	virtual void onAudioFramePlayStateChanged(
		const bytertc::StreamKey& stream_key, const char* meta_data, bytertc::FirstFramePlayState state) override;
	virtual void onVideoFramePlayStateChanged(
		const bytertc::StreamKey& stream_key, const char* meta_data, bytertc::FirstFramePlayState state) override;
	
private:
	bytertc::IRTCVideoEx *m_pVideoEngineEx = nullptr;
	bytertc::IRTCRoomEx  *m_pRtcRoomEx = nullptr;
	std::unique_ptr<ThreadLoop>    m_threadLoop;
	std::mutex						m_exitMutex;
	std::shared_ptr<StuPushExternalVideoFrameInfo> m_externalVideoFrameInfo;
	std::vector<uint8_t> m_audioPcm;
	int m_audioTotalChunks = 0;
	int m_audioCurrentChunk = 0;
	Timer *m_audioTimer = nullptr;
	bool m_hasAudio = false;
	bool m_roomJoined = false;
	bool m_audioPushActive = false;
	bool m_audioPublished = false;
	int m_audioFailCount = 0;
	int64_t m_audioTimestampUs = 0;
	std::atomic<bool> m_playbackFinished{false};
	std::atomic<bool> m_videoPushStarted{false};
	static const int kAudioFailThreshold = 5;
};
