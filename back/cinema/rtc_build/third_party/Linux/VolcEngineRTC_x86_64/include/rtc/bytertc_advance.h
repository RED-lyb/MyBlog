/*
 * Copyright (c) 2020 The VolcEngineRTC project authors. All Rights Reserved.
 * @brief VolcEngineRTC Advance API
*/

#pragma once

#include "../bytertc_video.h"

#include <stdint.h>
#ifdef __ANDROID__
#include "jni.h"
#endif


#ifdef __GNUC__
#    define attribute_deprecated __attribute__((deprecated))
#elif defined(_MSC_VER)
#    define attribute_deprecated __declspec(deprecated)
#else
#    define attribute_deprecated
#endif

namespace bytertc {

/** {zh}
 * @hidden for internal use only
 * @type
 * @brief RTC Audio Dump 节点配置。
 * 要与bae_audio_sample_interface中
 * 的AudioSampleType枚举和AudioSampleConfigure保持一致。
 */
/** {en}
 * @hidden for internal use only
 * @type
 * @brief RTC Audio Dump node configuration.
 * Be consistent with the AudioSampleType enumeration and AudioSampleConfigure in the bae_audio_sample_interface
 * .
 */
struct RTCAudioSampleConfigure {
    bool aec_near_in_enable = false;
    bool aec_far_in_enable = false;
    bool aec_far_in_ref_enable = false;
    bool aec_out_enable = false;
    bool agc_out_enable = false;
    bool ns_out_enable = false;
    bool ainr_out_enable = false;
    bool mix_out_enable = false;
    bool send2encoder_enable = false;
    bool audio_share_in_enable = false;
    bool audio_share_win_ref_enable = false;
    bool audio_share_out_enable = false;
    bool external_audio_in_enable = false;
    bool pitchfilter_out_enable = false;
    bool decoder_out_enable = false;
    bool front_aec_near_ref_enable = false;
    void reset() {
        aec_near_in_enable = false;
        aec_far_in_enable = false;
        aec_far_in_ref_enable = false;
        aec_out_enable = false;
        agc_out_enable = false;
        ns_out_enable = false;
        ainr_out_enable = false;
        mix_out_enable = false;
        send2encoder_enable = false;
        audio_share_in_enable = false;
        audio_share_win_ref_enable = false;
        audio_share_out_enable = false;
        external_audio_in_enable = false;
        pitchfilter_out_enable = false;
        decoder_out_enable = false;
        front_aec_near_ref_enable = false;
    }
    void normalMode() {
        aec_near_in_enable = true;
        aec_far_in_ref_enable = true;
        mix_out_enable = true;
    }
    void allMode() {
        aec_near_in_enable = true;
        aec_far_in_enable = true;
        aec_far_in_ref_enable = true;
        aec_out_enable = true;
        agc_out_enable = true;
        ns_out_enable = true;
        ainr_out_enable = true;
        mix_out_enable = true;
        send2encoder_enable = true;
        audio_share_in_enable = true;
        audio_share_win_ref_enable = true;
        audio_share_out_enable = true;
        external_audio_in_enable = true;
        pitchfilter_out_enable = true;
        decoder_out_enable = true;
        front_aec_near_ref_enable = true;
    }
};

/** {zh}
 * @hidden for internal use only
 * @type keytype
 * @brief SDK 的服务器环境。
 */
/** {en}
 * @hidden for internal use only
 * @type keytype
 * @brief SDK  server environment.
 */
enum Env {
    /** {zh}
     * @brief 线上环境。
     */
    /** {en}
     * @brief  Online environment.
     */
    kEnvProduct = 0,
    /** {zh}
     * @brief BOE 环境。
     */
    /** {en}
     * @brief BOE  environment.
     */
    kEnvBOE,
    /** {zh}
     * @brief 测试环境。
     */
    /** {en}
     * @brief  Test environment.
     */
    kEnvTest
};

attribute_deprecated
/** {zh}
 * @hidden for internal use only
 * @deprecated
 * @type api
 * @region 引擎管理
 * @brief 设置 SDK 当前使用的环境。
 * @param [in] env SDK 使用的环境参数，详见：Env{@link #Env} 。
 * @return
 *        0： 设置成功
 *        -1：设置失败
 * @notes
 *        1.本函数是可选函数，默认使用正式环境；
 *        2.本函数必须在创建 RtcEngine 实例 createRtcEngine{@link #createRtcEngine} 前调用。
 */
/** {en}
 * @hidden for internal use only
 * @deprecated
 * @type api
 * @region Engine management
 * @brief Set the environment currently used by the SDK.
 * @param  [in] env The environment parameters used by the SDK are detailed in: Env{@link #Env}.
 * @return
 *        0: Setup succeeded
 *        -1: Setup failed
 * @notes
 *        1. This function is optional function, the default use of official environment;
 *        2. This function must be called before creating the RtcEngine instance createRtcEngine{@link #createRtcEngine}.
 */
BYTERTC_API BYTERTC_DEPRECATED int setEnv(Env env);

attribute_deprecated
/** {zh}
 * @hidden for internal use only
 * @deprecated
 * @brief 设置设备ID
 * @param [in] device_id app根据当前软硬件环境生成的唯一设备id
 */
/** {en}
 * @hidden for internal use only
 * @deprecated
 * @brief  Set the device ID
 * @param  [in] device_id App to generate a unique device id based on the current software and hardware environment
 */
BYTERTC_API BYTERTC_DEPRECATED void setDeviceId(const char* device_id);
/** {zh}
 * @hidden for internal use only
 * @brief 设置应用的状态
 * @param [in] engine
 *       要通知的引擎
 * @param [in] app_state 应用状态字符串
 */
/** {en}
 * @hidden for internal use only
 * @brief  Set the state of the application
 * @param  [in] engine
 *        Engine to notify
 * @param  [in] app_state Application state string
 */
BYTERTC_API void setAppState(void* engine, const char* app_state);

attribute_deprecated
/** {zh}
 * @hidden for internal use only
 * @deprecated
 * @type api
 * @region 房间管理
 * @brief 私有接口
 * @param [in] parameters JSON字符串
 */
/** {en}
 * @hidden for internal use only
 * @deprecated
 * @type api
 * @region room management
 * @brief Private interface
 * @param  [in] parameters JSON string
 */
BYTERTC_API int setParameters(const char* parameters);

#ifdef __ANDROID__
/** {zh}
 * @hidden(iOS,macOS,Windows,Linux) for internal use only
 * @type api
 * @region 视频管理
 * @brief 用于给编码器设置共享的EGLContext，该接口需要传入一个 android.opengl.EGLContext 类型的EGLContext
 * 如果只有C++的EGLContext，则需要在绑定了EGLContext的线程环境下执行 setHardWareEncodeContext() 方法设置。
 * 设置后，RTC的编码器即可和当前的EGLContext共享资源。
 * 如果Android使用纯C++接口，则该方法必须在引擎创建前设置，用于初始化EGLContext，如果没有共享的EGLContext，参数传递nullptr即可
 * 引擎销毁后，应该调用 clearHardWareEncodeContext() 来进行资源释放
 * @param [in] j_egl_context
 *      传入Java的 android.opengl.EGLContext 类型的EGLContext
 * @return
 *      true: 设置成功
 *      false：设置失败
 */
/** {en}
 * @hidden(iOS,macOS,Windows,Linux) for internal use only
 * @type api
 * @region Video Management
 * @brief Is used to set the shared EGLContext for the encoder. The interface needs to pass in an EGLContext of type android.opengl. EGLContext
 * If there are only C++ EGLContext, you need to perform the setHardWareEncodeContext () method setting in a threaded environment bound with EGLContext.
 * Once set, the RTC encoder can share resources with the current EGLContext.
 * If Android uses a pure C++ interface, this method must be set before the engine is created to initialize EGLContext. If there is no shared EGLContext, the parameter can be passed nullptr
 * After the engine is destroyed, clearHardWareEncodeContext () should be called to release resources
 * @param  [in] j_egl_context
 *      Pass in Java EGLContext of the android.opengl. EGLContext type
 * @return
 *      True: set successfully
 *      False: set failed
 */
BYTERTC_API bool setHardWareEncodeContext(jobject j_egl_context);

/** {zh}
 * @hidden(iOS,macOS,Windows,Linux) for internal use only
 * @type api
 * @region 视频管理
 * @brief 用于给编码器设置共享的EGLContext，该接口需要在绑定了EGLContext的接口下执行方法设置。
 * 设置后，RTC的编码器即可和当前的EGLContext共享资源。
 * 如果Android使用纯C++接口，则该方法必须在引擎创建前设置，如果没有绑定了EGLContext的线程环境，可以使用参数为jobject的接口替代
 * 引擎销毁后，应该调用 clearHardWareEncodeContext() 来进行资源释放
 * @return
 *      true: 设置成功
 *      false：设置失败
 */
/** {en}
 * @hidden(iOS,macOS,Windows,Linux) for internal use only
 * @type api
 * @region Video Management
 * @brief Is used to set the shared EGLContext for the encoder. The interface needs to perform method settings under the interface bound with EGLContext.
 * Once set, the RTC encoder can share resources with the current EGLContext.
 * If Android uses a pure C++ interface, this method must be set before the engine is created. If there is no threaded environment bound with EGLContext, you can use an interface with the parameter jobject instead
 * After the engine is destroyed, clearHardWareEncodeContext () should be called for resource release
 * @return
 *      True: set successfully
 *      False: set failed
 */
BYTERTC_API bool setHardWareEncodeContext();

/** {zh}
 * @hidden(iOS,macOS,Windows,Linux) for internal use only
 * @type api
 * @region 视频管理
 * @brief 用于清除共享的EGLContext，在引擎销毁后，如果确定之后不会再使用 则应该调用本接口在进行EGLContext的资源释放
 */
/** {en}
 * @hidden(iOS,macOS,Windows,Linux) for internal use only
 * @type api
 * @region  video management
 * @brief  Used to clear the shared EGLContext, after the engine is destroyed, if it is determined that it will not be used again  then this interface should be called for resource release of EGLContext
 */
BYTERTC_API void clearHardWareEncodeContext();

/** {zh}
 * @hidden(iOS,macOS,Windows,Linux) for internal use only
 * @type api
 * @region 引擎管理
 * @brief 用于设置Android的ApplicationContext给Engine使用，
 * 如果Android使用纯C++接口，则该方法必须在引擎创建前设置
 * @param [in] j_egl_context
 *      传入Java的 android.content.Context 类型的EGLContext
 */
/** {en}
 * @hidden(iOS,macOS,Windows,Linux) for internal use only
 * @type api
 * @region Engine management
 * @brief Used to set the ApplicationContext for Android to use by Engine,
 * If Android uses a pure C++ interface, this method must be set before the engine is created
 * @param  [in] j_egl_context
 *      Passing in Java android.content. Context type EGLContext
 */
BYTERTC_API void setApplicationContext(jobject j_application_context);
#endif

/** {zh}
 * @type api
 * @region 视频管理
 * @type keytype
 * @brief 硬件加速设备类型
 */
/** {en}
 * @type api
 * @region video management
 * @type keytype
 * @brief  Hardware acceleration device type
 */
enum HWDeviceType {
    /** {zh}
     * @brief 未知的设备类型
     */
    /** {en}
     * @brief Unknown device type
     */
    kHWDeviceTypeNone,

    /** {zh}
     * @brief direct3d 11 视频加速设备
     */
    /** {en}
     * @brief Direct3d 11 Video acceleration device
     */
    kHWDeviceTypeD3D11,

    /** {zh}
     * @brief cuda 硬件加速设备
     * @notes cuda 是 nvidia 平台下硬件加速设备
     */
    /** {en}
     * @brief Cuda  hardware acceleration device
     * @notes Cuda  is a hardware acceleration device under the nvidia platform
     */
    kHWDeviceTypeCuda,

    /** {zh}
     * @brief intel 平台下 qsv 加速设备
     */
    /** {en}
     * @brief Qsv acceleration device under intel  platform
     */
    kHWDeviceTypeQsv,

    /** {zh}
     * @brief windows 平台 dx 硬件加速设备
     */
    /** {en}
     * @brief Windows  platform dx hardware acceleration device
     */
    kHWDeviceTypeDxva2,

    /** {zh}
     * @brief Android 平台下硬件加速设备 mediacodec
     */
    /** {en}
     * @brief Hardware acceleration device mediacodec under Android  platform
     */
    kHWDeviceTypeMediaCodec,

    /** {zh}
     * @brief IOS、MACOS 平台下硬件加速设备 VideoToolbox
     */
    /** {en}
     * @brief IOS, MACOS  platform hardware acceleration device VideoToolbox
     */
    kHWDeviceTypeVideoToolbox,
     /** {zh}
     * @brief android、linux 平台下硬件加速设备 egl context
     */
    /** {en}
     * @brief Android, linux  platform hardware acceleration device egl context
     */
    kHWDeviceTypeEglContext,

    /** {zh}
     * @brief linux、windows 平台下硬件加速设备 va context
     */
    /** {en}
     * @brief Linux, windows  platform hardware acceleration device va context
     */
    kHWDeviceTypeVaapi,
};

/** {zh}
 * @hidden for internal use only
 * @type keytype
 * @brief 硬编码设备 context
 */
/** {en}
 * @hidden for internal use only
 * @type keytype
 * @brief  Hardcoding device context
 */
enum HWDeviceContextKey {
    /**
     * @brief cuda context
     */
    kHWDeviceContextKeyCudaContext,
    /** {zh}
     * @brief derict3D11 设备
     */
    /** {en}
     * @brief Derict3D11  device
     */
    kHWDeviceContextKeyD3D11Device,
    /** {zh}
     * @brief derict3D11 设备 context
     */
    /** {en}
     * @brief Derict3D11  device context
     */
    kHWDeviceContextKeyD3D11DeviceContext,
    /** {zh}
     * @brief egl 设备 context
     */
    /** {en}
     * @brief Egl  device context
     */
    kHWDeviceContextKeyEglContext,
    /** {zh}
     * @brief vadisplay 设备 context
     */
    /** {en}
     * @brief Vadisplay  device context
     */
    kHWDeviceContextKeyVADisplay,
};

/** {zh}
 * @type keytype
 * @brief 硬件加速设备 context
 */
/** {en}
 * @type keytype
 * @brief Hardware acceleration device context
 */
class IHWDeviceContext {
public:
    virtual ~IHWDeviceContext() = default;
    /** {zh}
     * @brief 获取硬件加速设备 context 类型
     * @return 硬件加速设备类型，详见 HWDeviceType{@link #HWDeviceType}
     */
    /** {en}
     * @brief Get the hardware acceleration device context type
     * @return  Hardware acceleration device type. See HWDeviceType{@link #HWDeviceType}
     */
    virtual HWDeviceType deviceType() const = 0;
    /** {zh}
     * @brief 设置属性
     * @param [in] key
     *        硬件加速设备 context 类型，详见 ByteRTCHWDeviceContextKey:{@link #ByteRTCHWDeviceContextKey}
     * @param [in] value
     *        指向硬件加速设备 context 地址的指针
     */
    /** {en}
     * @brief Set property
     * @param  [in] key
     *         Hardware acceleration device context type. See ByteRTCHWDeviceContextKey:{@link #ByteRTCHWDeviceContextKey}
     * @param  [in] value
     *         Pointer to the hardware acceleration device context address
     */
    virtual void setProperty(HWDeviceContextKey key, void* value) = 0;
    /** {zh}
     * @brief 获取属性
     * @param [in] key
     *        硬件加速设备 context 类型，详见 ByteRTCHWDeviceContextKey:{@link #ByteRTCHWDeviceContextKey}
     * @return 返回硬件加速设备 context 地址的指针
     */
    /** {en}
     * @brief Get the property
     * @param  [in] key
     *         Hardware acceleration device context type. See ByteRTCHWDeviceContextKey:{@link #ByteRTCHWDeviceContextKey}
     * @return  Return a pointer to the hardware acceleration device context address
     */
    virtual void* getProperty(HWDeviceContextKey key) = 0;
    /** {zh}
     * @brief 内部 context 是否由该实例拥有
     * @return  <br>
     *        + true: 硬件设备 context 被实例对象拥有  <br>
     *        + false: 硬件设备上 context 文不被实例对象拥有  <br>
     */
    /** {en}
     * @brief Internal context is owned by the instance
     * @return   <br>
     *         + True: hardware device context is owned by the instance object <br>
     *         + False: hardware device context is not owned by the instance object <br>
     */
    virtual bool ownContext() const = 0;
    /** {zh}
     * @brief 设置 context 是否被实例对象拥有
     * @param  [in] own_context  <br>
     *       + true: context 被实例对象拥有  <br>
     *       + false: context 不被实例对象拥有  <br>
     */
    /** {en}
     * @brief Sets whether context is owned by the instance object
     * @param   [in] own_context <br>
     *        + True: context is owned by the instance object <br>
     *        + False: context is not owned by the instance object <br>
     */
    virtual void setOwnContext(bool own_context) = 0;
    /** {zh}
     * @brief 转移硬件设备 context，
     * @return 指向硬件设备 context 的指针
     */
    /** {en}
     * @brief Transfer hardware device context,
     * @return  Pointer to hardware device context
     */
    virtual IHWDeviceContext* moveContext() = 0;
    /** {zh}
     * @brief 释放实例对象
     */
    /** {en}
     * @brief Release instance object
     */
    virtual void release() = 0;
};

/**
 * @hidden for internal use only
 * @brief create a hardware device context with specified deviceType
 */
BYTERTC_API IHWDeviceContext* createHwDeviceContext(HWDeviceType device_type);

/** {zh}
 * @hidden for internal use only
 * @brief 设置视频源的设备上下文信息
 * @param [in] engine
 *       要设置的引擎，详见 IRTCVideo{@link #IRTCVideo}
 * @param [in] hw_context
 *        设置视频帧，详见：IHWDeviceContext{@link #IHWDeviceContext}
 * @notes 用于硬件编码传入 GPU 内存时使用
 */
/** {en}
 * @hidden for internal use only
 * @brief  Set the device context information of the video source
 * @param  [in] engine
 *        The engine to be set, see: IRtcEngine{@link #IRTCVideo}
 * @param  [in] hw_context
 *        Set the video frame, see: IHWDeviceContext{@link #IHWDeviceContext}
 * @notes Used when hardware encoding is passed in GPU memory
 */
BYTERTC_API void setVideoSourceHWDeviceContext(void* engine, IHWDeviceContext* hw_context);

/** {zh}
 * @hidden for internal use only
 * @type api
 * @region 视频管理
 * @brief 发送外部源视频数据
 * @param [in] engine
 *       要设置的引擎，详见 IRTCVideo{@link #IRTCVideo}
 * @param [in] frame
 *        输入视频帧，详见 IVideoFrame{@link #IVideoFrame}
 * @notes
 *      1.支持 YUV420P，NV12，D3D texture，Cuda 内存，OpenGL texture等格式的视频帧。
 *      2.该函数运行在用户调用线程内
 */
/** {en}
 * @hidden for internal use only
 * @type api
 * @region  video management
 * @brief  Send external source video data
 * @param  [in] engine
 *        The engine to be set up. See IRtcEngine{@link #IRTCVideo}
 * @param  [in] frame
 *         Input video frame. See IVideoFrame{@link #IVideoFrame}
 * @notes
 *      1. Support YUV420P, NV12, D3D texture, Cuda memory, OpenGL texture and other formats of video frames.
 *      2. This function runs in the user calling thread
 */
BYTERTC_API bool pushExternalVideoFrame(void* engine, const IVideoFrame* frame);


/** {zh}
 * @hidden for internal use only
 * @type keytype
 * @brief 音频帧信息
 */
/** {en}
 * @hidden for internal use only
 * @type keytype
 * @brief  Audio frame information
 */
class IEncodedAudioFrame {
public:
    virtual ~IEncodedAudioFrame() {
    }
    virtual AudioCodecType codecType() const = 0;
    virtual void setCodecType(AudioCodecType codec_type) = 0;
    virtual int sampleRate() const = 0;
    virtual void setSampleRate(int sample_rate) = 0;
    virtual int channelsNum() const = 0;
    virtual void setChannelsNum(int channels_num) = 0;
    virtual int64_t timestampUs() const = 0;
    virtual void setTimestampUs(int64_t timestamp_us) = 0;
    virtual int64_t timestampPts() const = 0;
    virtual void setTimestampPts(int64_t timestamp_pts) = 0;
    virtual int timebaseNum() const = 0;
    virtual void setTimestampNum(int timebase_num) = 0;
    virtual int timebaseDen() const = 0;
    virtual void setTimestampDen(int timebase_den) = 0;
    virtual void setStreamMemory(const ManagedMemory& memory) = 0;
    virtual uint8_t* data() const = 0;
    virtual int dataSize() const = 0;
    virtual int frameLength() const = 0;
};

/**
 * @hidden for internal use only
 */
BYTERTC_API IEncodedAudioFrame* createEncodedAudioFrame();

/** {zh}
 * @hidden for internal use only
 * @type callback
 * @region 音频数据回调
 * @brief 本地音频帧监测器
 */
/** {en}
 * @hidden for internal use only
 * @type callback
 * @region audio data callback
 * @brief Local audio frame monitor
 */
class ILocalEncodedAudioFrameObserver  {
public:
    virtual ~ILocalEncodedAudioFrameObserver() {
    }
    /** {zh}
     * @type callback
     * @region 音频数据回调
     * @brief 调用 RegisterLocalEncodedAudioFrameObserver{@link #RegisterLocalEncodedAudioFrameObserver} 后，SDK 收到本地音频帧信息时，回调该事件
     * @param [in] type 本地音频帧类型，参看 StreamIndex{@link #StreamIndex}
     * @param [in] audio_stream 本地音频帧信息，参看 IEncodedAudioFrame{@link #IEncodedAudioFrame}
     */
    /** {en}
     * @type callback
     * @region Audio data callback
     * @brief Call RegisterLocalEncodedAudioFrameObserver{@link #RegisterLocalEncodedAudioFrameObserver}, when the SDK receives local audio frame information, callback the event
     * @param  [in] type Local audio frame type. See StreamIndex{@link #StreamIndex}
     * @param  [in] audio_stream Local audio frame information. See IEncodedAudioFrame{@link #IEncodedAudioFrame}
     */
    virtual void onLocalEncodedAudioFrame(StreamIndex type, const IEncodedAudioFrame& audio_stream) = 0;
};

/** {zh}
 * @hidden for internal use only
 * @type callback
 * @region 音频数据回调
 * @brief 远端音频帧监测器
 */
/** {en}
 * @hidden for internal use only
 * @type callback
 * @region audio data callback
 * @brief Remote audio frame monitor
 */
class IRemoteEncodedAudioFrameObserver  {
public:
    virtual ~IRemoteEncodedAudioFrameObserver () {
    }
    /** {zh}
     * @type callback
     * @region 音频数据回调
     * @brief 调用 RegisterRemoteEncodedAudioFrameObserver{@link #RegisterRemoteEncodedAudioFrameObserver} 后，SDK 收到远端音频帧信息时，回调该事件
     * @param [in] stream_id 收到的远端音频流的 ID
     * @param [in] audio_stream 远端音频帧信息，参看 IEncodedAudioFrame{@link #IEncodedAudioFrame}
     * @param [in] stream_info 收到的远端音频流的信息，参看 RemoteStreamKey{@link #RemoteStreamKey}
     */
    /** {en}
     * @type callback
     * @region Audio data callback
     * @brief Call RegisterRemoteEncodedAudioFrameObserver{@link #RegisterRemoteEncodedAudioFrameObserver}, when the SDK receives the remote audio frame information, callback the event
     * @param  [in] stream_id The ID of the received remote audio stream
     * @param  [in] audio_stream The remote audio frame information. See IEncodedAudioFrame{@link #IEncodedAudioFrame}
     * @param  [in] stream_info Information about the received remote audio stream. See RemoteStreamKey{@link #RemoteStreamKey}
     */
    virtual void onRemoteEncodedAudioFrame(
            const char* stream_id, const IEncodedAudioFrame& audio_stream, const RemoteStreamKey& stream_info) = 0;
};


/** {zh}
 * @hidden for internal use only
 * @type api
 * @region 音频数据回调
 * @brief 注册远端音频帧监测器。  <br>
 *        调用该方法后，SDK 每监测到一帧远端音频帧时，都会将音频帧信息通过 OnRemoteEncodedAudioFrame{@link #OnRemoteEncodedAudioFrame} 回调给用户
 * @param [in] engine 需设置的引擎，参看 IRtcEngine{@link #IRTCVideo}
 * @param [in] observer 远端音频帧监测器，参看 IRemoteEncodedAudioFrameObserver{@link #IRemoteEncodedAudioFrameObserver}
 * @notes  <br>
 *       + 该方法建议在进房前调用。 <br>
 *       + 将参数设置为 nullptr 则取消注册。
 */
/** {en}
 * @hidden for internal use only
 * @type api
 * @region Audio data callback
 * @brief Register the remote audio frame monitor.   <br>
 *         After calling this method, every time the SDK detects a remote audio frame, it will call back the audio frame information to the user through OnRemoteEncodedAudioFrame{@link #OnRemoteEncodedAudioFrame}
 * @param  [in] engine The engine to be set up. See IRtcEngine{@link #IRTCVideo}
 * @param  [in] observer Remote AudioFrame Monitor. See IRemoteEncodedAudioFrameObserver{@link #IRemoteEncodedAudioFrameObserver}
 * @notes   <br>
 *        + This method is recommended to be called before entering the room. <br>
 *        + Setting the parameter to nullptr cancels registration.
 */
BYTERTC_API void registerRemoteEncodedAudioFrameObserver(void* engine, IRemoteEncodedAudioFrameObserver* observer);

/** {zh}
 * @hidden for internal use only
 * @type api
 * @region 音频数据回调
 * @brief 注册本地音频帧监测器。  <br>
 *        调用该方法后，SDK 每监测到一帧本地音频帧时，都会将音频帧信息通过 OnLocalEncodedAudioFrame{@link #OnLocalEncodedAudioFrame} 回调给用户
 * @param [in] engine 需设置的引擎，参看 IRtcEngine{@link #IRTCVideo}
 * @param [in] observer 本地音频帧监测器，参看 ILocalEncodedAudioFrameObserver{@link #ILocalEncodedAudioFrameObserver}
 * @notes  <br>
 *       + 该方法建议在进房前调用。 <br>
 *       + 将参数设置为 nullptr 则取消注册。
 */
/** {en}
 * @hidden for internal use only
 * @type api
 * @region Audio data callback
 * @brief Register a local audio frame monitor.   <br>
 *         After calling this method, every time the SDK detects a local audio frame, it will call back the audio frame information to the user through OnLocalEncodedAudioFrame{@link #OnLocalEncodedAudioFrame}
 * @param  [in] engine The engine to be set up. See IRtcEngine{@link #IRTCVideo}
 * @param  [in] observer Local AudioFrame Monitor. See ILocalEncodedAudioFrameObserver{@link #ILocalEncodedAudioFrameObserver}
 * @notes   <br>
 *        + This method is recommended to be called before entering the room. <br>
 *        + Setting the parameter to nullptr cancels registration.
 */
BYTERTC_API void registerLocalEncodedAudioFrameObserver(void* engine, ILocalEncodedAudioFrameObserver* observer);


/**
 * @hidden for internal use only
 */
BYTERTC_API bool pushExternalEncodedAudioFrame(void* engine, const IEncodedAudioFrame* audio_stream);

/**
 * @hidden for internal use only
 * @type api
 */
struct MediaIoOption {
    bool enable_audio_encoding = true;
    bool enable_video_encoding = true;
    bool enable_audio_decoding = true;
    bool enable_video_decoding = true;
};

/**
 * @hidden for internal use only
 * @type api
 */
BYTERTC_API void setupEngineMediaIo(void* engine, const MediaIoOption& option);

/** {zh}
 * @hidden for internal use only
 * @type keytype
 * @region 视频数据回调
 * @brief metadata 数据大小最大值
 */
/** {en}
 * @hidden for internal use only
 * @type keytype
 * @region  video data callback
 * @brief Metadata  maximum data size
 */
const int MAX_METADATA_LENGTH = 1024;


/** {zh}
 * @hidden for internal use only
 * @type callback
 * @brief 音频设备事件回调
 */
/** {en}
 * @hidden for internal use only
 * @type callback
 * @brief  Audio device event callback
 */
class IAudioDeviceEventHandler {
public:
    /** {zh}
     * @type callback
     * @brief 获得麦克风音量
     * @param [in] volume
     *       音量大小
     */
    /** {en}
     * @type callback
     * @brief  Get microphone volume
     * @param  [in] volume
     *        Volume size
     */
    virtual void onRecordingAudioVolumeIndication(int volume) = 0;

    /** {zh}
     * @type callback
     * @brief 获得Loopback音量
     * @param [in] volume
     *       音量大小
     */
    /** {en}
     * @type callback
     * @brief  Get Loopback volume
     * @param  [in] volume
     *        Volume size
     */
    virtual void onLoopbackAudioVolumeIndication(int volume) = 0;
};

/**
 * @hidden for internal use only
 * @type callback
 */
class IAudioDeviceManagerEx : public IAudioDeviceManager {
public:
    /** {zh}
     * @region 音频设备管理
     * @brief 构造函数
     */
    /** {en}
     * @region Audio Facility Management
     * @brief Constructor
     */
    IAudioDeviceManagerEx() = default;

    /** {zh}
     * @type api
     * @region 音频设备管理
     * @brief 析构当前对象，释放内存
     * @notes 该结构不需要的时候应该调用本函数释放音频操作相关的资源
     */
    /** {en}
     * @type api
     * @region Audio Facility Management
     * @brief Destruct the current object and free memory
     * @notes This function should be called when the structure is not needed to free resources related to audio operations
     */
    virtual void release() = 0;

    /** {zh}
     * @type api
     * @region 音频设备管理
     * @brief 切换音频播放到扬声器或者听筒，默认播放设备是扬声器
     * @param [in] enable  <br>
     *       + true：切换至扬声器  <br>
     *       + false：切换至听筒  <br>
     * @notes 本方法只在移动设备上有效
     */
    /** {en}
     * @type api
     * @region Audio Facility Management
     * @brief Switch audio to the speaker or earpiece, the default playback device is the speaker
     * @param  [in] enable <br>
     *        + True: switch to the speaker <br>
     *        + False: switch to the earpiece <br>
     * @notes This method is only valid on mobile devices
     */
    virtual void setEnableSpeakerphone(bool enable) = 0;

    /** {zh}
     * @type api
     * @region 音频设备管理
     * @brief 启动音频采集设备测试。  <br>
     *        该方法测试音频采集设备是否能正常工作。启动测试后，会收到 `onLocalAudioPropertiesReport` 回调上报的音量信息。
     * @param [in] indication_interval `onLocalAudioPropertiesReport` 回调的时间间隔，单位为毫秒。建议设置到大于 200 毫秒。最小不得少于 10 毫秒。小于10 毫秒行为未定义。
     * @return  方法调用结果  <br>
     *        + 0：方法调用成功  <br>
     *        + < 0：方法调用失败  <br>
     * @notes  <br>
     *       + 该方法必须在进房前调用，且不可与其它音频设备测试功能同时应用。  <br>
     *       + 你需调用 stopAudioCaptureDeviceTest{@link #IAudioDeviceManager#stopAudioCaptureDeviceTest} 停止测试。  <br>
     */
    /** {en}
     * @type api
     * @region Audio Facility Management
     * @brief Start the audio capture device test.   <br>
     *        This method tests whether the audio acquisition device can work properly. After starting the test, you will receive the volume information reported by the `onLocalAudioPropertiesReport` callback.
     * @param  [in] indication_interval The interval(ms) in `onLocalAudioPropertiesReport` callback. It is recommended to set to greater than 200 milliseconds. The minimum shall not be less than 10 milliseconds. Less than 10 milliseconds behavior is not defined.
     * @return  Method call result   <br>
     *         + 0: Success. <br>
     *         + < 0: failure <br>
     * @notes   <br>
     *        + This method must be called before joining the room and cannot be applied at the same time as other audio device testing functions. <br>
     *        + You need to call stopAudioCaptureDeviceTest{@link #IAudioDeviceManager#stopAudioCaptureDeviceTest} to stop the test. <br>
     */
    virtual int startAudioCaptureDeviceTest(int indication_interval) = 0;

    /** {zh}
     * @type api
     * @region 音频设备管理
     * @brief 停止音频采集设备测试。
     * @return  方法调用结果  <br>
     *        + 0：方法调用成功  <br>
     *        + < 0：方法调用失败  <br>
     * @notes  调用 startAudioCaptureDeviceTest{@link #IAudioDeviceManager#startAudioCaptureDeviceTest} 后，需调用本方法停止测试。
     */
    /** {en}
     * @type api
     * @region Audio Facility Management
     * @brief Stop audio capture device testing.
     * @return  Method call result   <br>
     *         + 0: Success. <br>
     *         + < 0: failure <br>
     * @notes  After calling startAudioCaptureDeviceTest{@link #IAudioDeviceManager#startAudioCaptureDeviceTest}, you need to call this method to stop the test.
     */
    virtual int stopAudioCaptureDeviceTest() = 0;

    /** {zh}
     * @type api
     * @region 音频设备管理
     * @brief 开始音频设备回路测试。  <br>
     *        该方法测试音频采集设备和音频播放设备是否能正常工作。一旦测试开始，音频采集设备会采集本地声音
     *        并通过音频播放设备播放出来，同时用户 App 会收到 `onLocalAudioPropertiesReport`
     *        回调上报的音量信息。
     * @param [in] indication_interval `onLocalAudioPropertiesReport` 回调的时间间隔，单位为毫秒。建议设置到大于 200 毫秒。最小不得少于 10 毫秒。小于 10 毫秒行为未定义。
     * @return  方法调用结果  <br>
     *        + 0：方法调用成功  <br>
     *        + < 0：方法调用失败  <br>
     * @notes  <br>
     *       + 该方法必须在进房前调用。且不可与其它音频设备测试功能同时应用。  <br>
     *       + 你需调用 stopAudioDeviceLoopbackTest{@link #IAudioDeviceManager#stopAudioDeviceLoopbackTest} 停止测试。  <br>
     *       + 该方法仅在本地进行音频设备测试，不涉及网络连接。  <br>
     */
    /** {en}
     * @type api
     * @region Audio Facility Management
     * @brief Begins audio device loop testing.   <br>
     *        This method tests whether the audio acquisition device and the audio playback device can work normally. Once the test starts, the audio capture device will capture the local sound
     *         And play it out through the audio playback device, and the user App will receive the volume information reported by the `onLocalAudioPropertiesReport` callback.
     * @param  [in] indication_interval The time interval(ms) in `onLocalAudioPropertiesReport`. It is recommended to set to greater than 200 milliseconds. The minimum shall not be less than 10 milliseconds. Less than 10 milliseconds behavior is not defined.
     * @return   Method call result   <br>
     *         + 0: Success. <br>
     *         + < 0: failure <br>
     * @notes   <br>
     *        + This method must be called before joining the room. And cannot be applied at the same time as other audio equipment test functions. <br>
     *        + You need to call stopAudioDeviceLoopbackTest{@link #IAudioDeviceManager#stopAudioDeviceLoopbackTest} to stop the test. <br>
     *        + This method only tests audio equipment locally and does not involve network connection. <br>
     */
    virtual int startAudioDeviceLoopbackTest(int indication_interval) = 0;

    /** {zh}
     * @type api
     * @region 音频设备管理
     * @brief 停止音频设备回路测试。
     * @return  方法调用结果  <br>
     *        + 0：方法调用成功  <br>
     *        + < 0：方法调用失败  <br>
     * @notes 调用 startAudioDeviceLoopbackTest{@link #IAudioDeviceManager#startAudioDeviceLoopbackTest} 后，需调用本方法停止测试。
     */
    /** {en}
     * @type api
     * @region Audio Facility Management
     * @brief Stop audio device loop testing.
     * @return  Method call result   <br>
     *         + 0: Success. <br>
     *         + < 0: failure <br>
     * @notes After calling startAudioDeviceLoopbackTest{@link #IAudioDeviceManager#startAudioDeviceLoopbackTest}, you need to call this method to stop the test.
     */
    virtual int stopAudioDeviceLoopbackTest() = 0;

protected:
    /** {zh}
     * @hidden constructor/destructor
     * @brief 析构函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Destructor
     */
    virtual ~IAudioDeviceManagerEx() = default;
};

/** {zh}
 * @deprecated since 3.51 and will be deleted in 3.53, use getAudioDeviceManager{@link #IRTCVideo#getAudioDeviceManager} instead
 * @hidden for internal use only
 * @type api
 * @brief 音频设备管理接口创建，该接口不依赖引擎，主要用于无引擎下的音频设备管理
 * @param [in] handler
 *       音频设备的事件回调
 * @return 音频设备管理接口
 */
/** {en}
 * @deprecated since 3.51 and will be deleted in 3.53, use getAudioDeviceManager{@link #IRTCVideo#getAudioDeviceManager} instead
 * @hidden for internal use only
 * @type api
 * @brief Audio Facility Management interface is created, this interface does not depend on the engine, and is mainly used for audio Facility Management without an engine
 * @param  [in] handler
 *       Audio device event callback
 * @return Audio Facility Management interface
 */
BYTERTC_API IAudioDeviceManagerEx* createAudioDeviceManager(IAudioDeviceEventHandler* handler);

}  // namespace bytertc

