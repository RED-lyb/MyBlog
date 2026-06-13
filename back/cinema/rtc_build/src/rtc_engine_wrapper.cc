#include "rtc_engine_wrapper.h"
#include "app_data_manager.h"
#include "video_file_src.h"
#include "mp4_audio_src.h"
#include "util/util.h"
#include "rtc/bytertc_audio_frame.h"
#include <algorithm>
#include <atomic>
#include <chrono>
#include <functional>
#include <memory>
#include "rtc/bytertc_advance.h"
#include "json11.hpp"
#include "bytedance_get_token.h"

RTCVideoEngineWrapper::RTCVideoEngineWrapper(){
	m_threadLoop = std::make_unique<ThreadLoop>();
}

RTCVideoEngineWrapper::~RTCVideoEngineWrapper() {
	if (m_pVideoEngineEx != nullptr) {
		destory();
	}
}

void RTCVideoEngineWrapper::resetPlaybackState()
{
	m_playbackFinished = false;
	m_videoPushStarted = false;
	m_roomJoined = false;
	m_audioPushActive = false;
	m_audioPublished = false;
	m_hasAudio = false;
	m_audioFailCount = 0;
	m_audioTimestampUs = 0;
	m_audioCurrentChunk = 0;
	m_audioTotalChunks = 0;
	m_audioPcm.clear();
	stopAudioPush();
	stopVideoPush();
	m_externalVideoFrameInfo.reset();
}

int RTCVideoEngineWrapper::init() 
{
	resetPlaybackState();

	auto chVersion = bytertc::getSDKVersion();
	std::string strVersion = chVersion ? chVersion : "";
	LOG_INFO("SDK版本:" << strVersion);
	auto appDataIns = AppDataManager::instance()->getAppData();
	
	using namespace json11;

	// default open hardware codec
	auto paramsJsonObj = Json::object{ { "rtc.video_encoder",
		Json::object{{"codec_name","auto"},{"codec_mode","hardware"}} } 
	};

	if (appDataIns->rtc_env == 2) {
		// for test env
		paramsJsonObj.emplace("config_hosts", Json::array{ "rtc-test.bytedance.com" });
		paramsJsonObj.emplace("access_hosts", Json::array{ "rtc-access-test.bytedance.com" });
	}else if (appDataIns->rtc_env == 1) {
		//for boe env
		paramsJsonObj.emplace("config_hosts", Json::array{ "rtc-boe.bytedance.com" });
		paramsJsonObj.emplace("access_hosts", Json::array{ "rtc-access-boe.bytedance.com" });
	}
	paramsJsonObj.emplace("rtc.enable_audio_send", appDataIns->enable_audio);
	paramsJsonObj.emplace("rtc.enable_audio_recv", false);
	
	Json paramJson = paramsJsonObj;
	std::string param;
	paramJson.dump(param);
	LOG_INFO("createRTCVideoEx 参数: " << param);
	m_pVideoEngineEx = bytertc::createRTCVideoEx(appDataIns->app_id.c_str(), this,this, param.c_str());
	if (m_pVideoEngineEx == nullptr) {
		LOG_INFO("创建 rtc video ex 错误!");
		return -1;
	}

	auto nRet = initVideoConfig();
	if (nRet) {
		return nRet;
	}

	nRet = initAudioConfig();
	if (nRet) {
		return nRet;
	}

	if (appDataIns->enable_video || m_hasAudio) {
		m_threadLoop->do_loop();
	}
	return 0;
}

int RTCVideoEngineWrapper::joinRoom() 
{
	if (m_pVideoEngineEx == nullptr) {
		LOG_WARN("rtc 引擎不存在");
		return -1;
	}

	auto appDataIns = AppDataManager::instance()->getAppData();
	if (m_pRtcRoomEx == nullptr) {
		m_pRtcRoomEx = m_pVideoEngineEx->createRTCRoomEx(appDataIns->room_id.c_str());
		m_pRtcRoomEx->setRTCRoomEventHandler(this);
		m_pRtcRoomEx->setRTCRoomEventHandlerEx(this);
	}
	if (m_pRtcRoomEx == nullptr) {
		LOG_WARN("create rtc room failed!");
		return -2;
	}

	bytertc::UserInfo user;
	user.uid = appDataIns->user_id.c_str();
	bytertc::RTCRoomConfig roomConfig;
	roomConfig.is_auto_publish = true;
	roomConfig.is_auto_subscribe_audio = false;
	roomConfig.is_auto_subscribe_video = false;
	std::string token="";
	if (token_requset(appDataIns->room_id,appDataIns->user_id,token)) {
		LOG_INFO("token值:" << token);
	}
	else{
		LOG_ERROR("获取token错误");
	}
	int nRet = m_pRtcRoomEx->joinRoom(token.c_str(), user, roomConfig);
	LOG_INFO("joinRoom 返回 ret=" << nRet);
	if (nRet != 0) {
		LOG_WARN("创建RTC房间错误" << nRet);
		return nRet;
	}
	// 先只发布视频；音频在进房后 push 成功再升级为 Both，避免音频异常拖垮视频
	bytertc::MediaStreamType publishType = bytertc::kMediaStreamTypeVideo;
	if (appDataIns->enable_video) {
		publishType = bytertc::kMediaStreamTypeVideo;
	} else if (m_hasAudio) {
		publishType = bytertc::kMediaStreamTypeAudio;
	} else {
		LOG_WARN("未启用视频且无音频数据，无法发布流");
		return -3;
	}
	m_pRtcRoomEx->publishStream(bytertc::kStreamIndexMain, publishType);

	m_roomJoined = true;
	// 音视频均在 onStart 同时开推，避免 joinRoom→onStart 间隔导致音频先跑 ~1s

	return nRet;
}

int RTCVideoEngineWrapper::destory() 
{
	LOG_INFO("");
	std::lock_guard<std::mutex> locker(m_exitMutex);
	if (m_pVideoEngineEx == nullptr) {
		LOG_WARN("rtc video engine is null");
		return -1;
	}

	m_playbackFinished = true;
	stopAudioPush();
	stopVideoPush();
	m_roomJoined = false;

	if (m_pRtcRoomEx) {
		m_pRtcRoomEx->leaveRoom();
		m_pRtcRoomEx->destroy();
		m_pRtcRoomEx = nullptr;
	}

	m_threadLoop->cancel_loop();
	bytertc::destroyRTCVideo();
	m_pVideoEngineEx = nullptr;
	resetPlaybackState();
	LOG_INFO("RTC 引擎已销毁");
	return 0;
}

static std::string to_string(bytertc::StreamPriority stream_priority) {
	std::string localStreamPriority;
	switch (stream_priority)
	{
	case bytertc::kStreamPriorityLow:
		localStreamPriority = "kStreamPriorityLow";
		break;
	case bytertc::kStreamPriorityNormal:
		localStreamPriority = "kStreamPriorityNormal";
		break;
	case bytertc::kStreamPriorityHigh:
		localStreamPriority = "kStreamPriorityHigh";
		break;
	default:
		break;
	}
	return localStreamPriority;
}

static bool checkFileExtension(const std::string& filename, const std::string& extension)
{
    size_t dotIndex = filename.find_last_of(".");
	std::string ext = extension;
    if (dotIndex != std::string::npos) {
        std::string fileExt = filename.substr(dotIndex + 1);
        std::transform(fileExt.begin(), fileExt.end(), fileExt.begin(), ::tolower);
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
        if (fileExt == ext) {
            return true;
        }
    }
    return false;
}

int RTCVideoEngineWrapper::initVideoConfig()
{
	LOG_INFO("");
	auto appDataIns = AppDataManager::instance()->getAppData();
	if (!appDataIns->enable_video) {
		LOG_INFO("未启用视频功能");
		return 0;
	}
#ifndef WITH_FFMPEG
	LOG_ERROR("读取本地 .mp4 文件需要启用 FFmpeg，请安装 FFmpeg 开发库后重新编译");
	return -1;
#endif
	const auto streamIndex = bytertc::kStreamIndexMain;
	LOG_INFO("********开始初始化主流视频配置*********");

	if (appDataIns->video_file.empty()) {
		LOG_ERROR("video_file 未配置");
		return -1;
	}
	if (!checkFileExtension(appDataIns->video_file, "mp4")) {
		LOG_ERROR("仅支持本地 .mp4 文件，当前路径: " << appDataIns->video_file);
		return -1;
	}

	if (appDataIns->stream_priority >= bytertc::kStreamPriorityLow
		&& appDataIns->stream_priority <= bytertc::kStreamPriorityHigh) {
		m_pVideoEngineEx->setLocalStreamPriority(streamIndex, static_cast<bytertc::StreamPriority>(appDataIns->stream_priority));
		LOG_INFO("设置主流优先级: " << to_string(static_cast<bytertc::StreamPriority>(appDataIns->stream_priority)));
	}

	bytertc::VideoSourceConfig videoSourceConfig;
	videoSourceConfig.content_category = bytertc::kVideoContentCategoryCamera;
	videoSourceConfig.source_type = bytertc::kVideoSourceTypeEncodedWithoutAutoSimulcast;
	m_pVideoEngineEx->setVideoSource(streamIndex, videoSourceConfig);

	m_externalVideoFrameInfo = std::make_shared<StuPushExternalVideoFrameInfo>();
	LOG_INFO("从本地 MP4 文件读取主流视频，文件: " << appDataIns->video_file);
	auto video = new VideoFileSrc(appDataIns->video_file.c_str());
	if (video->totalFrames() == 0 || video->sizeInByte() == 0) {
		LOG_ERROR("无法读取 MP4 文件或文件中无视频帧: " << appDataIns->video_file);
		delete video;
		m_externalVideoFrameInfo.reset();
		return -1;
	}
	m_externalVideoFrameInfo->h264_data = video->getEntireBuffer();
	m_externalVideoFrameInfo->h264_frame_offset = video->getFramesOffset();
	m_externalVideoFrameInfo->h264_frame_size = video->getFramesSize();
	m_externalVideoFrameInfo->h264_frame_is_key = video->getFramesIsKey();
	m_externalVideoFrameInfo->width = video->width();
	m_externalVideoFrameInfo->height = video->height();
	m_externalVideoFrameInfo->fps = static_cast<int>(video->fps());
	m_externalVideoFrameInfo->total_frames = video->totalFrames();
	m_externalVideoFrameInfo->first_key_frame_index = m_externalVideoFrameInfo->firstKeyFrameIndex();
	m_externalVideoFrameInfo->current_frame_index = m_externalVideoFrameInfo->first_key_frame_index;
	LOG_INFO("首个关键帧索引:" << m_externalVideoFrameInfo->first_key_frame_index
		<< " 总帧数:" << m_externalVideoFrameInfo->total_frames);
	m_pVideoEngineEx->setExternalVideoEncoderEventHandler(this);
	delete video;

	if (appDataIns->video_encoder_config) {
		bytertc::VideoEncoderConfig config;
		config.width = appDataIns->video_encoder_config->width;
		config.height = appDataIns->video_encoder_config->height;
		config.frame_rate = appDataIns->video_encoder_config->fps;
		config.max_bitrate = appDataIns->video_encoder_config->max_bitrate;
		LOG_INFO("设置视频编码器宽度:" << config.width << " 高度:" << config.height
			<< " 帧率:" << config.frame_rate << " 最大码率:" << config.max_bitrate);
		m_pVideoEngineEx->setVideoEncoderConfig(&config, 1);
	} else {
		LOG_WARN("视频编码器配置为空！");
	}

	LOG_INFO("********结束初始化主流视频配置*********");
	return 0;
}

int RTCVideoEngineWrapper::initAudioConfig()
{
	auto appDataIns = AppDataManager::instance()->getAppData();
	if (!appDataIns->enable_audio) {
		LOG_INFO("未启用音频推流");
		return 0;
	}
#ifndef WITH_FFMPEG
	LOG_WARN("FFmpeg 未启用，无法从 MP4 提取音频");
	return 0;
#endif
	if (appDataIns->video_file.empty()) {
		return 0;
	}

	LOG_INFO("从 MP4 提取音频轨: " << appDataIns->video_file);
	Mp4AudioSrc audioSrc(appDataIns->video_file.c_str());
	if (!audioSrc.valid()) {
		LOG_WARN("MP4 无可用音频轨，将仅推送视频");
		return 0;
	}

	m_audioPcm = audioSrc.pcm();
	m_audioTotalChunks = audioSrc.totalChunks();
	m_audioCurrentChunk = 0;
	m_hasAudio = true;

	const int srcRet = m_pVideoEngineEx->setAudioSourceType(
		bytertc::AudioSourceType::kAudioSourceTypeExternal);
	if (srcRet < 0) {
		LOG_WARN("setAudioSourceType 失败 ret=" << srcRet << "，将仅推送视频");
		m_hasAudio = false;
		return 0;
	}
	m_audioTimestampUs = 0;
	LOG_INFO("音频 PCM 已加载，共 " << m_audioTotalChunks << " 个 10ms 帧，进房后开始推送");
	alignAudioDurationToVideo();
	return 0;
}

void RTCVideoEngineWrapper::alignAudioDurationToVideo()
{
	if (!m_hasAudio || !m_externalVideoFrameInfo || m_audioPcm.empty()) {
		return;
	}
	const auto &info = m_externalVideoFrameInfo;
	const int fps = info->fps > 0 ? info->fps : 30;
	if (info->total_frames <= 0 || fps <= 0) {
		return;
	}
	const int videoMs = (info->total_frames * 1000) / fps;
	const int targetChunks = (videoMs + 9) / 10;
	const int prevChunks = m_audioTotalChunks;
	if (targetChunks <= prevChunks) {
		LOG_INFO("音画时长: 音频 " << (prevChunks * 10) << "ms, 视频约 " << videoMs << "ms");
		return;
	}
	const size_t needBytes = static_cast<size_t>(targetChunks) * static_cast<size_t>(Mp4AudioSrc::kBytesPer10Ms);
	m_audioPcm.resize(needBytes, 0);
	m_audioTotalChunks = targetChunks;
	LOG_INFO("音频末尾补静音对齐视频: " << prevChunks << " -> " << targetChunks
		<< " 块 (约 " << videoMs << "ms)");
}

void RTCVideoEngineWrapper::startAudioPush()
{
	if (!m_hasAudio || !m_roomJoined || m_audioPushActive) {
		return;
	}
	m_audioPushActive = true;
	m_audioFailCount = 0;
	if (m_audioTimer == nullptr) {
		m_audioTimer = m_threadLoop->addTimer(
			10, std::bind(&RTCVideoEngineWrapper::pushExternalAudioFrame, this), false);
	}
	LOG_INFO("开始推送 MP4 音频（进房后）");
}

void RTCVideoEngineWrapper::stopAudioPush()
{
	m_audioPushActive = false;
	if (m_audioTimer != nullptr) {
		m_threadLoop->delTimer(m_audioTimer);
		m_audioTimer = nullptr;
	}
}

void RTCVideoEngineWrapper::stopVideoPush()
{
	if (m_externalVideoFrameInfo && m_externalVideoFrameInfo->timer) {
		m_threadLoop->delTimer(m_externalVideoFrameInfo->timer);
		m_externalVideoFrameInfo->timer = nullptr;
	}
}

void RTCVideoEngineWrapper::markPlaybackComplete()
{
	if (m_playbackFinished.exchange(true)) {
		return;
	}
	LOG_INFO("影片已播完，自动停止推流");
	stopVideoPush();
	stopAudioPush();
	if (m_pRtcRoomEx && m_roomJoined) {
		m_pRtcRoomEx->unpublishStream(bytertc::kStreamIndexMain, bytertc::kMediaStreamTypeBoth);
	}
}

bool RTCVideoEngineWrapper::isPlaybackFinished() const
{
	return m_playbackFinished.load();
}

int RTCVideoEngineWrapper::maxPlaybackWaitMs() const
{
	if (!m_externalVideoFrameInfo) {
		return 120000;
	}
	const auto &info = m_externalVideoFrameInfo;
	const int fps = info->fps > 0 ? info->fps : 30;
	const int frames = info->total_frames > 0 ? info->total_frames : 300;
	const int playMs = (frames * 1000) / fps;
	return std::max(playMs + 15000, 20000);
}

void RTCVideoEngineWrapper::forceEndPlayback()
{
	markPlaybackComplete();
}

void RTCVideoEngineWrapper::ensureVideoPushStarted()
{
	if (!m_roomJoined || !m_externalVideoFrameInfo) {
		return;
	}
	bool expected = false;
	if (!m_videoPushStarted.compare_exchange_strong(expected, true)) {
		return;
	}
	auto info = m_externalVideoFrameInfo;
	pushExternalEncodedVideoFrame();
	const int fps = info->fps > 0 ? info->fps : 30;
	const int intervalMs = std::max(1, static_cast<int>(1000.0f / fps));
	if (info->timer == nullptr) {
		info->timer = m_threadLoop->addTimer(
			intervalMs,
			std::bind(&RTCVideoEngineWrapper::pushExternalEncodedVideoFrame, this),
			false);
	}
	LOG_INFO("视频推流定时器已启动 intervalMs=" << intervalMs);
}

void RTCVideoEngineWrapper::disableAudioWithFallback(const char *reason)
{
	if (!m_hasAudio && !m_audioPushActive) {
		return;
	}
	LOG_WARN("音频推流已停用: " << (reason ? reason : "unknown") << "，继续仅推送视频");
	stopAudioPush();
	m_hasAudio = false;
	m_audioPublished = false;
	m_audioFailCount = 0;

	auto appDataIns = AppDataManager::instance()->getAppData();
	if (m_pRtcRoomEx != nullptr && appDataIns->enable_video && m_roomJoined) {
		m_pRtcRoomEx->publishStream(bytertc::kStreamIndexMain, bytertc::kMediaStreamTypeVideo);
	}
}

void RTCVideoEngineWrapper::pushExternalAudioFrame()
{
	if (m_playbackFinished.load()) {
		return;
	}
	if (!m_audioPushActive || !m_roomJoined || !m_hasAudio || m_audioPcm.empty()
		|| m_audioTotalChunks <= 0 || m_pVideoEngineEx == nullptr) {
		return;
	}
	const bool videoStillPlaying = m_externalVideoFrameInfo
		&& m_externalVideoFrameInfo->current_frame_index < m_externalVideoFrameInfo->total_frames;
	const bool audioExhausted = m_audioCurrentChunk >= m_audioTotalChunks;
	if (audioExhausted && !videoStillPlaying) {
		return;
	}

	static const uint8_t kSilencePcm[Mp4AudioSrc::kBytesPer10Ms] = {};
	const uint8_t *pcm = kSilencePcm;
	if (!audioExhausted) {
		const size_t offset = static_cast<size_t>(m_audioCurrentChunk) * static_cast<size_t>(Mp4AudioSrc::kBytesPer10Ms);
		if (offset + static_cast<size_t>(Mp4AudioSrc::kBytesPer10Ms) > m_audioPcm.size()) {
			return;
		}
		pcm = m_audioPcm.data() + offset;
	}

	bytertc::AudioFrameBuilder builder;
	builder.data = const_cast<uint8_t *>(pcm);
	builder.data_size = Mp4AudioSrc::kBytesPer10Ms;
	builder.sample_rate = bytertc::kAudioSampleRate48000;
	builder.channel = bytertc::kAudioChannelStereo;
	builder.timestamp_us = m_audioTimestampUs;
	builder.deep_copy = true;

	auto frame = bytertc::buildAudioFrame(builder);
	if (!frame) {
		LOG_ERROR("buildAudioFrame 失败");
		if (++m_audioFailCount >= kAudioFailThreshold) {
			disableAudioWithFallback("buildAudioFrame 连续失败");
		}
		return;
	}
	const int nRet = m_pVideoEngineEx->pushExternalAudioFrame(frame);
	if (nRet != 0) {
		// -3: kReturnStatusWrongState，常见于未进房或已退房
		if (++m_audioFailCount >= kAudioFailThreshold) {
			disableAudioWithFallback("pushExternalAudioFrame 连续失败");
		} else if (m_audioFailCount == 1) {
			LOG_WARN("pushExternalAudioFrame 失败 ret=" << nRet
				<< "（-3 表示状态不允许，将重试；持续失败则仅保留视频）");
		}
		return;
	}

	m_audioFailCount = 0;
	m_audioTimestampUs += 10000;

	auto appDataIns = AppDataManager::instance()->getAppData();
	if (!m_audioPublished && m_pRtcRoomEx != nullptr && appDataIns->enable_video) {
		const int pubRet = m_pRtcRoomEx->publishStream(
			bytertc::kStreamIndexMain, bytertc::kMediaStreamTypeBoth);
		if (pubRet == 0) {
			m_audioPublished = true;
			LOG_INFO("音频推送正常，已升级为音视频同发");
		} else {
			LOG_WARN("升级为音视频同发失败 ret=" << pubRet << "，继续仅发布视频流");
		}
	}

	m_audioCurrentChunk++;
}

void RTCVideoEngineWrapper::pushExternalEncodedVideoFrame()
{
	if (m_playbackFinished.load()) {
		return;
	}
	if (!m_externalVideoFrameInfo) {
		LOG_WARN("external video frame info is null");
		return;
	}
	auto info = m_externalVideoFrameInfo;

	uint8_t* data = info->h264_data.data() + info->h264_frame_offset[info->current_frame_index];
	int size = info->h264_frame_size[info->current_frame_index];
	bool is_idr = info->h264_frame_is_key[info->current_frame_index];

	if (data == nullptr || size == 0) {
		LOG_ERROR("error, frame data is null");
		return;
	}

	bytertc::EncodedVideoFrameBuilder builder;
	builder.codec_type = bytertc::kVideoCodecTypeH264;
	builder.picture_type = is_idr ? bytertc::kVideoPictureTypeI : bytertc::kVideoPictureTypeP;
	builder.rotation = bytertc::kVideoRotation0;
	builder.data = (uint8_t*)data;
	builder.size = size;
	builder.width = info->width;
	builder.height = info->height;
	const int fps = info->fps > 0 ? info->fps : 30;
	int relFrame = info->current_frame_index - info->first_key_frame_index;
	if (relFrame < 0) {
		relFrame = 0;
	}
	const int64_t frameTsUs = static_cast<int64_t>(relFrame) * 1000000LL / fps;
	builder.timestamp_us = frameTsUs;
	builder.timestamp_dts_us = frameTsUs;
	builder.memory_deleter = [](uint8_t* data, int size, void* user_opaque) -> int{ return 0; };

	// LOG_INFO("frameType:" << (is_idr?"I":"P") << " index:" << m_videoFileSrc->index() << " size:" << size);
	
	bytertc::IEncodedVideoFrame* pFrame = bytertc::buildEncodedVideoFrame(builder);
	if (pFrame == nullptr) {
		LOG_ERROR("build frame error");
		return;
	}


	auto nRet = m_pVideoEngineEx->pushExternalEncodedVideoFrame(bytertc::kStreamIndexMain, 0, pFrame);
	if (nRet != 0) {
		LOG_ERROR("m_pVideoEngine->pushExternalEncodedVideoFrame() error, nRet=" << nRet);
	}
	info->current_frame_index++;
	if (info->current_frame_index >= info->total_frames) {
		markPlaybackComplete();
	}
}

void RTCVideoEngineWrapper::onRoomStateChanged(const char * room_id, const char * uid, int state, const char * extra_info)
{
	std::string roomId = room_id ? room_id : "";
	std::string userId = uid ? uid : "";
	std::string extraInfo = extra_info ? extra_info : "";
	LOG_INFO("[callback] roomid: " << room_id << " userid: " << userId << " state: " << state << " extra_info: " << extraInfo);
	// 注意：本 SDK 进房成功回调常为 state=0 且 extra_info 含 "elapsed"，勿当作离开房
}

void RTCVideoEngineWrapper::onWarning(int warn)
{
	LOG_INFO("[callback] warn:" << warn);
}

void RTCVideoEngineWrapper::onError(int err)
{
	LOG_INFO("[callback] err:" << err);
}

void RTCVideoEngineWrapper::onLeaveRoom(const bytertc::RtcRoomStats & stats)
{
	LOG_INFO("[callback]");
	stopAudioPush();
	m_roomJoined = false;
	m_audioPublished = false;
}

void RTCVideoEngineWrapper::onRoomStats(const bytertc::RtcRoomStats & stats)
{
	//LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onUserJoined(const bytertc::UserInfo & userInfo, int elapsed)
{
	std::string userId = userInfo.uid ? userInfo.uid : "";
	LOG_INFO("[callback] userid: " << userId << " elapsed: " <<elapsed);
}

void RTCVideoEngineWrapper::onUserLeave(const char * uid, bytertc::UserOfflineReason reason)
{
	std::string userId = uid ? uid : "";
	LOG_INFO("[callback] userid: " << userId << " reason: " <<reason);
}

//void RTCVideoEngineWrapper::onUserPublishStream(const char * uid, bytertc::MediaStreamType type)
//{
//	std::string userId = uid ? uid : "";
//	LOG_INFO("[callback] uid: " << userId << " type: "<<type);
//}

//void RTCVideoEngineWrapper::onUserUnpublishStream(const char * uid, bytertc::MediaStreamType type, bytertc::StreamRemoveReason reason)
//{
//	std::string userId = uid ? uid : "";
//	LOG_INFO("[callback] uid: " << userId << " type: " << type << " reason: " << reason);
//}

void RTCVideoEngineWrapper::onUserPublishScreen(const char * uid, bytertc::MediaStreamType type)
{
	std::string userId = uid ? uid : "";
	LOG_INFO("[callback] uid: " << userId << " type: " << type);
}

void RTCVideoEngineWrapper::onUserUnpublishScreen(const char * uid, bytertc::MediaStreamType type, bytertc::StreamRemoveReason reason)
{
	std::string userId = uid ? uid : "";
	LOG_INFO("[callback] uid: " << userId << " type: " << type << " reason: " << reason);
}

void RTCVideoEngineWrapper::onStreamRemove(const bytertc::MediaStreamInfo & bs, bytertc::StreamRemoveReason reason)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onStreamAdd(const bytertc::MediaStreamInfo & stream)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onStreamSubscribed(bytertc::SubscribeState stateCode, const char * stream_id, const bytertc::SubscribeConfig & info)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onStreamPublishSuccess(const char * user_id, bool is_screen)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onRoomMessageReceived(const char * uid, const char * message)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onRoomBinaryMessageReceived(const char * uid, int size, const uint8_t * message)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onUserMessageReceived(const char * uid, const char * message)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onUserBinaryMessageReceived(const char * uid, int size, const uint8_t * message)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onRoomMessageSendResult(int64_t msgid, int error)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onUserMessageSendResult(int64_t message_id, int error)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onUserPublishStream(const bytertc::RemoteStreamKey & stream_key, bool is_screen, bytertc::MediaStreamType type)
{
	std::string roomId = stream_key.room_id ? stream_key.room_id : "";
	std::string userId = stream_key.user_id ? stream_key.user_id : "";
	LOG_INFO("[callback] roomId: " << roomId <<" userId:" <<userId 
		<< " stream_index:" << stream_key.stream_index <<" type: "<<type);
}

void RTCVideoEngineWrapper::onUserUnpublishStream(const bytertc::RemoteStreamKey & stream_key, bytertc::MediaStreamType type, bytertc::StreamRemoveReason reason)
{
	std::string roomId = stream_key.room_id ? stream_key.room_id : "";
	std::string userId = stream_key.user_id ? stream_key.user_id : "";
	LOG_INFO("[callback] roomId: " << roomId << " userId:" << userId
		<< "stream_index:" << stream_key.stream_index << " type: " << type << " reason:" << reason);
}

void RTCVideoEngineWrapper::onStreamStateChanged(const bytertc::StreamKey & stream_key, int state, const char * extra_info)
{
	std::string roomId = stream_key.room_id ? stream_key.room_id : "";
	std::string userId = stream_key.user_id ? stream_key.user_id : "";
	std::string extraInfo = extra_info ? extra_info : "";
	LOG_INFO("[callback] roomId: " << roomId << " userId:" << userId
		<< "stream_index:" << stream_key.stream_index << " state: " << state << " extra_info:" << extraInfo);
}

void RTCVideoEngineWrapper::onAudioFrameSendStateChanged(const bytertc::StreamKey & stream_key, const char * meta_data, bytertc::FirstFrameSendState state)
{
	std::string roomId = stream_key.room_id ? stream_key.room_id : "";
	std::string userId = stream_key.user_id ? stream_key.user_id : "";
	std::string strMetadata = meta_data ? meta_data : "";
	LOG_INFO("[callback] roomId: " << roomId << " userId:" << userId
		<< "stream_index:" << stream_key.stream_index << " meta_data:" << strMetadata << " state: " << state );
}

void RTCVideoEngineWrapper::onVideoFrameSendStateChanged(const bytertc::StreamKey & stream_key, const char * meta_data, bytertc::FirstFrameSendState state)
{
	std::string roomId = stream_key.room_id ? stream_key.room_id : "";
	std::string userId = stream_key.user_id ? stream_key.user_id : "";
	std::string strMetadata = meta_data ? meta_data : "";
	LOG_INFO("[callback] roomId: " << roomId << " userId:" << userId
		<< "stream_index:" << stream_key.stream_index << " meta_data:" << strMetadata << " state: " << state);
}

void RTCVideoEngineWrapper::onAudioFramePlayStateChanged(const bytertc::StreamKey & stream_key, const char * meta_data, bytertc::FirstFramePlayState state)
{
	std::string roomId = stream_key.room_id ? stream_key.room_id : "";
	std::string userId = stream_key.user_id ? stream_key.user_id : "";
	std::string strMetadata = meta_data ? meta_data : "";
	LOG_INFO("[callback] roomId: " << roomId << " userId:" << userId
		<< "stream_index:" << stream_key.stream_index << " meta_data:" << strMetadata << " state: " << state);
}

void RTCVideoEngineWrapper::onVideoFramePlayStateChanged(const bytertc::StreamKey & stream_key, const char * meta_data, bytertc::FirstFramePlayState state)
{
	std::string roomId = stream_key.room_id ? stream_key.room_id : "";
	std::string userId = stream_key.user_id ? stream_key.user_id : "";
	std::string strMetadata = meta_data ? meta_data : "";
	LOG_INFO("[callback] roomId: " << roomId << " userId:" << userId
		<< "stream_index:" << stream_key.stream_index << " meta_data:" << strMetadata << " state: " << state);
}

void RTCVideoEngineWrapper::onConnectionStateChanged(bytertc::ConnectionState state)
{
	LOG_INFO("[callback] state: "<<state);
}

void RTCVideoEngineWrapper::onPerformanceAlarms(bytertc::PerformanceAlarmMode mode, const char * room_id, bytertc::PerformanceAlarmReason reason, const bytertc::SourceWantedData & data)
{
	LOG_INFO("[callback]");
}

void RTCVideoEngineWrapper::onLocalAudioStateChanged(bytertc::LocalAudioStreamState state, bytertc::LocalAudioStreamError error)
{
	LOG_INFO("[callback] state: "<<state << " error: "<< error);
}

void RTCVideoEngineWrapper::onRemoteAudioStateChanged(const bytertc::RemoteStreamKey & key, bytertc::RemoteAudioState state, bytertc::RemoteAudioStateChangeReason reason)
{
	std::string roomId = key.room_id ? key.room_id : "";
	std::string userId = key.user_id ? key.user_id : "";
	LOG_INFO("[callback] roomId: "<<roomId << " userId: "<< userId<<" index: "<<key.stream_index << " state: "<<state <<" reason: " << reason);
}

void RTCVideoEngineWrapper::onFirstLocalVideoFrameCaptured(bytertc::StreamIndex index, bytertc::VideoFrameInfo info)
{
	LOG_INFO("[callback] index: " << index << " width: "<<info.width <<" height: "<<info.height );
}

void RTCVideoEngineWrapper::onLocalVideoSizeChanged(bytertc::StreamIndex index, const bytertc::VideoFrameInfo & info)
{
	LOG_INFO("[callback] index: " << index << " width: "<<info.width <<" height: "<<info.height );
}

void RTCVideoEngineWrapper::onRemoteVideoSizeChanged(bytertc::RemoteStreamKey key, const bytertc::VideoFrameInfo & info)
{
	std::string roomId = key.room_id ? key.room_id : "";
	std::string userId = key.user_id ? key.user_id : "";
	LOG_INFO("[callback] roomId: " << roomId << " userId: " << userId << " index: " << key.stream_index << " width: " << info.width << " height: " <<  info.height);
}

void RTCVideoEngineWrapper::onFirstRemoteVideoFrameRendered(const bytertc::RemoteStreamKey key, const bytertc::VideoFrameInfo & info)
{
	std::string roomId = key.room_id ? key.room_id : "";
	std::string userId = key.user_id ? key.user_id : "";
	LOG_INFO("[callback] roomId: " << roomId << " userId: " << userId << " index: " << key.stream_index << " width: " << info.width << " height: " << info.height);
}

void RTCVideoEngineWrapper::onFirstRemoteVideoFrameDecoded(const bytertc::RemoteStreamKey key, const bytertc::VideoFrameInfo & info)
{
	std::string roomId = key.room_id ? key.room_id : "";
	std::string userId = key.user_id ? key.user_id : "";
	LOG_INFO("[callback] roomId: " << roomId << " userId: " << userId << " index: " << key.stream_index << " width: " << info.width << " height: " << info.height);
}

void RTCVideoEngineWrapper::onMediaDeviceWarning(const char * device_id, bytertc::MediaDeviceType device_type, bytertc::MediaDeviceWarning device_warning)
{
	std::string strDevId = device_id ? device_id : "";
	LOG_INFO("[callback] device_id: " << strDevId << " device_type: " << device_type << " device_warning: " << device_warning);
}

void RTCVideoEngineWrapper::onAudioDeviceStateChanged(const char * device_id, bytertc::RTCAudioDeviceType device_type, bytertc::MediaDeviceState device_state, bytertc::MediaDeviceError device_error)
{
	std::string strDevId = device_id ? device_id : "";
	LOG_INFO("[callback] device_id:" << strDevId << " device_type: " << device_type << " device_state: " << device_state << " device_error: " << device_error);
}

void RTCVideoEngineWrapper::onVideoDeviceStateChanged(const char * device_id, bytertc::RTCVideoDeviceType device_type, bytertc::MediaDeviceState device_state, bytertc::MediaDeviceError device_error)
{
	std::string strDevId = device_id ? device_id : "";
	LOG_INFO("[callback] device_id:" << strDevId << " device_type: " << device_type << " device_state: " << device_state << " device_error: " << device_error);
}

RTCVideoEngineWrapper *RTCVideoEngineWrapper::instance()
{
	static RTCVideoEngineWrapper ins;
	return &ins;
}


void RTCVideoEngineWrapper::onStart(bytertc::StreamIndex streamIndex)
{
	if (streamIndex != bytertc::kStreamIndexMain || !m_externalVideoFrameInfo) {
		return;
	}
	m_roomJoined = true;
	m_audioCurrentChunk = 0;
	m_audioTimestampUs = 0;
	ensureVideoPushStarted();
	auto appDataIns = AppDataManager::instance()->getAppData();
	if (m_hasAudio && appDataIns->enable_audio) {
		startAudioPush();
	}
	LOG_INFO("[callback] onStart 音画同步起点");
}

void RTCVideoEngineWrapper::onStop(bytertc::StreamIndex streamIndex)
{
	if (streamIndex != bytertc::kStreamIndexMain || !m_externalVideoFrameInfo) {
		return;
	}
	auto info = m_externalVideoFrameInfo;
	if (info->timer) {
		m_threadLoop->delTimer(info->timer);
		info->timer = nullptr;
	}
	LOG_INFO("[callback] onStop");
}

void RTCVideoEngineWrapper::onRateUpdate(bytertc::StreamIndex index, int32_t video_index, bytertc::VideoRateInfo info)
{
	LOG_INFO("[callback] onRateUpdate");
}

void RTCVideoEngineWrapper::onRequestKeyFrame(bytertc::StreamIndex index, int32_t video_index)
{
	if (m_playbackFinished.load()) {
		return;
	}
	if (index != bytertc::kStreamIndexMain || !m_externalVideoFrameInfo) {
		return;
	}
	auto info = m_externalVideoFrameInfo;
	// 新观众进房会触发关键帧请求；回退到历史 I 帧会改变推流时间线，导致已在观看的用户画面跳变。
	// 保持当前播放进度：仅当当前帧已是关键帧时补发，否则等待定时器自然推到下一个 GOP（与音频一致）。
	if (!info->h264_frame_is_key[info->current_frame_index]) {
		LOG_INFO("[callback] onRequestKeyFrame ignored, wait natural GOP at index "
			<< info->current_frame_index);
		return;
	}
	LOG_INFO("[callback] onRequestKeyFrame, push current key frame index:" << info->current_frame_index);
	pushExternalEncodedVideoFrame();
}

void RTCVideoEngineWrapper::onActiveVideoLayer(bytertc::StreamIndex index, int32_t video_index, bool active)
{
	LOG_INFO("[callback] onActiveVideoLayer");
}
