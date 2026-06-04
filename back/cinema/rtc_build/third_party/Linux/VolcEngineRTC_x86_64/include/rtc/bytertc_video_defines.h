/*
 * Copyright (c) 2022 The VolcEngineRTC project authors. All Rights Reserved.
 * @brief VolcEngineRTC Video Defines
 */

#pragma once

#include "bytertc_rts_defines.h"
#include "bytertc_video_frame.h"

namespace bytertc {
/** {zh}
 * @type keytype
 * @brief 渲染模式
 */
/** {en}
 * @type keytype
 * @brief Rendering mode
 */
enum RenderMode {
    /** {zh}
     * @brief 视窗填满优先，默认值。
     *        视频帧等比缩放，直至视窗被视频填满。如果视频帧长宽比例与视窗不同，视频帧的多出部分将无法显示。
     *        缩放完成后，视频帧的一边长和视窗的对应边长一致，另一边长大于等于视窗对应边长。
     */
    /** {en}
     * @brief (Default) Fill and Crop.
     *        The video frame is scaled with fixed aspect ratio, and completely fills the canvas. The region of the video exceeding the canvas will be cropped. <br>
     */
    kRenderModeHidden = 1,
    /** {zh}
     * @brief 视频帧内容全部显示优先。
     *        视频帧等比缩放，直至视频帧能够在视窗上全部显示。如果视频帧长宽比例与视窗不同，视窗上未被视频帧填满区域将被涂黑。
     *        缩放完成后，视频帧的一边长和视窗的对应边长一致，另一边长小于等于视窗对应边长。
     */
    /** {en}
     * @brief Fit.
     *        The video frame is scaled with fixed aspect ratio, and is shown completely in the canvas. The region of the canvas not filled with video frame, is filled with `background`.
     */
    kRenderModeFit = 2,
    /** {zh}
     *  @brief 视频帧自适应画布。
     *         视频帧非等比缩放，直至画布被填满。在此过程中，视频帧的长宽比例可能会发生变化。
     */
   /** {en}
     *  @brief Fill the canvas.
     *         The video frame is scaled to fill the canvas. During the process, the aspect ratio may change.
     */
    kRenderModeFill = 3,
};

/** {zh}
 * @type keytype
 * @brief 订阅媒体的类型
 */
/** {en}
 * @type keytype
 * @brief Type of the media stream subscribed to
 */
enum SubscribeMediaType {
    /** {zh}
     * @brief 既不订阅音频，也不订阅视频
     */
    /** {en}
     * @brief Neither audio nor video
     */
    kRTCSubscribeMediaTypeNone = 0,
    /** {zh}
     * @brief 只订阅音频，不订阅视频
     */
    /** {en}
     * @brief Audio only
     */
    kRTCSubscribeMediaTypeAudioOnly,
    /** {zh}
     * @brief 只订阅视频，不订阅音频
     */
    /** {en}
     * @brief Video only
     */
    kRTCSubscribeMediaTypeVideoOnly,
    /** {zh}
     * @brief 同时订阅音频和视频
     */
    /** {en}
     * @brief Video only
     */
    kRTCSubscribeMediaTypeVideoAndAudio
};

/** {zh}
 * @type keytype
 * @brief 暂停/恢复接收远端的媒体流类型。
 */
/** {en}
 * @type keytype
 * @brief Type of the stream to be paused/resumed.
 */
enum PauseResumeControlMediaType {
    /** {zh}
     * @brief 只控制音频，不影响视频
     */
    /** {en}
     * @brief Audio only
     */
    kRTCPauseResumeControlMediaTypeAudio = 0,
    /** {zh}
     * @brief 只控制视频，不影响音频
     */
    /** {en}
     * @brief Video only
     */
    kRTCPauseResumeControlMediaTypeVideo = 1,
    /** {zh}
     * @brief 同时控制音频和视频
     */
    /** {en}
     * @brief Both video and audio
     */
    kRTCPauseResumeControlMediaTypeVideoAndAudio = 2
};

/** {zh}
 * @type keytype
 * @brief 时域分层定义
 */
/** {en}
 * @type keytype
 * @brief  Time domain hierarchical definition
 */
enum SVCLayer {
    /** {zh}
    * @brief 不指定分层(默认值）
    */
   /** {en}
    * @brief No hierarchy specified (default)
    */
    kSVCLayerDefault = 0,
    /** {zh}
     * @brief T0层
     */
    /** {en}
     * @brief T0 layer
     */
    kSVCLayerBase = 1,
    /** {zh}
     * @brief T0+T1层
     */
    /** {en}
     * @brief T0 + T1 layer
     */
    kSVCLayerMain = 2,
    /** {zh}
     * @brief T0+T1+T2层
     */
    /** {en}
     * @brief T0 + T1 + T2 layer
     */
    kSVCLayerHigh = 3,
};

/** {zh}
 * @type keytype
 * @brief 流切换信息。本地用户订阅的远端流触发回退策略时的流切换信息。
 */
/** {en}
 * @type keytype
 * @brief Information of stream switching due to a Fallback
 */
struct RemoteStreamSwitch {
    /** {zh}
     * @brief 订阅的音视频流的发布者的用户 ID。
     */
    /** {en}
     * @brief User ID of the publisher of the subscribed media stream
     */
    const char* uid;
    /** {zh}
     * @brief 是否是屏幕流。
     */
    /** {en}
     * @brief Whether it is a screen-sharing stream
     */
    bool is_screen;
    /** {zh}
     * @brief 流切换前本地用户订阅的视频流的分辨率对应的索引。
     */
    /** {en}
     * @brief Index corresponding to the resolution of the subscribed video stream before the stream switch.
     */
    int before_video_index;
    /** {zh}
     * @brief 流切换后本地用户订阅的视频流的分辨率对应的索引。
     */
    /** {en}
     * @brief Index corresponding to the resolution of the subscribed video stream after the stream switch.
     */
    int after_video_index;
    /** {zh}
     * @brief 流切换前是否有视频流。
     */
    /** {en}
     * @brief Is there a video stream before switching.
     */
    bool before_enable;
    /** {zh}
     * @brief 流切换后是否有视频流。
     */
    /** {en}
     * @brief Is there a video stream after switching.
     */
    bool after_enable;
    /** {zh}
     * @brief 触发流回退的原因，详见类型 FallbackOrRecoverReason{@link #FallbackOrRecoverReason} 。
     */
    /** {en}
     * @brief Refer to FallbackOrRecoverReason{@link #FallbackOrRecoverReason} for the reason of the Fallback or reverting from the Fallback of the subscribed stream.
     */
    FallbackOrRecoverReason reason;
};

/** {zh}
 * @type keytype
 * @brief 背景模式
 */
/** {en}
 * @type keytype
 * @brief Background mode
 */
enum BackgroundMode {
    /** {zh}
     *@brief 无
     */
    /** {en}
     *@brief No
     */
    kBackgroundModeNone = 0,
    /** {zh}
     *@brief 虚化
     */
    /** {en}
     *@brief Virtualization
     */
    kBackgroundModeBlur = 1,
    /** {zh}
     *@brief 背景 1
     */
    /** {en}
     *@brief Background 1
     */
    kBackgroundModeA = 2,
    /** {zh}
     *@brief 背景 2
     */
    /** {en}
     *@brief Background 2
     */
    kBackgroundModeB = 3,
};

/** {zh}
 * @type keytype
 * @brief 分割模型
 */
/** {en}
 * @type keytype
 * @brief To split the model
 */
enum DivideMode {
    /** {zh}
     *@brief 自研
     */
    /** {en}
     *@brief Self-research
     */
    kDivideModeNone = 0,
    /**
     *@brief effect
     */
    kDivideModeEffect = 1,
};

/** {zh}
 * @type keytype
 * @brief 流属性。  <br>
 */
/** {en}
 * @type keytype
 * @brief Flow property.   <br>
 */
struct MediaStreamInfo {
    /** {zh}
     * @brief 发布此流的用户 ID 。
     */
    /** {en}
     * @brief The user ID that published this stream.
     */
    const char* user_id;
    /** {zh}
     * @hidden for internal use only
     * @brief 该流的标识 ID，用户内唯一。
     */
    /** {en}
     * @hidden for internal use only
     * @brief The flag of the stream, unique in user scope.
     */
    StreamIndex stream_index;
    /** {zh}
     * @brief 此流是否为共享屏幕流。
     */
    /** {en}
     * @brief Whether this stream is a shared screen stream.
     */
    bool is_screen;
    /** {zh}
     * @brief 此流是否包括视频流。
     */
    /** {en}
     * @brief Whether this stream includes a video stream.
     */
    bool has_video;
    /** {zh}
     * @brief 流是否包括音频流。
     */
    /** {en}
     * @brief Whether the stream includes an audio stream.
     */
    bool has_audio;
    /** {zh}
     * @brief 视频流的属性。  <br>
     *        当远端用户调用 setVideoEncoderConfig{@link #IRTCVideo#setVideoEncoderConfig} 方法发布多个配置的视频流时，此处会包含该用户发布的所有视频流的属性信息。
     *        参看 VideoSolutionDescription{@link #VideoSolutionDescription}。
     */
    /** {en}
     * @brief Properties of the video stream.   <br>
     *        When a remote user calls the setVideoEncoderConfig{@link #IRTCVideo#setVideoEncoderConfig} method to publish multiple configured video streams, this will contain attribute information for all video streams published by the user.
     *        See VideoSolutionDescription{@link #VideoSolutionDescription}.
     */
    VideoSolutionDescription* profiles;
    /** {zh}
     * @brief 不同配置流的个数。  <br>
     *        当远端用户调用 setVideoEncoderConfig{@link #IRTCVideo#setVideoEncoderConfig} 方法发布多个配置的视频流时，此处会包含该用户发布的视频流的数目。
     */
    /** {en}
     * @brief Number of different configuration streams.   <br>
     *        When a remote user calls the setVideoEncoderConfig{@link #IRTCVideo#setVideoEncoderConfig} method to publish multiple configured video streams, this contains the number of video streams published by the user.
     */
    int profile_count;

    /** {zh}
     * @brief 最大视频流的属性。  <br>
     *        当远端用户开启带通道划分的大小流时，回调最大视频流属性信息。用户可以使用新的订阅方式，订阅任意不超过该分辨率的流。
     *        最终接收到的流，会受房间内其他用户的订阅行为的影响，综合确定一个最接近用户请求的分辨率的流。
     */
    /** {en}
     * @brief Properties of the maximum video stream.   <br>
     *        When a remote user publishes multiple configured video streams, this will contain the maximum attribute information . user with new subscribe call can require any stream does not exceed this resolution.
     *        The final stream received, influenced by the others in room, server would diliver the closest to the resolution requested by the user。
     *
     */
    VideoSolutionDescription max_profile;
};

/** {zh}
 * @type keytype
 * @brief 视频订阅配置信息
 */
/** {en}
 * @type keytype
 * @brief  Video subscription configuration information
 */
struct SubscribeVideoConfig {
    /** {zh}
     * @brief 订阅的视频流分辨率下标。  <br>
     *        当远端用户通过调用 setVideoEncoderConfig{@link #IRTCVideo#setVideoEncoderConfig} 方法启动发布多路不同分辨率的视频流时，本地用户需通过此参数指定希望订阅的流。  <br>
     *        默认值为 0，即订阅第一路流。  <br>
     *        如果不想更改之前的设置，可以输入 -1。  <br>
     */
    /** {en}
     * @brief Subscribed video stream resolution subscript.   <br>
     *        In Simulcast mode, use a number to specify the expected quality of the video stream to be subscribed to.  In Simulcast mode, a video has a diversity of encoded qualities that ranking from 0 to 3. Call setVideoEncoderConfig{@link #IRTCVideo#setVideoEncoderConfig} to enable Simulcast mode on the publisher's clients.  <br>
     *         Ranging from -1 to 3<br>
     *         0 (Default): The best quality <br>
     *         -1: Use the previous settings. <br>
     */
    int video_index = 0;
    /** {zh}
     * @brief 远端用户优先级，参看 RemoteUserPriority{@link #RemoteUserPriority}，默认值为 0。
     */
    /** {en}
     * @brief Remote user priority. The default value is 0. Refer to RemoteUserPriority{@link #RemoteUserPriority} for more details.
     */
    int priority = 0;
    /** {zh}
     * @hidden constructor/destructor
     * @brief 构造函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Constructor
     */
    SubscribeVideoConfig() : video_index(0), priority(0) {
    }
    /**
     * @hidden constructor/destructor
     */
    bool operator==(const SubscribeVideoConfig& config) const {
        bool result = video_index == config.video_index && priority == config.priority;
        return result;
    }
    /**
     * @hidden constructor/destructor
     */
    bool operator!=(const SubscribeVideoConfig& config) const {
        bool result = (*this == config);
        return !result;
    }
};

/** {zh}
 * @type keytype
 * @brief 手动订阅流的配置信息。  
 */
/** {en}
 * @type keytype
 * @brief Configuration information for manual subscription flows.  
 */
struct SubscribeConfig {
    /** {zh}
     * @brief 是否是屏幕流（默认为否）。  <br>
     */
    /** {en}
     * @brief Whether it is a screen stream (default is no).   
     */
    bool is_screen = false;
    /** {zh}
     * @brief 是否订阅视频。  <br>
     */
    /** {en}
     * @brief Whether to subscribe to videos.   <br>
     */
    bool sub_video;
    /** {zh}
     * @brief 是否订阅音频。  <br>
     */
    /** {en}
     * @brief Whether to subscribe to audio.   <br>
     */
    bool sub_audio;
    /** {zh}
     * @brief 订阅的视频流分辨率下标。  <br>
     *        用户可以通过调用 setVideoEncoderConfig{@link #IRTCVideo#setVideoEncoderConfig} 方法在一路流中发布多个不同分辨率的视频。因此订阅流时，需要指定订阅的具体分辨率。此参数即用于指定需订阅的分辨率的下标，默认值为 0 。  <br>
     */
    /** {en}
     * @brief Subscribed video stream resolution subscript.   <br>
     *        Users can publish multiple videos of different resolutions in a stream by calling the setVideoEncoderConfig{@link #IRTCVideo#setVideoEncoderConfig} method. Therefore, when subscribing to a stream, you need to specify the specific resolution of the subscription. This parameter is used to specify the subscript of the resolution to be subscribed to, and the default value is 0. <br>
     */
    int video_index;
    /** {zh}
     * @brief 远端用户的需求优先级，参看 RemoteUserPriority{@link #RemoteUserPriority}，默认值为 0 。  <br>
     *        当开启了订阅流回退选项功能（详见 setSubscribeFallbackOption{@link #IRTCVideo#setSubscribeFallbackOption} 方法），弱网或性能不足时会优先保证收到的高优先级用户的流的质量。  <br>
     */
    /** {en}
     * @brief For the remote user's requirement priority. See RemoteUserPriority{@link #RemoteUserPriority}, the default value is 0. <br>
     *         When the subscription flow fallback option function is turned on (see setSubscribeFallbackOption{@link #IRTCVideo#setSubscribeFallbackOption} method for details), weak connections or insufficient performance will give priority to ensuring the quality of the received high-priority user's flow. <br>
     */
    int priority = 0;
    /** {zh}
     * @brief 远端用户的时域分层，参看 SVCLayer{@link #SVCLayer}，默认值为 0 。  <br>
     *        仅码流支持SVC特性时可以生效。  <br>
     */
    /** {en}
     * @brief The time domain hierarchy of the remote user. See SVCLayer{@link #SVCLayer}, the default value is 0. <br>
     *         This only works if the stream supports the SVC feature. <br>
     */
    int svc_layer = 0;
    /** {zh}
     * @brief 期望订阅的最高帧率，单位：fps，默认值为 0，设为大于 0 的值时开始生效。  <br>
     *        当发布端帧率低于设定帧率，或订阅端开启性能回退后下行弱网，则帧率会相应下降。  <br>
     *        仅码流支持 SVC 分级编码特性时方可生效。
     */
    /** {en}
     * @brief Expected maximum frame rate of the subscribed stream in fps. The default value is 0, values greater than 10 are valid.  <br>
     *        If the frame rate of the stream published is lower than the value you set, or if your subscribed stream falls back under limited network conditions, the frame rate you set will drop accordingly.  <br>
     *        Only valid if the stream is coded with SVC technique.
     */
    int framerate = 0;
    /** {zh}
     * @brief 用户通过指定UI对应的最合适的流的宽度，单位：px
     */
    /** {en}
     * @brief The user specifies the width(px) of the most appropriate stream corresponding to the UI by specifying
     */
    int sub_width = 0;
    /** {zh}
     * @brief 用户通过指定UI对应的最合适的流的高度，单位：px
     */
    /** {en}
     * @brief The user specifies the height(px) of the most appropriate stream corresponding to the UI by specifying
     */
    int sub_height = 0;
    /**
     * @hidden for internal use only
     */
    int sub_video_index = -1;

public:
    /** {zh}
     * @hidden constructor/destructor
     * @brief 构造函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Constructor
     */
    SubscribeConfig() : is_screen(false), sub_video(true), sub_audio(true), video_index(0), priority(0) {
    }

    /** {zh}
     * @hidden constructor/destructor
     * @brief 构造函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Constructor
     */
    SubscribeConfig(bool is_screen, bool subvideo, bool subaudio, int videoindex)
            : is_screen(is_screen), sub_video(subvideo), sub_audio(subaudio), video_index(videoindex) {
    }

    /** {zh}
     * @hidden constructor/destructor
     * @brief 构造函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Constructor
     */
    SubscribeConfig(bool is_screen, bool subvideo, bool subaudio, int videoindex, int priority)
            : is_screen(is_screen),
              sub_video(subvideo),
              sub_audio(subaudio),
              video_index(videoindex),
              priority(priority) {
    }

    /** {zh}
     * @hidden constructor/destructor
     * @brief 构造函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief constructor
     */
    SubscribeConfig(bool is_screen, bool subvideo, bool subaudio, int videoindex,
     int priority,int svc_layer,int width,int height)
            : is_screen(is_screen),
              sub_video(subvideo),
              sub_audio(subaudio),
              video_index(videoindex),
              priority(priority),
              svc_layer(svc_layer),
              sub_width(width),
              sub_height(height) {
    }
    /**
     * @hidden constructor/destructor
     */
    bool operator==(const SubscribeConfig& config) const {
        // sub_width * sub_height valid
        bool common_result = is_screen == config.is_screen && sub_video == config.sub_video
                             && sub_audio == config.sub_audio && priority == config.priority
                             && svc_layer == config.svc_layer && framerate == config.framerate;
        bool result;
        if(sub_width * sub_height > 0 && config.sub_width * config.sub_height > 0) {
          result = common_result && sub_width == config.sub_width && sub_height == config.sub_height ;
        }  else if((sub_width * sub_height == 0) && (config.sub_width * config.sub_height == 0) ) {
          result = common_result && video_index == config.video_index;
        } else {
          result = false;
        }
        return result;
    }

    /**
     * @hidden constructor/destructor
     */
    bool operator!=(const SubscribeConfig& config) const {
        bool result = (*this == config);
        return !result;
    }
};

/** {zh}
 * @type keytype
 * @brief 远端视频类型
 *      目前C++ sdk 只支持 kVideoStreamTypeHigh 类型
 */
/** {en}
 * @type keytype
 * @brief Remote video type
 *      Currently C++ sdk only supports kVideoStreamTypeHigh type
 */
enum VideoStreamType {
    /** {zh}
     * @brief 高分辨率视频流
     */
    /** {en}
     * @brief High Resolution Video Streaming
     */
    kVideoStreamTypeHigh = 0,
    /** {zh}
     * @brief 低分辨率视频
     */
    /** {en}
     * @brief Low Resolution Video
     */
    kVideoStreamTypeLow = 1,
};

/** {zh}
 * @type keytype
 * @brief 渲染目标类型
 */
/** {en}
 * @type keytype
 * @brief Render target type
 */
enum RenderTargetType {
    /** {zh}
     * @brief 指定渲染目标类型为 SurfaceView/TextureView (Android), UIView(iOS), NSView(macOS), HWND (Windows)
     */
    /** {en}
     * @brief Use this value when the target is in the range of SurfaceView/TextureView for Android, UIView for iOS, NSView for macOS, or HWND for Windows
     */
    kRenderTargetTypeView = 0,
    /** {zh}
     * @brief 仅在 Android 平台生效，指定渲染目标类型为 Surface
     */
    /** {en}
     * @brief Use this value when the target is in the range of Surface for Android
     */
    kRenderTargetTypeSurface = 1,
};

/** {zh}
 * @type keytype
 * @brief 视频帧渲染设置。
 */
/** {en}
 * @type keytype
 * @brief Video rendering configuration.
 */
struct VideoCanvas {
    /** {zh}
     * @brief 本地视图句柄
     */
    /** {en}
     * @brief Local view handle
     */
    void* view = NULL;
    /** {zh}
     * @brief 视频渲染模式，参看 RenderMode{@link #RenderMode}
     */
    /** {en}
     * @brief Video rendering mode. See RenderMode{@link #RenderMode}
     */
    int render_mode = kRenderModeHidden;
    /** {zh}
     * @brief 用于填充画布空白部分的背景颜色。取值范围是 `[0x00000000, 0xFFFFFFFF]`。默认值是 `0x00000000`。其中，透明度设置无效。
     */
    /** {en}
     * @brief Set the background color of the canvas which is not filled with video frame. The range is `[0x00000000, 0xFFFFFFFF]`. The default is `0x00000000`. The Alpha index is ignored.
     */
    uint32_t background_color = 0;
    /** {zh}
     * @brief 渲染目标的类型。参看 RenderTargetType{@link #RenderTargetType}。
     */
    /** {en}
     * @brief See RenderTargetType{@link #RenderTargetType}.
     */
    RenderTargetType render_target_type = kRenderTargetTypeView;
    /** {zh}
     * @brief 视频帧旋转角度。参看 VideoRotation{@link #VideoRotation}。默认为 0 度，即不做旋转处理。<br>
     *        该设置仅对远端视频有效，对本地视频设置不生效。
     */
    /** {en}
     * @brief Video frame rotation angle. See VideoRotation{@link #VideoRotation}. The default value is 0, which means no rotation is applied.<br>
     *        This parameter only applies to remote video and does not affect local video settings.
     */
     VideoRotation render_rotation = kVideoRotation0;
    /** {zh}
     * @hidden constructor/destructor
     * @brief 构造函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Constructor
     */
    VideoCanvas() : view(NULL), render_mode(kRenderModeHidden), background_color(0), render_target_type(kRenderTargetTypeView) {
    }
    /** {zh}
     * @hidden constructor/destructor
     * @brief 构造函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Constructor
     */
    VideoCanvas(void* v, int m, uint32_t c) : view(v), render_mode(m), background_color(c) {
    }
};

/** {zh}
 * @type keytype
 * @brief 远端视频帧渲染设置
 */
/** {en}
 * @type keytype
 * @brief Remote video rendering configuration.
 */
struct RemoteVideoRenderConfig {
    /** {zh}
     * @brief 渲染模式：
     *        + 1（`RENDER_MODE_HIDDEN`）视窗填满优先，默认值。视频帧等比缩放，直至视窗被视频填满。如果视频帧长宽比例与视窗不同，视频帧的多出部分将无法显示。缩放完成后，视频帧的一边长和视窗的对应边长一致，另一边长大于等于视窗对应边长。
     *        + 2（`RENDER_MODE_FIT`）视频帧内容全部显示优先。视频帧等比缩放，直至视频帧能够在视窗上全部显示。如果视频帧长宽比例与视窗不同，视窗上未被视频帧填满区域将填充 `backgroundColor`。缩放完成后，视频帧的一边长和视窗的对应边长一致，另一边长小于等于视窗对应边长。
     *        + 3（`RENDER_MODE_FILL`）视频帧自适应画布。视频帧非等比缩放，直至画布被填满。在此过程中，视频帧的长宽比例可能会发生变化。
     */
    /** {en}
     * @brief Rendering mode.
     *        + 1（`RENDER_MODE_HIDDEN`）Fill and Crop. Default setting. The video frame is scaled with a fixed aspect ratio and completely fills the canvas. The region of the video exceeding the canvas will be cropped.
     *        + 2（`RENDER_MODE_FIT`）Fit. The video frame is scaled with a fixed aspect ratio and is shown completely on the canvas. The region of the canvas not filled with the video frame will be filled with `backgroundColor`.
     *        + 3（`RENDER_MODE_FILL`）Fill the canvas. The video frame is scaled to fill the canvas. During the process, the aspect ratio may change.
     */
    int render_mode = kRenderModeHidden;
    /** {zh}
     * @brief 用于填充画布空白部分的背景颜色。取值范围是 `[0x00000000, 0xFFFFFFFF]`。默认值是 `0x00000000`。其中，透明度设置无效。
     */
    /** {en}
     * @brief Set the background color of the canvas which is not filled with video frame. The range is `[0x00000000, 0xFFFFFFFF]`. The default is `0x00000000`. The Alpha index is ignored.
     */
    uint32_t background_color = 0;

    /** {zh}
     * @brief 用户自定义画面旋转。可选值 0, 90, 180, 270， 默认值是0。其中0代表保持原始画面，90, 180, 270代表顺时针旋转原始canvas相应角度。
     */
    /** {en}
     * @brief User-defined render rotation。the value must be 0, 90, 180. 270, 0 mean keeping origin canvas orientation, 90, 180, and 270 represent clockwise rotation angles of the original canvas.
     */
    VideoRotation render_rotation = kVideoRotation0;
};

/** {zh}
 * @type keytype
 * @brief Windows 窗口 id, Windows 平台下传 Windows 窗口句柄
 */
/** {en}
 * @type keytype
 * @brief Windows window id, Windows platform down to Windows window handle
 */
typedef void* view_t;

/** {zh}
 * @type keytype
 * @brief 矩形区域，用于指定屏幕区域。
 */
/** {en}
 * @type keytype
 * @brief  A rectangle that you can move around and re-size to share just the portion of the screen defined by that rectangle.
 */
struct Rectangle {
    /** {zh}
     * @brief 矩形区域左上角的 x 坐标。
     */
    /** {en}
     * @brief The upper-left X coordinates of the rectangular.
     */
    int x = 0;
    /** {zh}
     * @brief 矩形区域左上角的 y 坐标。
     */
    /** {en}
     * @brief The upper-left Y coordinates of the rectangular.
     */
    int y = 0;
    /** {zh}
     * @brief 矩形宽度。
     */
    /** {en}
     * @brief Width.
     */
    int width = 0;
    /** {zh}
     * @brief 矩形高度。
     */
    /** {en}
     * @brief Height.
     */
    int height = 0;
};

/** {zh}
 * @type keytype
 * @brief 屏幕共享时的边框高亮设置。
 */
/** {en}
 * @type keytype
 * @brief Configure how a border is highlighted when you share your screen.
 */
struct HighlightConfig {
    /** {zh}
     * @brief 是否显示高亮边框，默认显示。
     */
    /** {en}
     * @brief Whether to display a highlighted border. A border is highlighted by default.
     */
    bool enable_highlight = true;
    /** {zh}
     * @brief 边框的颜色, 颜色格式为十六进制 ARGB:  0xAARRGGB。
     */
    /** {en}
     * @brief Color(ARGB format: 0xAARRGGBB).
     */
    uint32_t border_color = 0xFF29CCA3;
    /** {zh}
     * @brief 边框的宽度，单位：像素。
     */
    /** {en}
     * @brief Width(in pixel).
     */
    int border_width = 4;
};

/** {zh}
 * @type keytype
 * @brief 抓取屏幕时排除指定窗口，默认不排除任何窗体。
 */
/** {en}
 * @type keytype
 * @brief  Exclude a specific window when sharing your screen. No window is excluded by default.
 */
struct ScreenFilterConfig {
    /** {zh}
     * @brief 抓取屏幕时排除窗口列表。这个参数仅在抓取屏幕时生效。
     */
    /** {en}
     * @brief The list of windows excluded from screen capture. This parameter only takes effect when sharing your screen.
     */
    view_t* excluded_window_list = nullptr;
   /** {zh}
     * @brief 排除窗口的数量。
     */
    /** {en}
     * @brief The number of windows excluded from screen capture.
     */
    int excluded_window_num = 0;
};

/** {zh}
 * @type keytype
 * @region 屏幕共享
 * @brief 内部采集屏幕视频流时，是否采集鼠标信息。
 */
/** {en}
 * @type keytype
 * @region Screen sharing
 * @brief Whether to capture the mouse cursor when capturing screen streams by RTC.
 */
enum MouseCursorCaptureState {
    /** {zh}
     * @brief 采集鼠标信息。
     */
    /** {en}
     * @brief Yes.
     */
    kMouseCursorCaptureStateOn,
    /** {zh}
     * @brief 不采集鼠标信息。
     */
    /** {en}
     * @brief No.
     */
    kMouseCursorCaptureStateOff,
};

/** {zh}
 * @type keytype
 * @brief 屏幕共享参数
 */
/** {en}
 * @type keytype
 * @brief  Screen sharing parameter
 */
struct ScreenParameters {
    /** {zh}
     * @brief 编码帧率,单位为 fps
     */
    /** {en}
     * @brief Encoded frame rate in fps
     */
    int frame_rate = 15;
    /** {zh} 
     * @brief 屏幕采集编码码率, `-1` 为自动码率, SDK 会根据宽高信息选择合适的码率，单位 kbps
     */
    /** {en} 
     * @brief Encoding bitrate in kbps of the screen-sharing stream. `-1` for self-adapted that SDK will choose the appropriate encoding rate according to the width and height for the stream.
     */
    int kbitrate = -1;
    /** {zh} 
     * @brief 视频最小编码码率, 单位 kbps。编码码率不会低于 `min_kbitrate`。<br>
     *        默认值为 `0`。<br>
     *        范围：[0, kbitrate)，当 `kbitrate` < `min_kbitrate` 时，为适配码率模式。<br>
     *        以下情况，设置本参数无效：<br>
     *        + 当 `kbitrate` 为 `0` 时，不对视频流进行编码发送。<br>
     *        + 当 `kbitrate` < `0` 时，适配码率模式。
     */
    /** {en} 
     * @brief Minimum video encoding bitrate in kbps. The encoding bitrate will not be lower than the `min_kbitrate`.<br>
     *        It defaults to `0`. <br>
     *        It ranges within [0, kbitrate). When `bitrate` < `min_kbitrate`, the bitrate is self-adpapted.<br>
     *        In the following circumstance, the assignment to this variable has no effect:<br>
     *        + When `min_kbitrate` = `0`, the video encoding is disabled.<br>
     *        + When `min_kbitrate` < `0`, the bitrate is self-adapted.
     */
    int min_kbitrate = 0;
};

/** {zh}
 * @type keytype
 * @region 屏幕共享
 * @brief 内部采集屏幕视频流的内容类型。
 */
/** {en}
 * @type keytype
 * @region Screen sharing
 * @brief Content hints of the internally captured screen video stream.
 */
enum ContentHint {
    /** {zh}
     * @brief 细节内容。当共享文档、图片时，建议使用该内容类型。默认值。
     */
    /** {en}
     * @brief Detailed content. Recommended when you capture documents, images, etc. Default value.
     */
    kContentHintDetails = 0,
    /** {zh}
     * @brief 动画内容。当共享视频、游戏时，建议使用该内容类型。
     */
    /** {en}
     * @brief  Animation content. Recommended when you capture videos, games, etc.
     */
    kContentHintMotion,
};

/** {zh}
 * @type keytype
 * @brief 屏幕共享内部采集参数
 */
/** {en}
 * @type keytype
 * @brief  Screen internal capture parameters
 */
struct ScreenCaptureParameters {
    /** {zh}
     * @brief 采集区域，参看 Rectangle{@link #Rectangle}。
     */
    /** {en}
     * @brief Collection area. See Rectangle{@link #Rectangle}.
     */
    Rectangle region_rect;
    /** {zh}
     * @brief 是否采集鼠标状态，参看 MouseCursorCaptureState{@link #MouseCursorCaptureState}。
     */
    /** {en}
     * @brief To collect mouse status. See MouseCursorCaptureState{@link #MouseCursorCaptureState}.
     */
    MouseCursorCaptureState capture_mouse_cursor = MouseCursorCaptureState::kMouseCursorCaptureStateOn;
    /** {zh}
     * @brief 屏幕过滤设置，填写不需要采集的窗口 ID，参看 ScreenFilterConfig{@link #ScreenFilterConfig}。
     */
    /** {en}
     * @brief Screen filtering settings. Provide ID of the windows to be excluded. See ScreenFilterConfig{@link #ScreenFilterConfig}.
     */
    ScreenFilterConfig filter_config;
    /** {zh}
     * @brief 采集区域的边框高亮设置，参看 HighlightConfig{@link #HighlightConfig}。
     */
    /** {en}
     * @brief Settings for highlighting borders of the sharing region. See HighlightConfig{@link #HighlightConfig}.
     */
    HighlightConfig highlight_config;
};

/** {zh}
 * @type keytype
 * @brief 屏幕共享的编码参数配置。
 */
/** {en}
 * @type keytype
 * @brief  The encoding configuration for screen sharing.
 */
struct DesktopCaptureParameters {
    /** {zh}
     * @brief 屏幕采集编码最大宽度，单位 px。
     */
    /** {en}
     * @brief The maximum width(in px).
     */
    int max_width = 1920;
    /** {zh}
     * @brief 屏幕采集编码最大高度，单位 px。
     */
    /** {en}
     * @brief The maximum height(in px).
     */
    int max_height = 1080;
    /** {zh}
     * @brief 屏幕采集编码帧率, 单位 fps。
     */
    /** {en}
     * @brief The frame rate(in fps).
     */
    int frame_rate = 15;
    /** {zh}
     * @brief 屏幕采集编码码率, -1 为自动码率, SDK 会根据宽高信息选择合适的码率，单位 kbps
     */
    /** {en}
     * @brief The bitrate. If you set this value to -1, RTC will automatically recommend the bitrate(in kbps) based on the input resolution.
     */
    int bitrate = -1;
    /** {zh}
     * @brief 最小编码码率，使用 SDK 内部采集时可选设置，自定义采集时必须设置，单位：kbps。
     *        最小编码码率必须小于或等于最大编码，否则不对视频流进行编码发送。
     */
    /** {en}
     * @brief The minimum bitrate(in kbps).Optional for internal capture while mandatory for custom capture.  <br>
     *        The minimum bitrate must be set lower than the maximum bitrate. Otherwise, the streams will not be encoded and published. 
     */
    int min_bitrate = 0;
    /** {zh}
     * @brief 是否捕获鼠标光标。
     */
    /** {en}
     * @brief Whether to capture the mouse cursor.
     */
    bool capture_mouse_cursor = true;
    /** {zh}
     * @brief 抓取屏幕时排除窗口列表。这个参数仅在抓取屏幕时生效。
     */
    /** {en}
     * @brief The list of windows excluded from screen capture. This parameter only takes effect when you capture your screen.
     */
    view_t* excluded_window_list = nullptr;
    /** {zh}
     * @brief 抓取屏幕时排除的窗口数量。
     */
    /** {en}
     * @brief The number of windows excluded from screen capture.
     */
    int excluded_window_num = 0;
    /** {zh}
     * @brief 高亮边框的配置。
     */
    /** {en}
     * @brief Configure how a border is highlighted.
     */
    HighlightConfig highlight_config;
};

/** {zh}
 * @type keytype
 * @brief 自定义视频渲染器
 */
/** {en}
 * @type keytype
 * @brief Custom video renderer
 */
class IVideoSink {
public:
    /** {zh}
     * @type keytype
     * @brief 视频帧编码格式
     */
    /** {en}
     * @type keytype
     * @brief Video frame encoding format
     */
    enum PixelFormat {
        /** {zh}
         * @brief YUV I420 格式
         */
        /** {en}
         * @brief YUV I420 format
         */
        kI420 = VideoPixelFormat::kVideoPixelFormatI420,
        /** {zh}
         * @brief RGBA 格式, 字节序为 R8 G8 B8 A8
         */
        /** {en}
         * @brief RGBA format
         */
        kRGBA = VideoPixelFormat::kVideoPixelFormatRGBA,
        /** {zh}
         * @brief 原始视频帧格式
         */
        /** {en}
         * @brief Original format
         */
		kOriginal = VideoPixelFormat::kVideoPixelFormatUnknown,
    };
    /** {zh}
     * @type callback
     * @brief 视频帧回调
     * @param [out] video_frame 视频帧结构类，参看 IVideoFrame{@link #IVideoFrame}
     * @return 返回值暂未使用
     */
    /** {en}
     * @type callback
     * @brief Video frame callback
     * @param [out] video_frame Video frame structure. See IVideoFrame{@link #IVideoFrame}.
     * @return Temporarily unavailable
     */
    virtual bool onFrame(IVideoFrame* video_frame) = 0;

    /** {zh}
     * @type callback
     * @region 房间管理
     * @brief 获取外部渲染耗时。
     * @notes 获取外部渲染耗时进行上报。开发者需要自己计算平均渲染耗时。
     */
    /** {en}
     * @type callback
     * @region Room Management
     * @brief Gets the time taken in custom rendering.
     * @notes Gets the time taken in custom rendering and report. You need to calculate the average rendering time by yourself.
     */
    virtual int getRenderElapse() = 0;
    /** {zh}
     * @type callback
     * @brief 释放渲染器。
     * @notes 通知开发者渲染器即将被废弃。收到该返回通知后即可释放资源。
     */
    /** {en}
     * @type callback
     * @brief Releases the renderer.
     * @notes Used to notify the user that the renderer is about to be deprecated. Resources can be released upon receipt of this notification.
     */
    virtual void release() {
    }
    /** {zh}
     * @hidden constructor/destructor
     * @brief 析构函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Destructor
     */
    virtual ~IVideoSink() = default;

    /** {zh}
     * @hidden sink id
     * @brief sink id
     */
    /** {en}
     * @hidden sink id
     * @brief sink id
     */
    virtual void* uniqueId() const { return (void *)this; }
};

/** {zh}
 * @type keytype
 * @brief 本地视频帧回调位置。
 */
/** {en}
 * @type keytype
 * @brief The position of the local video frame.
 */
enum LocalVideoRenderPosition {
    /** {zh}
     * @brief 采集后。
     */
    /** {en}
     * @brief After capturing.
     */
    kLocalVideoRenderPositionAfterCapture,
    /** {zh}
     * @brief （默认值）前处理后。
     */
    /** {en}
     * @brief (Default) After preprocessing.
     */
    kLocalVideoRenderPositionAfterPreProcess
};

/** {zh}
 * @type keytype
 * @brief 是否将视频帧自动转正。
 */
/** {en}
 * @type keytype
 * @brief Whether the video frame needs to be automatically rotate.
 */
enum VideoApplyRotation {
    /** {zh}
     * @brief （默认值）不旋转。
     */
    /** {en}
     * @brief (Default) No rotation.
     */
    kVideoApplyRotationDefault = -1,
    /** {zh}
     * @brief 自动转正视频，即根据视频帧的旋转角信息将视频帧旋转到 0 度。
     */
    /** {en}
     * @brief Automatic rotation, which rotates video frames to 0 degree based on the rotation angle information.
     */
    kVideoApplyRotation0 = 0,
};

/** {zh}
 * @type keytype
 * @brief 是否将视频帧镜像。
 */
/** {en}
 * @type keytype
 * @brief Whether the video frame needs to be mirrored.
 */
enum VideoRenderMirrorType {
    /** {zh} 
     * @brief 开启镜像。
     */
    /** {en} 
     * @brief Enable mirroring effect.
     */
    kVideoSinkMirrorTypeON = 1,
    /** {zh} 
     * @brief （默认值）不开启镜像。
     */
    /** {en} 
     * @brief (Default) No mirroring effect.
     */
    kVideoSinkMirrorTypeOFF = 2,
};

/** {zh}
 * @type keytype
 * @brief 本地视频帧回调配置。
 */
/** {en}
 * @type keytype
 * @brief Local video frame callback config.
 */
struct LocalVideoSinkConfig {
    /** {zh}
     * @brief 本地视频帧回调位置，参看 LocalVideoRenderPosition{@link #LocalVideoRenderPosition}，默认回调前处理后的视频帧。
     */
    /** {en}
     * @brief The position of the local video frame. See LocalVideoRenderPosition{@link #LocalVideoRenderPosition}.
     */
    LocalVideoRenderPosition position = kLocalVideoRenderPositionAfterPreProcess;
    /** {zh}
     * @brief 本地视频帧回调格式，参看 VideoPixelFormat{@link #VideoPixelFormat}，默认值为 0。
     */
    /** {en}
     * @brief The pixel format of the local video frame. See VideoPixelFormat{@link #VideoPixelFormat}. The default value is 0.
     */
    VideoPixelFormat pixel_format = kVideoPixelFormatUnknown;
};

/** {zh}
 * @type keytype
 * @brief 远端视频帧回调位置。
 */
/** {en}
 * @type keytype
 * @brief The position of the remote video frame.
 */
enum RemoteVideoRenderPosition {
    /** {zh}
     * @brief 解码后。
     */
    /** {en}
     * @brief After decoding.
     */
    kRemoteVideoRenderPositionAfterDecoder,
    /** {zh}
     * @brief （默认值）后处理后。
     */
    /** {en}
     * @brief (Default) After processing.
     */
    kRemoteVideoRenderPositionAfterPostProcess
};

/** {zh}
 * @type keytype
 * @brief 远端视频帧回调配置。
 */
/** {en}
 * @type keytype
 * @brief Remote video frame callback configurations.
 */
struct RemoteVideoSinkConfig {
    /** {zh}
     * @brief 远端视频帧回调位置，参看 RemoteVideoRenderPosition{@link #RemoteVideoRenderPosition}，默认回调后处理后的视频帧。
     */
    /** {en}
     * @brief The position of the remote video frame. See RemoteRenderPosition{@link #RemoteRenderPosition}. The default position is after processing.
     */
    RemoteVideoRenderPosition position = kRemoteVideoRenderPositionAfterPostProcess;
    /** {zh}
     * @brief 远端视频帧回调格式，参看 VideoPixelFormat{@link #VideoPixelFormat}，默认值为 0。
     */
    /** {en}
     * @brief The pixel format of the remote video frame. See VideoPixelFormat{@link #VideoPixelFormat}. The default value is 0.
     */
    VideoPixelFormat pixel_format = kVideoPixelFormatUnknown;
    /** {zh}
     * @brief 是否将视频帧自动转正，参看 VideoApplyRotation{@link #VideoApplyRotation}，默认为不旋转。
     */
    /** {en}
     * @brief Whether the video frame needs to be automatically rotate. See VideoApplyRotation{@link #VideoApplyRotation}. The default value is no rotate.
     */
    VideoApplyRotation apply_rotation = kVideoApplyRotationDefault;
    /** {zh}
     * @brief 是否将视频帧镜像。参看 VideoRenderMirrorType{@link #VideoRenderMirrorType}，默认为不镜像。
     *        本设置与 setRemoteVideoMirrorType{@link #IRTCVideo#setRemoteVideoMirrorType} （适用于内部渲染）相互独立。
     */
    /** {en}
     * @brief Whether the video frame needs to be mirrored. See VideoRenderMirrorType{@link #VideoRenderMirrorType}. The default value is no mirroring effect.
     */
    VideoRenderMirrorType mirror_type = kVideoSinkMirrorTypeOFF;
};

/** {zh}
 * @hidden
 * @type keytype
 * @deprecated since 3.29 and will be deleted in 3.51, use MirrorType{@link #MirrorType} instead.
 * @brief 是否开启镜像模式
 */
/** {en}
 * @hidden
 * @type keytype
 * @deprecated since 3.45 and will be deleted in 3.51, use MirrorType{@link #MirrorType} instead.
 * @brief Whether to turn on mirror mode
 */
enum MirrorMode {
    /** {zh}
     * @brief 不开启
     */
    /** {en}
     * @brief Not open
     */
    kMirrorModeOff = 0,
    /** {zh}
     * @brief 开启
     */
    /** {en}
     * @brief Open
     */
    kMirrorModeOn = 1,
};

/** {zh}
 * @type keytype
 * @brief 镜像类型
 */
/** {en}
 * @type keytype
 * @brief  Mirror type
 */
enum MirrorType : int {
    /** {zh}
     * @brief 本地预览和编码传输时均无镜像效果
     */
    /** {en}
     * @brief The preview and the published video stream are not mirrored.
     */
    kMirrorTypeNone = 0,
    /** {zh}
     * @brief 本地预览时有镜像效果，编码传输时无镜像效果
     */
    /** {en}
     * @brief The preview is mirrored. The published video stream is not mirrored.
     */
    kMirrorTypeRender = 1,
    /** {zh}
     * @brief 本地预览和编码传输时均有镜像效果
     */
    /** {en}
     * @brief The preview and the published video stream are mirrored.
     */
    kMirrorTypeRenderAndEncoder = 3,
};


/** {zh}
 * @type keytype
 * @brief 远端流的镜像类型。
 */
/** {en}
 * @type keytype
 * @brief Mirroring type for remote stream.
 */
enum RemoteMirrorType {
    /** {zh}
     * @brief （默认值）远端视频渲染无镜像效果。
     */
    /** {en}
     * @brief (Default) No mirroring effect.
     */
    kRemoteMirrorTypeNone = 0,
    /** {zh}
     * @brief 远端视频渲染有镜像效果。
     */
    /** {en}
     * @brief Enable mirroring effect.
     */
    kRemoteMirrorTypeRender = 1,
};

/** {zh}
 * @type keytype
 * @brief 弱光适应类型
 */
/** {en}
 * @type keytype
 * @brief  Low light adjusted type
 */
enum VideoEnhancementMode {
    /** {zh}
     * @brief 关闭弱光适应
     */
    /** {en}
     * @brief Turn off low light adaptation
     */
    kVideoEnhancementModeDisabled = 0,
    /** {zh}
     * @brief 开启弱光适应
     */
    /** {en}
     * @brief Turn on low light adaptation
     */
    kVideoEnhancementModeAuto = 1,
};

/** {zh}
 * @type keytype
 * @brief 视频输入源类型
 */
/** {en}
 * @type keytype
 * @brief Video source type
 */
enum VideoSourceType {
    /** {zh}
     * @brief 自定义采集视频源
     */
    /** {en}
     * @brief Custom video source
     */
    kVideoSourceTypeExternal = 0,
    /** {zh}
     * @brief 内部采集视频源
     */
    /** {en}
     * @brief Internal video capture
     */
    kVideoSourceTypeInternal = 1,
    /** {zh}
     * @brief 自定义编码视频源。  <br>
     *        你仅需推送分辨率最大的一路编码后视频流，SDK 将自动转码生成多路小流
     */
    /** {en}
     * @brief Custom encoded video source.   <br>
     *        Push the encoded video stream with the largest resolution, and the SDK will automatically transcode to generate multiple lower-quality streams for Simulcast.
     */
    kVideoSourceTypeEncodedWithAutoSimulcast = 2,
    /** {zh}
     * @brief 自定义编码视频源。  <br>
     *        SDK 不会自动生成多路流，你需要自行生成并推送多路流
     */
    /** {en}
     * @brief Custom encoded video source.   <br>
     *         The SDK does not automatically generate multiple streams for Simulcast, you need to generate and push streams of different qualities.
     */
    kVideoSourceTypeEncodedWithoutAutoSimulcast = 3,
};

/** {zh}
 * @type keytype
 * @brief 数码变焦参数类型
 */
/** {en}
 * @type keytype
 * @brief Digital Zoom type
 */
enum ZoomConfigType {
    /** {zh}
     * @brief 设置缩放系数
     */
    /** {en}
     * @brief To set the offset for zooming in and zooming out.
     */
    kZoomConfigTypeFocusOffset = 0, 
    /** {zh}
     * @brief 设置移动步长
     */
    /** {en}
     * @brief To set the offset for panning and tiling.
     */
    kZoomConfigTypeMoveOffset,
};

/** {zh}
 * @type keytype
 * @brief 数码变焦操作类型
 */
/** {en}
 * @type keytype
 * @brief Action of the digital zoom control
 */
enum ZoomDirectionType {
    /** {zh}
     * @brief 相机向左移动
     */
    /** {en}
     * @brief Move to the left.
     */
    kZoomDirectionTypeMoveLeft = 0,
    /** {zh}
     * @brief 相机向右移动
     */
    /** {en}
     * @brief Move to the right.
     */
    kZoomDirectionTypeMoveRight,
    /** {zh}
     * @brief 相机向上移动
     */
    /** {en}
     * @brief Move upwards.
     */
    kZoomDirectionTypeMoveUp,
    /** {zh}
     * @brief 相机向下移动
     */
    /** {en}
     * @brief Move downwards.
     */
    kZoomDirectionTypeMoveDown,
    /** {zh}
     * @brief 相机缩小焦距
     */
    /** {en}
     * @brief Zoom out.
     */
    kZoomDirectionTypeZoomOut,
    /** {zh}
     * @brief 相机放大焦距
     */
    /** {en}
     * @brief Zoom in.
     */
    kZoomDirectionTypeZoomIn,
    /** {zh}
     * @brief 恢复到原始画面
     */
    /** {en}
     * @brief Reset digital zoom.
     */
    kZoomDirectionTypeReset,
};

/** {zh}
 * @type keytype
 * @brief 视频帧信息
 */
/** {en}
 * @type keytype
 * @brief  Video frame information
 */
struct VideoFrameInfo {
    /** {zh}
     * @brief 宽（像素）
     */
    /** {en}
     * @brief Width (pixels)
     */
    int width = 0;
    /** {zh}
     * @brief 高（像素）
     */
    /** {en}
     * @brief High (pixels)
     */
    int height = 0;
    /** {zh}
     * @brief 视频帧顺时针旋转角度。参看 VideoRotation{@link #VideoRotation}。
     */
    /** {en}
     * @brief Video frame clockwise rotation angle. See VideoRotation{@link #VideoRotation}.
     */
    VideoRotation rotation = VideoRotation::kVideoRotation0;
};

/** {zh}
 * @type keytype
 * @brief 视频前处理配置参数。<br>
 */
/** {en}
 * @type keytype
 * @brief  Video preprocessing configuration parameters. <br>
 */
struct VideoPreprocessorConfig {
    /** {zh}
     * @brief 视频帧像素格式，参看 VideoPixelFormat{@link #VideoPixelFormat}
     *        当前仅支持 `kVideoPixelFormatI420` 和 `kVideoPixelFormatUnknown` 格式。
     */
    /** {en}
     * @brief Video frame pixel format. See VideoPixelFormat{@link #VideoPixelFormat}
     *         Only `kVideoPixelFormatI420` and `kVideoPixelFormatUnknown` are supported.
     */
    VideoPixelFormat required_pixel_format = kVideoPixelFormatUnknown;
};

/** {zh}
 * @type keytype
 * @brief 自定义编码流信息
 */
/** {en}
 * @type keytype
 * @brief  Custom coded stream information
 */
struct VideoRateInfo {
    /** {zh}
     * @brief 帧率，单位 fps
     */
    /** {en}
     * @brief Frame rate, units fps
     */
    int fps = 0;
    /** {zh}
     * @brief 码率，单位 kbps
     */
    /** {en}
     * @brief Bit rate, unit kbps
     */
    int bitrate_kbps = 0;
    /** {zh} 
     * @brief 视频最小编码码率, 单位 kbps。编码码率不会低于 `min_bitrate_kbps`。<br>
     *        默认值为 `0`。<br>
     *        范围：[0, bitrate_kbps)，当 `bitrate_kbps` < `min_bitrate_kbps` 时，为适配码率模式。<br>
     *        以下情况，设置本参数无效：<br>
     *        + 当 `bitrate_kbps` 为 `0` 时，不对视频流进行编码发送。<br>
     *        + 当 `bitrate_kbps` < `0` 时，适配码率模式。
     */
    /** {en} 
     * @brief Minimum video encoding bitrate in kbps. The encoding bitrate will not be lower than the `min_bitrate_kbps`.<br>
     *        It defaults to `0`. <br>
     *        It ranges within [0, bitrate_kbps). When `bitrate_kbps` < `min_bitrate_kbps`, the bitrate is self-adpapted.<br>
     *        In the following circumstance, the assignment to this variable has no effect:<br>
     *        + When `bitrate_kbps` = `0`, the video encoding is disabled.<br>
     *        + When `bitrate_kbps` < `0`, the bitrate is self-adapted.
     */
    int min_bitrate_kbps = 0;
};

/** {zh}
 * @type keytype
 * @brief 视频解码方式
 */
/** {en}
 * @type keytype
 * @brief  Video decoding method
 */
enum VideoDecoderConfig {
    /** {zh}
     * @brief 开启 SDK 内部解码，只回调解码后的数据。回调为onFrame{@link #IVideoSink#onFrame}。
     */
    /** {en}
     * @brief Enable SDK internal decoding, only callback the decoded data
     */
    kVideoDecoderConfigRaw,
    /** {zh}
     * @brief 开启自定义解码，只回调解码前数据。回调为onRemoteEncodedVideoFrame{@link #IRemoteEncodedVideoFrameObserver#onRemoteEncodedVideoFrame}。
     */
    /** {en}
     * @brief Turn on custom decoding, only callback the data before decoding
     */
    kVideoDecoderConfigEncode,
    /** {zh}
     * @brief 开启 SDK 内部解码，同时回调解码前和解码后的数据。回调为onFrame{@link #IVideoSink#onFrame} 和 onRemoteEncodedVideoFrame{@link #IRemoteEncodedVideoFrameObserver#onRemoteEncodedVideoFrame}。
     */
    /** {en}
     * @brief Enable SDK internal decoding, and call back the data before and after decoding at the same time
     */
    kVideoDecoderConfigBoth,
};

/** {zh}
 * @type keytype
 * @brief 视频采集配置参数。<br>
 */
/** {en}
 * @type keytype
 * @brief  Video capture configuration parameters. <br>
 */
struct VideoCaptureConfig {
   /** {zh}
    * @type keytype
    * @brief 视频采集模式
    */
   /** {en}
    * @type keytype
    * @brief Video capture preference
    */
    enum CapturePreference {
       /** {zh}
        * @brief （默认）自动设置采集参数。
        *        SDK在开启采集时根据服务端下发的采集配置结合编码参数设置最佳采集参数。
        */
       /** {en}
        * @brief (Default) Video capture preference: auto <br>
        *        SDK determines the best video capture parameters referring to the camera output parameters and the encoder configuration.
        */
        kAuto = 0,
       /** {zh}
        * @brief 手动设置采集参数，包括采集分辨率、帧率。
        */
       /** {en}
        * @brief Video capture preference: manual <br>
        *        Set the resolution and the frame rate manually.
        */
        kManual = 1,
       /** {zh}
        * @brief 采集参数与编码参数一致，即在 setVideoEncoderConfig{@link #IRTCVideo#setVideoEncoderConfig} 中设置的参数。
        */
       /** {en}
        * @brief Video capture preference: encoder configuration <br>
        *        The capture parameters are the same with the parameters set in setVideoEncoderConfig{@link #IRTCVideo#setVideoEncoderConfig}.
        */
        kAutoPerformance = 2,
    };
    /** {zh}
     * @brief 视频采集模式，参看 [CapturePreference](#capturepreference-2)
     */
    /** {en}
     * @brief Video capture preference. See [CapturePreference](#capturepreference-1).
     */
    CapturePreference capture_preference = CapturePreference::kAuto;

    /** {zh}
     * @brief 视频采集分辨率的宽度，单位：px。
     */
    /** {en}
     * @brief The width of video capture resolution in px.
     */
    int width = 0;
    /** {zh}
     * @brief 视频采集分辨率的高度，单位：px。
     */
    /** {en}
     * @brief The height of video capture resolution in px.
     */
    int height = 0;
    /** {zh}
     * @brief 视频采集帧率，单位：fps。
    */
   /** {en}
     * @brief Video capture frame rate in fps.
    */
    int frame_rate = 0;
};

/** {zh}
 * @type keytype
 * @brief 本地录制的媒体类型
 */
/** {en}
 * @type keytype
 * @brief Locally recorded media type
 */
enum RecordingType {
    /** {zh}
     * @brief 只录制音频
     */
    /** {en}
     * @brief Audio only
     */
    kRecordingTypeAudioOnly = 0,
    /** {zh}
     * @brief 只录制视频
     */
    /** {en}
     * @brief Video only
     */
    kRecordingTypeVideoOnly = 1,
    /** {zh}
     * @brief 同时录制音频和视频
     */
    /** {en}
     * @brief Record audio and video simultaneously
     */
    kRecordingTypeVideoAndAudio = 2,
};

/** {zh}
 * @type keytype
 * @brief 当前视频设备类型
 */
/** {en}
 * @type keytype
 * @brief  Current audio device type
 */
enum RTCVideoDeviceType {
    /** {zh}
     * @brief 未知设备类型
     */
    /** {en}
     * @brief Unknown device
     */
    kRTCVideoDeviceTypeUnknown = -1,
    /** {zh}
     * @brief 视频渲染设备类型
     */
    /** {en}
     * @brief Video rendering device
     */
    kRTCVideoDeviceTypeRenderDevice = 0,
    /** {zh}
     * @brief 视频采集设备类型
     */
    /** {en}
     * @brief Video capture device
     */
    kRTCVideoDeviceTypeCaptureDevice = 1,
    /** {zh}
     * @brief 屏幕流视频设备
     */
    /** {en}
     * @brief Screen recorder
     */
    kRTCVideoDeviceTypeScreenCaptureDevice = 2,
};

/** {zh}
 * @type errorcode
 * @brief 公共流状态码
 */
/** {en}
 * @hidden currently not available
 * @type errorcode
 * @brief State and errors for publishing or subscribing public streams
 */
enum PublicStreamErrorCode {
    /** {zh}
     * @brief 发布或订阅成功。
     */
    /** {en}
     * @brief Published or subscribed successfully.
     */
    kPublicStreamErrorCodeOK = 0,
    /** {zh}
     * @brief 公共流的参数异常，请修改参数后重试。
     */
    /** {en}
     * @brief Invalid parameter(s). Please revise the paramter(s) and retry.
     */
    kPublicStreamErrorCodePushInvalidParam = 1191,
    /** {zh}
     * @brief 服务端状态异常，将自动重试。
     */
    /** {en}
     * @brief Error for the task at the server side. The server will retry upon the failure.
     */
    kPublicStreamErrorCodePushInvalidStatus = 1192,
    /** {zh}
     * @brief 内部错误，不可恢复，请重试。
     */
    /** {en}
     * @brief Unrecoverable error of publishing the public stream. Please start the task again.
     */
    kPublicStreamErrorCodePushInternalError = 1193,
    /** {zh}
     * @brief 发布失败，将自动重试，请关注重试结果。
     */
    /** {en}
     * @brief Failed to publish. The SDK will retry upon the failure. We recommend to keep listening to the publishing result.
     */
    kPublicStreamErrorCodePushFailed = 1195,
    /** {zh}
     * @brief 发布失败，10 s 后会重试，重试 3 次后自动停止。
     */
    /** {en}
     * @brief Failed to publish the public stream for time-out error. The SDK will retry 10 s after the timeout. The maximum number of retry attempts is 3.
     */
    kPublicStreamErrorCodePushTimeout = 1196,
    /** {zh}
     * @brief 订阅失败，发布端未开始发布流。
     */
    /** {en}
     * @brief Failed to play a public stream because the publisher has not started publishing.
     */
    kPublicStreamErrorCodePullNoPushStream = 1300,
};

/** {zh}
 * @type keytype
 * @brief 视频旋转模式
 */
/** {en}
 * @type keytype
 * @brief Video orientation
 */
enum VideoRotationMode {
    /** {zh}
     * @brief 跟随App界面方向
     */
    /** {en}
     * @brief The orientation of the App
     */
    kVideoRotationModeFollowApp = 0,
    /** {zh}
     * @brief 跟随设备重力方向
     */
    /** {en}
     * @brief Gravity
     */
    kVideoRotationModeFollowGSensor = 1,
};

/** {zh}
 * @type keytype
 * @brief 媒体流类型
 */
/** {en}
 * @type keytype
 * @brief Media stream type
 */
enum MediaStreamType {
    /** {zh}
     * @brief 只控制音频
     */
    /** {en}
     * @brief Controls audio only
     */
    kMediaStreamTypeAudio = 1 << 0,
    /** {zh}
     * @brief 只控制视频
     */
    /** {en}
     * @brief Controls video only
     */
    kMediaStreamTypeVideo = 1 << 1,
    /** {zh}
     * @brief 同时控制音频和视频
     */
    /** {en}
     * @brief Controls both audio and video
     */
    kMediaStreamTypeBoth = kMediaStreamTypeAudio | kMediaStreamTypeVideo
};
/** {zh}
 * @type keytype
 * @brief 占发布端原始帧率的比例
 */
/** {en}
 * @type keytype
 * @brief Ratio to the original video frame rate of the publisher
 */
enum FrameRateRatio {
  /** {zh}
   * @brief 100%
   */
  /** {en}
   * @brief 100%
   */
  kFrameRateRatioOriginal = 0,
  /** {zh}
   * @brief 50%
   */
  /** {en}
   * @brief 50%
   */
  kFrameRateRatioHalf = 1,
  /** {zh}
   * @brief 25%
   */
  /** {en}
   * @brief 25%
   */
  kFrameRateRatioQuarter = 2,
};
/** {zh}
 * @type keytype
 * @brief 远端视频帧信息
 */
/** {en}
 * @type keytype
 * @brief Information on remote video frame
 */
struct RemoteVideoConfig {
    /** {zh}
     * @brief 期望订阅的最高帧率，单位：fps，默认值为 0 即满帧订阅，设为大于 0 的值时开始生效。  <br>
     *        当发布端帧率低于设定帧率，或订阅端开启性能回退后下行弱网，则帧率会相应下降。  <br>
     *        仅码流支持 SVC 分级编码特性时方可生效。
     */
    /** {en}
     * @brief Expected maximum frame rate of the subscribed stream in px. The default value is 0, which represents full-frame-rate, values greater than 0 are valid.  <br>
     *        If the frame rate of the stream published is lower than the value you set, or if your subscribed stream falls back under limited network conditions, the frame rate you set will drop accordingly.  <br>
     *        Only valid if the stream is coded with SVC technique.
     */
    int framerate = 0;
    /** {zh}
     * @brief 视频宽度，单位：px
     */
    /** {en}
     * @brief Width of the video frame in px
     */
    int resolution_width = 0;
    /** {zh}
     * @brief 视频高度，单位：px
     */
    /** {en}
     * @brief Height of the video frame in px
     */
    int resolution_height = 0;
};
/** {zh}
 * @type keytype
 * @brief 房间参数配置。房间是 RTC 通话的抽象概念。在同一个房间中的用户可以进行音视频通话。
 */
/** {en}
 * @type keytype
 * @brief Room configuration. Room is a abstract concept for an RTC call. Users can interactive with each other in the same room.
 */
struct RTCRoomConfig {
    /** {zh}
     * @brief 房间模式，参看 RoomProfileType{@link #RoomProfileType}，默认为 `kRoomProfileTypeCommunication`，进房后不可更改。
     */
    /** {en}
     * @brief Room profile. See RoomProfileType{@link #RoomProfileType}. The default is `kRoomProfileTypeCommunication`. The setting cannot be changed after joining the room.
     */
    RoomProfileType room_profile_type = kRoomProfileTypeCommunication;
    /** {zh}
     * @brief 是否自动发布音视频流，默认为自动发布。 <br>
     *        创建和加入多房间时，只能将其中一个房间设置为自动发布。若每个房间均不做设置，则默认在第一个加入的房间内自动发布流。<br>
     *        若调用 setUserVisibility{@link #IRTCRoom#setUserVisibility} 将自身可见性设为 false，无论是默认的自动发布流还是手动设置的自动发布流都不会进行发布，你需要将自身可见性设为 true 后方可发布。
     */
   /** {en}
    * @brief Whether to publish media streams automatically. The default is automatic publishing.  <br>
     *       Only one of the rooms the user joined can be set to auto-publish. If no settings are made in each room, the stream is automatically published in the first room joined by default.<br>
    *        If you call setUserVisibility{@link #IRTCRoom#setUserVisibility} to set your own visibility to false, you will not publish media streams regardless of the value of `is_auto_publish`.
    */
    bool is_auto_publish = true;
    /** {zh}
     * @brief 是否自动订阅音频流，默认为自动订阅。<br>
     *        包含主流和屏幕流。 
     */
    /** {en}
     * @brief Whether to automatically subscribe to the audio stream. The default is automatic subscription.<br>
     *        This setting affects both the main stream and the screen-sharing stream.
     */
    bool is_auto_subscribe_audio = true;
    /** {zh}
     * @brief 是否自动订阅视频流，默认为自动订阅。<br>
     *        包含主流和屏幕流。 
     */
    /** {en}
     * @brief Whether to automatically subscribe to the video stream. The default is automatic subscription.<br>
     *        This setting affects both the main stream and the screen-sharing stream.
     */
    bool is_auto_subscribe_video = true;
    /** {zh}
     * @brief 远端视频流参数，参看 RemoteVideoConfig{@link #RemoteVideoConfig}
     */
    /** {en}
     * @brief Expected configuration of remote video stream, see RemoteVideoConfig{@link #RemoteVideoConfig}.
     */
    RemoteVideoConfig remote_video_config;
};

/** {zh}
 * @type keytype
 * @brief 屏幕采集的媒体类型
 */
/** {en}
 * @type keytype
 * @brief  The media type for screen capture
 */
enum ScreenMediaType {
    /** {zh}
     * @brief 仅采集视频
     */
    /** {en}
     * @brief Capture video only
     */
    kScreenMediaTypeVideoOnly = 0,
    /** {zh}
     * @brief 仅采集音频
     */
    /** {en}
     * @brief Capture audio only
     */
    kScreenMediaTypeAudioOnly = 1,
    /** {zh}
     * @brief 同时采集音频和视频
     */
    /** {en}
     * @brief Capture Audio and video simultaneously.
     */
    kScreenMediaTypeVideoAndAudio = 2,
};

/** {zh}
 * @type keytype
 * @brief 基础美颜模式。
 */
/** {en}
 * @type keytype
 * @brief Basic beauty effect.
 */
enum EffectBeautyMode {
    /** {zh}
     * @brief 美白。
     */
    /** {en}
     * @brief Brightening.
     */ 
    kEffectBeautyModeWhite = 0,
    /** {zh}
     * @brief 磨皮。
     */
    /** {en}
     * @brief Smoothing.
     */
    kEffectBeautyModeSmooth = 1,
    /** {zh}
     * @brief 锐化。
     */
    /** {en}
     * @brief Sharpening.
     */ 
    kEffectBeautyModeSharpen = 2,
    /** {zh}
     * @valid since 3.55
     * @brief 清晰，需集成 v4.4.2+ 版本的特效 SDK。
     */
    /** {en}
     * @valid since 3.55
     * @brief Clarity. Integrating Effects SDK v4.4.2+ is required for this sub-item.
     */ 
    kEffectBeautyModeClear = 3,
};

/** {zh} 
 * @type keytype
 * @brief 视频设备朝向类型
 */
/** {en} 
 * @type keytype
 * @brief  video device facing type
 */
enum VideoDeviceFacing {
    /** {zh} 
     * @brief 前置摄像头
     */
    /** {en} 
     * @brief Front-facing video camera
     */
    kVideoDeviceFacingFront = 0,
    /** {zh} 
     * @brief 后置摄像头
     */
    /** {en} 
     * @brief Back-facing video camera
     */
    kVideoDeviceFacingBack = 1,
    /** {zh} 
     * @brief 未知类型
     */
    /** {en} 
     * @brief video camera facing unknown
     */
    kVideoDeviceFacingUnknown = 2,
};

/** {zh}
 * @type keytype
 * @brief 视频设备信息
 */
/** {en}
 * @type keytype
 * @brief Video device information
 */
struct VideoDeviceInfo {
    /** {zh}
     * @brief 设备 ID
     */
    /** {en}
     * @brief Device ID
     */
    char device_id[MAX_DEVICE_ID_LENGTH];
    /** {zh}
     * @brief 设备名称
     */
    /** {en}
     * @brief Device alias
     */
    char device_name[MAX_DEVICE_ID_LENGTH];
    /** {zh}
     * @brief 设备的厂商 ID
     */
    /** {en}
     * @brief ID of the device vendor
     */
    int64_t device_vid;
    /** {zh}
     * @brief 设备的产品编码
     */
    /** {en}
     * @brief Product number of the device
     */
    int64_t device_pid;
    /** {zh}
     * @brief 设备的传输方式
     */
    /** {en}
     * @brief Connection type of the device
     */
    DeviceTransportType transport_type;
    /** {zh} 
     * @brief 视频设备朝向类型
     */
    /** {en} 
     * @brief  video device facing type
     */
    VideoDeviceFacing device_facing;
    /**
     * @hidden constructor/destructon
     */
    VideoDeviceInfo() {
        memset(device_id, 0, MAX_DEVICE_ID_LENGTH);
        memset(device_name, 0, MAX_DEVICE_ID_LENGTH);
        this->device_vid = 0;
        this->device_pid = 0;
        this->transport_type = DeviceTransportType::kDeviceTransportTypeUnknown;
        this->device_facing = VideoDeviceFacing::kVideoDeviceFacingFront;
    };

    /**
     * @hidden constructor/destructon
     */
    VideoDeviceInfo& operator=(const VideoDeviceInfo& src) {
        if (this != &src) {
            strncpy(device_id, src.device_id, MAX_DEVICE_ID_LENGTH - 1);
            strncpy(device_name, src.device_name, MAX_DEVICE_ID_LENGTH - 1);
            device_id[MAX_DEVICE_ID_LENGTH - 1] = '\0';
            device_name[MAX_DEVICE_ID_LENGTH - 1] = '\0';
            device_vid = src.device_vid;
            device_pid = src.device_pid;
            transport_type = src.transport_type;
            device_facing = src.device_facing;
        }

        return *this;
    }
};

/** {zh}
 * @type keytype
 * @brief 视频帧朝向
 */
/** {en}
 * @type keytype
 * @brief Orientation of the video frame.
 */
enum VideoOrientation {
    /** {zh}
     * @brief （默认）使用相机输出的原始视频帧的角度，不对视频帧进行额外旋转。
     */
    /** {en}
     * @brief (Default) The original orientation of the captured video frame.
     */
    kVideoOrientationAdaptive = 0,
    /** {zh}
     * @brief 固定为竖屏，将相机采集到的视频帧转换为竖屏，在整个 RTC 链路中传递竖屏帧。
     */
    /** {en}
     * @brief Portrait mode. Adjust the captured video frame to vertical layout in RTC SDK.
     */
    kVideoOrientationPortrait = 1,
    /** {zh}
     * @brief 固定为横屏，将相机采集到的视频帧转换为横屏，在整个 RTC 链路中传递横屏帧。
     */
    /** {en}
     * @brief Landscape mode. Adjust the captured video frame to horizontal layout in RTC SDK.
     */
    kVideoOrientationLandscape = 2
};

/** {zh}
 * @hidden(Windows, Linux, macOS)
 * @type keytype
 * @brief 超分状态改变原因。
 */
/** {en}
 * @hidden not available
 * @type keytype
 * @brief The reason for the change in super resolution mode.
 */
enum VideoSuperResolutionModeChangedReason {
    /** {zh}
     * @brief 调用 setRemoteVideoSuperResolution{@link #IRTCVideo#setRemoteVideoSuperResolution} 成功关闭超分。
     */
    /** {en}
     * @brief Successfully turned off the super resolution mode by calling setRemoteVideoSuperResolution{@link #IRTCVideo#setRemoteVideoSuperResolution}.
     */
    kVideoSuperResolutionModeChangedReasonAPIOff = 0,
    /** {zh}
     * @brief 调用 setRemoteVideoSuperResolution{@link #IRTCVideo#setRemoteVideoSuperResolution} 成功开启超分。
     */
    /** {en}
     * @brief Successfully turned on the super resolution mode by calling setRemoteVideoSuperResolution{@link #IRTCVideo#setRemoteVideoSuperResolution}.
     */
    kVideoSuperResolutionModeChangedReasonAPIOn = 1,
    /** {zh}
     * @brief 开启超分失败，远端视频流的原始视频分辨率超过 640 × 360 px。
     */
    /** {en}
     * @brief Failed to turn on super-resolution mode. The original resolution of the remote video stream should not exceed 640 × 360 pixels.
     */
    kVideoSuperResolutionModeChangedReasonResolutionExceed = 2,
    /** {zh}
     * @brief 开启超分失败，已对一路远端流开启超分。
     */
    /** {en}
     * @brief Failed to turn on super-resolution mode. You can only turn on super-resolution mode for one stream.
     */
    kVideoSuperResolutionModeChangedReasonOverUse = 3,
    /** {zh}
     * @brief 设备不支持使用超分辨率。
     */
    /** {en}
     * @brief Incompatible device for super resolution.
     */
    kVideoSuperResolutionModeChangedReasonDeviceNotSupport = 4,
    /** {zh}
     * @brief 当前设备性能存在风险，已动态关闭超分。
     */
    /** {en}
     * @brief The super-resolution mode is turned off because of lacking device capabilities.
     */
    kVideoSuperResolutionModeChangedReasonDynamicClose = 5,
    /** {zh}
     * @brief 超分因其他原因关闭。
     */
    /** {en}
     * @brief The super-resolution mode is turned off for other reasons.
     */
    kVideoSuperResolutionModeChangedReasonOtherSettingDisabled = 6,
    /** {zh}
     * @brief 超分因其他原因开启。
     */
    /** {en}
     * @brief The super-resolution mode is turned on for other reasons.
     */
    kVideoSuperResolutionModeChangedReasonOtherSettingEnabled = 7,
    /** {zh}
     * @brief SDK 没有编译超分组件。
     */
    /** {en}
     * @brief The super-resolution mode is not compiled in the SDK.
     */
    kVideoSuperResolutionModeChangedReasonNoComponent = 8,
    /** {zh}
     * @brief 远端流不存在。房间 ID 或用户 ID 无效，或对方没有发布流。
     */
    /** {en}
     * @brief The remote stream does not exist. Reasons include invalid room ID, user ID, or the stream is not published.
     */
    kVideoSuperResolutionModeChangedReasonStreamNotExist = 9,
};

/** {zh}
 * @hidden(Windows, Linux, macOS)
 * @type keytype
 * @brief 视频降噪模式状态改变原因。
 */
/** {en}
 * @hidden not available
 * @type keytype
 * @brief The reasons for the change in the video noise reduction mode.
 */
enum VideoDenoiseModeChangedReason {
    /** {zh}
     * @brief 未知原因导致视频降噪状态改变。
     */
    /** {en}
     * @brief Video noise reduction mode changed due to unknown reasons.
     */
    kVideoDenoiseModeChangedReasonNull = -1,
    /** {zh}
     * @brief 通过调用 setVideoDenoiser{@link #IRTCVideo#setVideoDenoiser} 成功关闭视频降噪。
     */
    /** {en}
     * @brief Successfully turned off the video noise reduction by calling setVideoDenoiser{@link #IRTCVideo#setVideoDenoiser}.
     */
    kVideoDenoiseModeChangedReasonApiOff = 0,
    /** {zh}
     * @brief 通过调用 setVideoDenoiser{@link #IRTCVideo#setVideoDenoiser} 成功开启视频降噪。
     */
    /** {en}
     * @brief Successfully turned on the video noise reduction by calling setVideoDenoiser{@link #IRTCVideo#setVideoDenoiser}.
     */
    kVideoDenoiseModeChangedReasonApiOn = 1,
    /** {zh}
     * @brief 后台未配置视频降噪，视频降噪开启失败，请联系技术人员解决。
     */
    /** {en}
     * @brief Video noise reduction disabled by configuration.
     */
    kVideoDenoiseModeChangedReasonConfigDisabled = 2,
    /** {zh}
     * @brief 后台配置开启了视频降噪。
     */
    /** {en}
     * @brief Video noise reduction enabled by configuration.
     */
    kVideoDenoiseModeChangedReasonConfigEnabled = 3,
    /** {zh}
     * @brief 由于内部发生了异常，视频降噪关闭。 
     */
    /** {en}
     * @brief Video noise reduction turned off due to internal exceptions. 
     */
    kVideoDenoiseModeChangedReasonInternalException = 4,
    /** {zh}
     * @brief 当前设备性能过载，已动态关闭视频降噪。
     */
    /** {en}
     * @brief Video noise reduction turned off due to hardware performance stress. 
     */
    kVideoDenoiseModeChangedReasonDynamicClose = 5,
    /** {zh}
     * @brief 当前设备性能裕量充足，已动态开启视频降噪。
     */
    /** {en}
     * @brief Device hardware capacity is sufficient, video noise reduction turned on.
     */
    kVideoDenoiseModeChangedReasonDynamicOpen = 6,
    /** {zh}
     * @brief
     * 分辨率导致视频降噪状态发生改变。分辨率过高会导致性能消耗过大，从而导致视频降噪关闭。若希望继续使用视频降噪，可选择降低分辨率。
     */
    /** {en}
     * @brief Video noise reduction mode changed due to video resolution. High resolution leads to high hardware utilization. Reduce the resolution to recover video noise reduction.
     */
    kVideoDenoiseModeChangedReasonResolution = 7,
};

/** {zh}
 * @type keytype
 * @brief 屏幕采集对象的类型
 */
/** {en}
 * @type keytype
 * @brief Type of the screen capture object
 */
enum ScreenCaptureSourceType {
    /** {zh}
     * @brief 类型未知
     */
    /** {en}
     * @brief Type unknown
     */
    kScreenCaptureSourceTypeUnknown,

    /** {zh}
     * @brief 应用程序的窗口
     */
    /** {en}
     * @brief Application window
     */
    kScreenCaptureSourceTypeWindow,

    /** {zh}
     * @brief 桌面
     */
    /** {en}
     * @brief Desktop
     */
    kScreenCaptureSourceTypeScreen
};

/** {zh}
 * @type keytype
 * @brief 屏幕共享对象的详细信息
 */
/** {en}
 * @type keytype
 * @brief Detailed information of the screen sharing object
 */
struct ScreenCaptureSourceInfo {
    /** {zh}
     * @brief 屏幕共享对象的类型，参看 ScreenCaptureSourceType{@link #ScreenCaptureSourceType}
     */
    /** {en}
     * @brief Type of the screen-sharing object. Refer to ScreenCaptureSourceType{@link #ScreenCaptureSourceType} for the type of shared object.
     */
    ScreenCaptureSourceType type = kScreenCaptureSourceTypeUnknown;

    /** {zh}
     * @brief 屏幕共享对象的 ID
     */
    /** {en}
     * @brief ID of the screen-sharing object
     */
    view_t source_id = nullptr;
    /** {zh}
     * @brief 屏幕共享对象的名称<br>
     *        调用 release{@link #IScreenCaptureSourceList#release} 时将被释放，请及时转为 string 对象保存
     */
    /** {en}
     * @brief Name of the screen-sharing object<br>
     *        Make sure you haved save them as `string` objects before calling release{@link #IScreenCaptureSourceList#release} to release the dynamic memory.
     */
    const char* source_name = nullptr;
    /** {zh}
     * @brief 共享的应用窗体所属应用的名称<br>
     *        当共享对象为应用窗体时有效 <br>
     *        调用 release{@link #IScreenCaptureSourceList#release} 时将被释放，请及时转为 string 对象保存<br>
     */
    /** {en}
     * @brief The title of the application to be shared.<br>
     *        Only available if the sharing object is an application windows.<br>
     *        Make sure you haved save them as `string` objects before calling release{@link #IScreenCaptureSourceList#release} to release the dynamic memory.
     */
    const char* application = nullptr;
    /** {zh}
     * @brief 共享的应用窗体所属应用进程的 pid<br>
     *        当共享对象为应用窗体时有效 <br>
     */
     /** {en}
     * @brief Process pid of the application to be shared.<br>
     *        Only available if the sharing object is an application windows.<br>
     */
    int pid = 0;
    /** {zh}
     * @brief 共享的屏幕是否为主屏。<br>
     *        当共享对象为屏幕时有效 <br>
     */
     /** {en}
     * @brief Tag for the screen to be shared identifying whether it is the primary screen<br>
     *        Only available when the screen-sharing object is a screen. <br>
     */
    bool primary_monitor = false;
    /** {zh}
     * @brief 屏幕共享对象的坐标。详见 Rectangle{@link #Rectangle}。<br>
     *        仅在采集源为显示器屏幕时有效。<br>
     *        + 对于多屏幕的场景，不同平台的坐标系原点不同：<br>
     *          - 对于 Windows 平台，屏幕坐标以主屏左上角为原点 (0, 0)，向右向下扩展。<br>
     *          — 对于 Linux 平台，屏幕坐标以 **恰好包住所有显示器的矩形区域的左上角** 为原点 (0, 0)，向右向下扩展。<br>
     *        + 对于不同平台，窗口区域不同：<br>
     *          - 对于 Windows 和 macOS 平台，窗口区域包含系统标题栏。<br>
     *          - 对于 Linux 平台，窗口区域不包含系统标题栏。
     */
    /** {en}
     * @brief Coordinates of the screen-sharing object. See Rectangle{@link #Rectangle}.<br>
     *        Valid only when the capture source is the monitor screen. <br>
      *       + When there are several screens, the origin (0, 0) is different for different platforms: <br>
      *         - For Windows, the origin (0, 0) is the top-left corner of the main screen. <br>
      *         - For Linux, the origin (0, 0) is the top-left corner of the rectangle that merely covers all screens. <br>
      *       + The region of the window is different for different platforms:
      *         - For Windows and macOS, the region includes the system title bar of the window. <br>
      *         - For Linux, the region does not includes the system title bar of the window. 
     */
    Rectangle region_rect;
};

/** {zh}
 * @type api
 * @region 屏幕共享
 * @brief 屏幕共享对象信息列表
 * 共享对象相关数据将在调用 release{@link #IScreenCaptureSourceList#release} 后被释放。
 */
/** {en}
 * @type api
 * @region  screen sharing
 * @brief  Information list of the screen-sharing objects
 * Calling release{@link #IScreenCaptureSourceList#release} will release all the objects related to this class.
 */
class IScreenCaptureSourceList {
public:
   /**
    * @hidden constructor/destructor
    */
    virtual ~IScreenCaptureSourceList() {
    }
    /** {zh}
     * @type api
     * @region 屏幕共享
     * @brief 获取列表长度
     * @return 可共享对象数量
     */
    /** {en}
     * @type api
     * @region Screen sharing
     * @brief Get the length of the list
     * @return Number of the items in the list
     */
    virtual int32_t getCount() = 0;

    /** {zh}
     * @type api
     * @region 屏幕共享
     * @brief 根据索引号，获取屏幕共享列表中的元素
     * @param [in] index 列表索引号
     * @return 屏幕源类型信息，详见 ScreenCaptureSourceInfo{@link #ScreenCaptureSourceInfo}。
     */
    /** {en}
     * @type api
     * @region Screen share
     * @brief According to the index, get the elements in the screen share list
     * @param [in] index Index number
     * @return Screen source item. Refer to ScreenCaptureSourceInfo{@link #ScreenCaptureSourceInfo} for more details.
     */
    virtual ScreenCaptureSourceInfo getSourceInfo(int32_t index) = 0;

    /** {zh}
     * @type api
     * @region 屏幕共享
     * @brief IScreenCaptureSourceList{@link #IScreenCaptureSourceList} 使用结束后，调用本接口删除对象，清空和释放内存。
     */
    /** {en}
     * @type api
     * @region Screen sharing
     * @brief If you are finished with the IScreenCaptureSourceList{@link #IScreenCaptureSourceList}, call this API to destruct it and release the memory.
     */
    virtual void release() = 0;
};

/** {zh}
 * @type callback
 * @brief 自定义编码帧回调类
 * 注意：回调函数是在 SDK 内部线程（非 UI 线程）同步抛出来的，请不要做耗时操作或直接操作 UI，否则可能导致 app 崩溃。
 */
/** {en}
 * @type callback
 * @brief  Custom coded frame callback class
 * Note: Callback functions are thrown synchronously in a non-UI thread within the SDK. Therefore, you must not perform any time-consuming operations or direct UI operations within the callback function, as this may cause the app to crash.
 */
class IExternalVideoEncoderEventHandler {
public:
    /** {zh}
     * @hidden constructor/destructor
     * @brief 析构函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Destructor
     */
    virtual ~IExternalVideoEncoderEventHandler(){}
    /** {zh}
     * @type callback
     * @region 视频管理
     * @brief 提示自定义编码帧可以开始推送的回调。  <br>
     *        收到该回调后，你即可调用 pushExternalEncodedVideoFrame{@link #IRTCVideo#pushExternalEncodedVideoFrame} 向 SDK 推送自定义编码视频帧
     * @param [in] index 可以推送的编码流的属性，参看 StreamIndex{@link #StreamIndex}
     */
    /** {en}
     * @type callback
     * @region Video management
     * @brief Prompt custom encoded frames to start pushing callbacks.   <br>
     *         After receiving this callback, you can call pushExternalEncodedVideoFrame{@link #IRTCVideo#pushExternalEncodedVideoFrame} to push a custom encoded video frame to the SDK
     * @param  [in] index The properties of the encoded stream that can be pushed. See StreamIndex{@link #StreamIndex}
     */
    virtual void onStart(StreamIndex index) = 0;
    /** {zh}
     * @type callback
     * @region 视频管理
     * @brief 当收到该回调时，你需停止向 SDK 推送自定义编码视频帧
     * @param [in] index 需停止推送的编码流的属性，参看 StreamIndex{@link #StreamIndex}
     */
    /** {en}
     * @type callback
     * @region Video management
     * @brief When you receive the callback, you need to stop pushing custom encoded video frames to the SDK
     * @param  [in] index The properties of the encoded stream that you need to stop pushing. See StreamIndex{@link #StreamIndex}
     */
    virtual void onStop(StreamIndex index) = 0;
    /** {zh}
     * @type callback
     * @region 视频管理
     * @brief 当自定义编码流的帧率或码率发生变化时，触发该回调
     * @param [in] index 发生变化的编码流的属性，参看 StreamIndex{@link #StreamIndex}
     * @param [in] video_index 对应编码流的下标
     * @param [in] info 变化后的编码流信息，参看 VideoRateInfo{@link #VideoRateInfo}
     */
    /** {en}
     * @type callback
     * @region Video management
     * @brief When the frame rate or bit rate of a custom encoded stream changes, the callback is triggered
     * @param  [in] index The Properties of the encoded stream with the changed index. See StreamIndex{@link #StreamIndex}
     * @param  [in] video_index The subscript of the corresponding encoded stream
     * @param  [in] info The encoded stream information after the change. See VideoRateInfo{@link #VideoRateInfo}
     */
    virtual void onRateUpdate(StreamIndex index, int32_t video_index, VideoRateInfo info) = 0;
    /** {zh}
     * @type callback
     * @region 视频管理
     * @brief 提示流发布端需重新生成关键帧的回调
     * @param [in] index 远端编码流的属性，参看 StreamIndex{@link #StreamIndex}
     * @param [in] video_index 对应编码流的下标
     */
    /** {en}
     * @type callback
     * @region Video management
     * @brief This callback is used to inform the stream publisher that a keyframe needs to be regenerated.
     * @param [in] index Properties of the remote encoded stream. See StreamIndex{@link #StreamIndex}
     * @param [in] video_index The subscript of the corresponding encoded stream
     */
    virtual void onRequestKeyFrame(StreamIndex index, int32_t video_index) = 0;
    /** {zh}
     * @valid since 3.56
     * @type callback
     * @brief 作为自定义编码视频流的发送端，你会在视频流可发送状态发生变化时，收到此回调。
     *        你可以根据此回调的提示，仅对可发送的视频流进行编码，以降低本端视频编码性能消耗。此回调会根据多个因素综合判断触发，包括：本端设备性能和本端网络性能，以及按需订阅场景下，远端用户是否订阅。
     * @param index 远端编码流的属性，参看 StreamIndex{@link #StreamIndex}。
     * @param video_index 对应编码流的下标
     * @param active 该路流可发送状态
     * @notes 要收到此回调，必须调用 setVideoSourceType{@link #IRTCVideo#setVideoSourceType} 设置视频源是自定义编码，且通过 setExternalVideoEncoderEventHandler{@link #IRTCVideo#setExternalVideoEncoderEventHandler} 设置了回调句柄。
     */
    /** {en}
     * @valid since 3.56
     * @type callback
     * @brief As the sender of a external encoded video stream, you will receive this callback at certain moments. 
     *        Based on the hints of this callback, you can selectively encode the video stream that is ready for transmission, in order to reduce the performance impact of video encoding on the local device. This callback is triggered based on a combination of factors, including  the performance of the local device, the local network, and whether the stream is subscribed by the remote user.
     * @param index See StreamIndex{@link #StreamIndex}.
     * @param video_index Subscript of the corresponding encoded stream.
     * @param active The active state of the corresponding encoded stream.
     * @notes To receive the callback, call setVideoSourceType{@link #IRTCVideo#setVideoSourceType} to set the input video source to custom encoded video and call setExternalVideoEncoderEventHandler{@link #IRTCVideo#setExternalVideoEncoderEventHandler} to set the callback handler.
     */
    virtual void onActiveVideoLayer(StreamIndex index, int32_t video_index, bool active) = 0;
};

/** {zh}
 * @type callback
 * @region 视频数据回调
 * @brief 本地视频帧监测器
 * 注意：回调函数是在 SDK 内部线程（非 UI 线程）同步抛出来的，请不要做耗时操作或直接操作 UI，否则可能导致 app 崩溃。
 */
/** {en}
 * @type callback
 * @region Video Data Callback
 * @brief Local video frame observer
 * Note: Callback functions are thrown synchronously in a non-UI thread within the SDK. Therefore, you must not perform any time-consuming operations or direct UI operations within the callback function, as this may cause the app to crash.
 */
class ILocalEncodedVideoFrameObserver {
public:
    /** {zh}
     * @hidden constructor/destructor
     * @brief 析构函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Destructor
     */
    virtual ~ILocalEncodedVideoFrameObserver() {
    }
    /** {zh}
     * @type callback
     * @region 视频数据回调
     * @brief 调用 registerLocalEncodedVideoFrameObserver{@link #IRTCVideo#registerLocalEncodedVideoFrameObserver} 后，SDK 每次使用内部采集，采集到一帧视频帧，或收到一帧外部视频帧时，都会回调该事件。
     * @param [in] type 本地视频帧类型，参看 StreamIndex{@link #StreamIndex}
     * @param [in] video_stream 本地视频帧信息，参看 IEncodedVideoFrame{@link #IEncodedVideoFrame}
     */
    /** {en}
     * @type callback
     * @region Video Data Callback
     * @brief After calling registerLocalEncodedVideoFrameObserver{@link #IRTCVideo#registerLocalEncodedVideoFrameObserver}, SDK will trigger this callback when it receives local video frames.
     * @param [in] type Type of the local video frame. See StreamIndex{@link #StreamIndex}.
     * @param [in] video_stream Information about the local video frame. See IEncodedVideoFrame{@link #IEncodedVideoFrame}.
     */
    virtual void onLocalEncodedVideoFrame(StreamIndex type, const IEncodedVideoFrame& video_stream) = 0;
};

/** {zh}
 * @type callback
 * @region 视频管理
 * @brief 远端编码后视频数据监测器
 * 注意：回调函数是在 SDK 内部线程（非 UI 线程）同步抛出来的，请不要做耗时操作或直接操作 UI，否则可能导致 app 崩溃。
 */
/** {en}
 * @type callback
 * @region  video management
 * @brief  Remote encoded video data monitor
 * Note: Callback functions are thrown synchronously in a non-UI thread within the SDK. Therefore, you must not perform any time-consuming operations or direct UI operations within the callback function, as this may cause the app to crash.
 */
class IRemoteEncodedVideoFrameObserver {
public:
    /** {zh}
     * @hidden constructor/destructor
     * @brief 析构函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief  Destructor
     */
    virtual ~IRemoteEncodedVideoFrameObserver() {
    }
    /** {zh}
     * @type callback
     * @region 视频数据回调
     * @brief 调用 registerRemoteEncodedVideoFrameObserver{@link #IRTCVideo#registerRemoteEncodedVideoFrameObserver} 后，SDK 监测到远端编码后视频数据时，触发该回调
     * @param [in] stream_info 收到的远端流信息，参看 RemoteStreamKey{@link #RemoteStreamKey}
     * @param [in] video_stream 收到的远端视频帧信息，参看 IEncodedVideoFrame{@link #IEncodedVideoFrame}
     */
    /** {en}
     * @type callback
     * @region  video data callback
     * @brief  Call registerRemoteEncodedVideoFrameObserver{@link #IRTCVideo#registerRemoteEncodedVideoFrameObserver}, the callback is triggered when the SDK detects the remote encoded video data
     * @param  [in] stream_info The received remote stream information. See RemoteStreamKey{@link #RemoteStreamKey}
     * @param  [in] video_stream The received remote video frame information. See IEncodedVideoFrame{@link #IEncodedVideoFrame}
     */
    virtual void onRemoteEncodedVideoFrame(const RemoteStreamKey& stream_info, const IEncodedVideoFrame& video_stream) = 0;
};

/** {zh}
 * @type keytype
 * @brief 视频帧中包含的 metadata 信息
 */
/** {en}
 * @type keytype
 * @brief The metadata information contained in the video frame
 */
struct VideoMetadataBuffer {
    /** {zh}
     * @brief 接收或者发送的 metadata
     */
    /** {en}
     * @brief Received or sent metadata
     */
    char* data;
    /** {zh}
     * @brief 接收或者发送的 metadata 数据大小，不能超过 1024
     */
    /** {en}
     * @brief The size of metadata data received or sent cannot exceed 1024
     */
    int size;
    /** {zh}
     * @brief 包含 metadata 视频帧的时间戳，单位微秒
     */
    /** {en}
     * @brief A timestamp containing metadata video frames in microseconds
     */
    int64_t timestamp_us;
};

/** {zh}
 * @deprecated since 3.26 and will be deleted in 3.51, use [sendSEIMessage](70098#IRTCVideo-sendseimessage-2) instead.
 * @type callback
 * @region 视频数据回调
 * @brief metadata 观察者，可以接收媒体流中的 metadata， 或者向媒体流中添加 metadata
 * 注意：回调函数是在 SDK 内部线程（非 UI 线程）同步抛出来的，请不要做耗时操作或直接操作 UI，否则可能导致 app 崩溃。
 */
/** {en}
 * @deprecated since 3.45 and will be deleted in 3.51, use [sendSEIMessage](70098#IRTCVideo-sendseimessage-2) instead.
 * @type callback
 * @region video data callback
 * @brief Metadata observer, you can receive metadata in the media stream, or add metadata to the media stream
 * Note: Callback functions are thrown synchronously in a non-UI thread within the SDK. Therefore, you must not perform any time-consuming operations or direct UI operations within the callback function, as this may cause the app to crash.
 */
class IMetadataObserver {
public:
    /**
     * @hidden constructor/destructor
     */
    virtual ~IMetadataObserver() {
    }

    /** {zh}
     * @type callback
     * @region 视频数据回调
     * @brief 当 SDK 准备发送一个视频帧时，会回调该事件，以确定是否需要在该视频帧中添加 metadata。
     * @param [in/out] metadata 待发送的数据，把数据拷贝到 data 字段中，并将 size 设置为真实的大小。
     * @return  <br>
     *        + true：需要向视频帧中添加 metadata  <br>
     *        + false：不需要向视频帧中添加 metadata  <br>
     * @notes  <br>
     *        + metadata 的大小不能超过1024字节  <br>
     *        + metadata 中的 timestampUs 是输入字段，代表视频帧的时间戳，做同步使用，不需要修改。  <br>
     *        + 回调中不能有耗时操作，以免影响视频卡顿  <br>
     */
    /** {en}
     * @type callback
     * @region Video data callback
     * @brief When the SDK is ready to send a video frame, the event is called back to determine whether metadata needs to be added to the video frame.
     * @param  [in/out] Metadata The data to be sent, copy the data into the data field, and set the size to the real size.
     * @return   <br>
     *         + true: You need to add metadata <br>
     *         + false: You don't need to add metadata <br>
     * @notes   <br>
     *         + The size of metadata cannot exceed 1024 bytes <br>
     *         + The timestampUs in metadata is the input field, which represents the timestamp of the video frame. It is used for synchronization and does not need to be modified .. <br>
     *         + There must be no time-consuming operations in the callback to avoid affecting the video card <br>
     */
    virtual bool onReadyToSendMetadata(VideoMetadataBuffer* metadata) = 0;

    /** {zh}
     * @type callback
     * @region 视频数据回调
     * @brief 当 SDK 收到一个视频帧时，并且其中包含 medatada 时，会回调该事件。
     * @param [in] roomid 当前帧所属的房间 ID。
     * @param [in] uid 当前帧所属的用户 ID。
     * @param [in] metadata 视频帧中包含的 metadata 信息。参看 VideoMetadataBuffer{@link #VideoMetadataBuffer}。
     * @notes 回调中不能有耗时操作，以免影响视频卡顿。
     */
    /** {en}
     * @type callback
     * @region Video data callback
     * @brief When a video frame is received by the SDK and contains a medatada, the event is called back.
     * @param  [in] roomid The room ID to which the current frame belongs.
     * @param  [in] uid The user ID to which the current frame belongs.
     * @param  [in] metadata The metadata information contained in the video frame. See VideoMetadataBuffer{@link #VideoMetadataBuffer}.
     * @notes There must be no time-consuming operations in the callback so as not to affect the video card.
     */
    virtual void onMetadataReceived(const char* roomid, const char* uid, const VideoMetadataBuffer& metadata) = 0;
};

/** {zh}
 * @hidden
 * @deprecated since 3.50 and will be deleted in 3.55.
 * @type callback
 * @region 视频管理
 * @brief 视频数据回调观察者
 */
/** {en}
 * @hidden
 * @deprecated since 3.50 and will be deleted in 3.55.
 * @type callback
 * @region Video Management
 * @brief Video data callback observer
 */
class IVideoFrameObserver {
public:
    /** {zh}
     * @hidden constructor/destructor
     * @brief 析构函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Destructor
     */
    virtual ~IVideoFrameObserver() = default;

    /** {zh}
     * @type callback
     * @region 视频管理
     * @brief 获取采集成功的本地屏幕视频帧，用于自定义处理或渲染。
     * @param [in] video_frame 视频数据，参看 IVideoFrame{@link #IVideoFrame}。
     */
    /** {en}
     * @type callback
     * @region Video Management
     * @brief Get the successfully captured local screen video frames for custom processing or rendering.
     * @param [in] video_frame Video data. See IVideoFrame{@link #IVideoFrame}.
     */
    virtual bool onLocalScreenFrame(IVideoFrame* video_frame) = 0;

    /** {zh}
     * @type callback
     * @region 视频管理
     * @brief 获取采集成功的本地摄像头流视频帧，用于自定义处理或渲染。
     * @param [in] video_frame 视频数据，参看 IVideoFrame{@link #IVideoFrame}。
     */
    /** {en}
     * @type callback
     * @region Video Management
     * @brief Get the successfully captured local camera stream for custom processing or rendering.
     * @param [in] video_frame Video data. See IVideoFrame{@link #IVideoFrame}.
     */
    virtual bool onLocalVideoFrame(IVideoFrame* video_frame) = 0;

    /** {zh}
     * @type callback
     * @region 视频管理
     * @brief 获取采集成功的远端屏幕视频帧，用于自定义处理或渲染。
     * @param [in] roomid 房间 ID。
     * @param [in] uid 远端用户 ID。
     * @param [in] video_frame 视频数据，参看 IVideoFrame{@link #IVideoFrame}。
     */
    /** {en}
     * @type callback
     * @region Video Management
     * @brief Get the successfully captured remote screen video frames for custom processing or rendering.
     * @param [in] roomid The ID of the room from which the video is streamed.
     * @param [in] uid The ID of the remote user who published the stream.
     * @param [in] video_frame Video data. See IVideoFrame{@link #IVideoFrame}.
     */
    virtual bool onRemoteScreenFrame(const char* roomid, const char* uid, IVideoFrame* video_frame) = 0;

    /** {zh}
     * @type callback
     * @region 视频管理
     * @brief 获取采集成功的远端摄像头流视频帧，用于自定义处理或渲染。
     * @param [in] roomid 房间 ID。
     * @param [in] uid 远端用户 ID。
     * @param [in] video_frame 视频数据，参看 IVideoFrame{@link #IVideoFrame}。
     * @notes 不同的平台上（macOS, Windows, Linux）上获取的视频帧的 pixelFormat 可能不同。
     */
    /** {en}
     * @type callback
     * @region Video Management
     * @brief Get the successfully captured remote camera stream for custom processing or rendering.
     * @param [in] roomid The ID of the room from which the video is streamed.
     * @param [in] uid The ID of the remote user who published the stream.
     * @param [in] video_frame Video data. See IVideoFrame{@link #IVideoFrame}.
     * @notes The pixelFormat of the received video frame depends on your platform (macOS, Windows, Linux).
     */
    virtual bool onRemoteVideoFrame(const char* roomid, const char* uid, IVideoFrame* video_frame) = 0;

    /** {zh}
     * @type callback
     * @region 视频管理
     * @brief 拼接视频数据回调
     * @param [in] roomid 房间 id
     * @param [in] uid 远端用户ID
     * @param [in] video_frame 视频数据，详见 IVideoFrame{@link #IVideoFrame}
     */
    /** {en}
     * @type callback
     * @region video management
     * @brief Callback carrying splicing video data
     * @param [in] roomid The ID of the room from which the video is streamed.
     * @param [in] uid The ID of the remote user who published the stream.
     * @param [in] video_frame Video data. See IVideoFrame{@link #IVideoFrame}.
     */
    virtual bool onMergeFrame(const char* roomid, const char* uid, IVideoFrame* video_frame) {
        return false;
    }
};
/** {zh}
 * @hidden(Linux)
 * @type callback
 * @brief 截图的回调。
 * 注意：回调函数是在 SDK 内部线程（非 UI 线程）同步抛出来的，请不要做耗时操作或直接操作 UI，否则可能导致 app 崩溃。
 */
/** {en}
 * @hidden(Linux)
 * @type callback
 * @brief The callback of taking snapshots.
 * Note: Callback functions are thrown synchronously in a non-UI thread within the SDK. Therefore, you must not perform any time-consuming operations or direct UI operations within the callback function, as this may cause the app to crash.
 */
class ISnapshotResultCallback {
public:
    /**
     * @hidden constructor/destructor
     */
    virtual ~ISnapshotResultCallback() = default;
    /** {zh}
     * @type callback
     * @brief 调用 takeLocalSnapshot{@link #IRTCVideo#takeLocalSnapshot} 截取视频画面时，收到此回调。
     * @param [in] task_id 本地截图任务的编号。和 takeLocalSnapshot{@link #IRTCVideo#takeLocalSnapshot} 的返回值一致。
     * @param [in] stream_index 截图的视频流的属性，参看 StreamIndex{@link #StreamIndex}。
     * @param [in] image 截图。你可以保存为文件，或对其进行二次处理。截图失败时，为空。
     * @param [in] error_code 截图错误码：<br>
     *        + 0: 成功 <br>
     *        + -1: 截图错误。生成图片数据失败或 RGBA 编码失败 <br>
     *        + -2: 截图错误。流无效。
     *        + -3: 截图错误。截图超时,超时时间1秒。
     */
    /** {en}
     * @type callback
     * @brief Receives the callback after calling takeLocalSnapshot{@link #IRTCVideo#takeLocalSnapshot}.
     * @param [in] task_id The index for the snapshot, the same as the return value of takeLocalSnapshot{@link #IRTCVideo#takeLocalSnapshot}.
     * @param [in] stream_index See StreamIndex{@link #StreamIndex}.
     * @param [in] image The snapshot image. If the snapshot task fails, the value is `null`.
     * @param [in] error_code Error code: <br>
     *        + 0: Success. <br>
     *        + -1: Failure. Fails to generate the image. <br>
     *        + -2: Failure. The stream is invalid.
     *        + -3: Failure. snapshot timeout, default 1s.
     */
    virtual void onTakeLocalSnapshotResult(long task_id, StreamIndex stream_index, IVideoFrame* image, int error_code) = 0;
    /** {zh}
     * @type callback
     * @brief 调用 takeRemoteSnapshot{@link #IRTCVideo#takeRemoteSnapshot} 截取视频画面时，收到此回调。
     * @param [in] task_id 远端截图任务的编号。和 takeRemoteSnapshot{@link #IRTCVideo#takeRemoteSnapshot} 的返回值一致。
     * @param [in] stream_key 截图的视频流，参看 RemoteStreamKey{@link #RemoteStreamKey}。
     * @param [in] image 截图。你可以保存为文件，或对其进行二次处理。截图失败时，为空。
     * @param [in] error_code 截图错误码：<br>
     *        + 0: 成功 <br>
     *        + -1: 截图错误。生成图片数据失败或 RGBA 编码失败 <br>
     *        + -2: 截图错误。流无效。
     *        + -3: 截图错误。截图超时,超时时间1秒。
     */
    /** {en}
     * @type callback
     * @brief Receives the callback after calling takeRemoteSnapshot{@link #IRTCVideo#takeRemoteSnapshot}.
     * @param [in] task_id The index for the remote snapshot, the same as the return value of takeRemoteSnapshot{@link #IRTCVideo#takeRemoteSnapshot}.
     * @param [in] stream_key See RemoteStreamKey{@link #RemoteStreamKey}.
     * @param [in] image The snapshot image. If the snapshot task fails, the value is `null`.
     * @param [in] error_code Error code: <br>
     *        + 0: Success. <br>
     *        + -1: Failure. Fails to generate the image. <br>
     *        + -2: Failure. The stream is invalid.
     *        + -3: Failure. snapshot timeout, default 1s.
     */
    virtual void onTakeRemoteSnapshotResult(long task_id, RemoteStreamKey stream_key, IVideoFrame* image, int error_code) = 0;
};
/** {zh}
 * @hidden(macOS, Windows, Linux)
 * @type keytype
 * @brief 蜂窝网络辅助增强应用的媒体模式
 */
/** {en}
 * @hidden(macOS, Windows, Linux)
 * @type keytype
 * @brief Media type for cellular assisted Enhancement
 */
struct MediaTypeEnhancementConfig {
    /** {zh}
     * @brief 对信令消息，是否启用蜂窝网络辅助增强。默认不启用。
     */
    /** {en}
     * @brief Apply to signaling or not. Not by default.
     */
    bool enhance_signaling = false;
    /** {zh}
     * @brief 对屏幕共享以外的其他音频，是否启用蜂窝网络辅助增强。默认不启用。
     */
    /** {en}
     * @brief Apply to audio stream (Screen-sharing audio not included) or not. Not by default.
     */
    bool enhance_audio = false;
    /** {zh}
     * @brief 对屏幕共享音频，是否启用蜂窝网络辅助增强。默认不启用。
     */
    /** {en}
     * @brief Apply to screen sharing audio or not. Not by default.
     */
    bool enhance_screen_audio = false;
    /** {zh}
     * @brief 对屏幕共享视频以外的其他视频，是否启用蜂窝网络辅助增强。默认不启用。
     */
    /** {en}
     * @brief Apply to video (Screen-sharing video not included) or not. Not by default.
     */
    bool enhance_video = false;
    /** {zh}
     * @brief 对屏幕共享视频，是否启用蜂窝网络辅助增强。默认不启用。
     */
    /** {en}
     * @brief Apply to screen sharing video or not. Not by default.
     */
    bool enhance_screen_video = false;
};

}  // namespace bytertc
