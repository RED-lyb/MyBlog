//
//  bytertc_publicstream_interface.h
//  VolcEngineRTC

#pragma once

#include "bytertc_defines.h"
#include "bytertc_transcoder_base_interface.h"

#define PUBLICSTREAM_OK 0
#define PUBLICSTREAM_BASE 1190
#define PUBLICSTREAM_INVALID_PARAM 1191
#define PUBLICSTREAM_INVALID_STATE 1192
#define PUBLICSTREAM_INTERNAL_ERROR 1193
#define PUBLICSTREAM_PUSH_FAILED 1195
#define PUBLICSTREAM_TIMEOUT 1196

namespace bytertc {
/** {zh}
 * @type keytype
 * @brief 公共流的布局模式
 */
/** {en}
 * @type keytype
 * @brief Layout mode of the public stream
 */
enum StreamLayoutMode {
    /** {zh}
     * @brief 自动布局
     */
    /** {en}
     * @brief auto mode
     */
    kStreamLayoutModeAuto = 0,
    /** {zh}
     * @brief 自定义
     */
    /** {en}
     * @brief Customer mode
     */ 
    kStreamLayoutModeCustom = 2
};

/** {zh}
 * @type keytype
 * @brief 公共流视频裁剪配置
 */
/** {en}
 * @type keytype
 * @brief Configurations on how to crop the public stream
 */
typedef struct SourceCrop {
    /** {zh}
     * @brief 裁剪后得到的视频帧左上角横坐标相对于裁剪前整体画面的归一化比例，取值范围[0.0, 1.0)
     */
    /** {en}
     * @brief The normalized horizontal coordinate value of the top left vertex of the cropped image to width of the original image, ranging within [0.0, 1.0).
     */     
    float location_x = 0.0;
    /** {zh}
     * @brief 裁剪后得到的视频帧左上角纵坐标相对于裁剪前整体画面的归一化比例，取值范围[0.0, 1.0)
     */
    /** {en}
     * @brief The normalized vertical coordinate value of the top left vertex of the cropped image to height of the original image, ranging within [0.0, 1.0).
     */
    float location_y = 0.0;
    /** {zh}
     * @brief 裁剪后得到的视频帧宽度相对于裁剪前整体画面的归一化比例，取值范围(0.0, 1.0]
     */
    /** {en}
     * @brief The normalized ratio of the width of the cropped image to that of the original image, ranging within [0.0, 1.0).
     */
    float width_proportion = 0.0;
    /** {zh}
     * @brief 裁剪后得到的视频帧高度相对于裁剪前整体画面的归一化比例，取值范围(0.0, 1.0]
     */
    /** {en}
     * @brief The normalized ratio of the height of the cropped image to that of the original image, ranging within [0.0, 1.0).
     */
    float height_proportion = 0.0;
} SourceCrop;
/** {zh}
 * @type keytype
 * @brief 公共流视频编码参数
 */
/** {en}
 * @type keytype
 * @brief Encoding properties of the public video stream
 */
typedef struct PublicStreamVideoParam {
    /** {zh}
     * @brief 公共流视频宽度，必填。单位为 px，范围为 [2, 1920]，必须是偶数。
     */
    /** {en}
     * @brief Required. Width of the video frame. Unit: px. Ranging: [16, 1920], even value is effective.
     */
    int32_t width;
    /** {zh}
     * @brief 公共流视频高度，必填。单位为 px，范围为 [16, 1280]，必须是偶数。
     */
    /** {en}
     * @brief Required. Width of the video frame. Unit: px. Ranging: [16, 1280], even value is effective.
     */
    int32_t height;
    /** {zh}
     * @brief 公共流视频帧率。必填<br>
     *        范围：[1, 60]
     */
    /** {en}
     * @brief Required. Frame rate in fps<br>
     *        Range: [1, 60]
     */
    int32_t fps;
    /** {zh}
     * @brief 视频码率，必填<br>
     *        范围：[1,10000000]<br>
     *        单位为 bps
     */
    /** {en}
     * @brief Required. Bitrate in bps <br>
     *        Range: [1,10000000]<br>
     */
    int32_t bitrate_kpbs;
} PublicStreamVideoParam;
/** {zh}
 * @hidden currently not available
 * @type keytype
 * @brief 公共流音频编码参数
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief Properties of the public audio stream
 */
typedef struct PublicStreamAudioParam {
    /** {zh}
     * @brief 音频采样率，必填。单位为 Hz。可选取值：16000, 32000, 44100 和 48000
     */
    /** {en}
     * @brief Required. Audio sample rate in Hz. Options: 16000, 32000, 44100, or 48000
     */
    int32_t sample_rate;
    /** {zh}
     * @brief 音频声道数，必填。
     * + 1: 单声道<br>
     * + 2: 双声道
     */
    /** {en}
     * @brief Required. Number of the audio channels.
     * + 1: Mono<br>
     * + 2: Dual
     */
    int32_t channel_num;
    /** {zh}
     * @brief 音频码率，必填。单位为 kbps。<br>
     * 正整数，可选取值：16, 32, 64。
     */
    /** {en}
     * @brief Required. Audio bitrate in kbps. <br>
     * Positive integer in kbps. Options: 16, 32, or 64
     */
    int32_t bitrate_kbps;
} PublicStreamAudioParam;
/** {zh}
 * @type keytype
 * @brief 单个视频流在公共流中的布局信息。  <br>
 *        在多路视频流公共流时，你需要设置每一路视频流在公共流中的布局信息。
 */
/** {en}
 * @type keytype
 * @brief Layout of each stream to be mixed into the public stream <br>
 *        You can configure each of the video streams for the public stream.
 */
typedef struct PublicStreamLayoutRegion {
    /** {zh}
     * @brief 目标公共流用户的 ID, 不能为空
     */
    /** {en}
     * @brief ID of the public stream，must not be empty
     */
    const char* user_id = "";
    /** {zh}
     * @brief 跨房间订阅流时，目标流所在的房间 ID, 不能为空
     */
    /** {en}
     * @brief ID of the room from which the stream is intended to be sent as a public stream，
     * must not be empty
     */
    const char* room_id = "";
    /** {zh}
     * @brief 背景图片地址
     */
    /** {en}
     * @brief Uniform resource identifier(URI) of the background image
     */
    const char* alternate_image_uri = "";
    /** {zh}
     * @brief 用户视频布局相对画布左侧的偏移量，取值的范围为 [0.0, 1.0)。必填。
     */
    /** {en}
     * @brief Required. Left offset of the video against the local client' view, ranging [0.0, 1.0)
     */
    float x;
    /** {zh}
     * @brief 用户视频布局相对画布顶端的偏移量，取值的范围为 [0.0, 1.0)。必填。
     */
    /** {en} 
     * @brief Required. Top offset of the video against the local client' view, ranging [0.0, 1.0)
     */
    float y;
    /** {zh}
     * @brief 用户视频宽度相对画布宽度的比例，取值的范围为 (0.0, 1.0]。必填。
     */
    /** {en}
     * @brief Required. Ratio of the width of the video to that of the client's view, ranging [0.0, 1.0)
     */
    float width;
    /** {zh}
     * @brief 用户视频高度相对画布高度的比例，取值的范围为 (0.0, 1.0]。必填。
     */
    /** {en}
     * @brief Required. Ratio of the height of the video to that of the client's view, ranging [0.0, 1.0)
     */
    float height;
    /** {zh}
     * @brief 透明度，取值范围 [0，255], 0 为全透明，255 为不透明
     */
    /** {en}
     * @brief Transparency, ranging [0，255], 0 for transparent. 255 for solid.
     */
    float alpha;
    /** {zh}
     * @brief 用户视频布局在画布中的层级，取值范围 [0，100]，0(默认）为底层，100 为顶层。
     */
    /** {en}
     * @brief Stack's layer order (also known as the z-order) of videos in the public stream. <br>
     *        Ranging [0, 100]. 0 for the bottom, by default. 100 for the top.
     */
    int32_t z_order;
    /** {zh}
     * @brief 必填。媒体流类型：  <br>
     *        + 0: 普通流（默认设置）  <br>
     *        + 1: 屏幕流
     */
    /** {en}
     * @brief Required. Stream index:<br>
     *        + 0: Main stream which is video or audio stream captured by media device or externally sourced media stream.
     *        + 1: Screen-sharing stream
     */
    int stream_type = 0;
    /** {zh}
     * @brief 公共流输出类型，参看 TranscoderContentControlType{@link #TranscoderContentControlType}
     */
    /** {en}
     * @brief Media type of the public stream. Refer to TranscoderContentControlType{@link #TranscoderContentControlType} for more details.
     */
    TranscoderContentControlType media_type;
    /** {zh}
     * @brief 渲染时，视频内容缩放模式，必填。参看 RenderMode{@link #RenderMode}
     */
    /** {en}
     * @brief Required. The fit mode when rendering. Refer to RenderMode{@link #RenderMode} for more details.
     */
    RenderMode render_mode;
    /** {zh}
     * @brief 支持对每一路参与公共流的视频进行裁剪，参看 SourceCrop{@link #SourceCrop}
     */
    /** {en}
     * @brief Configurations on how to crop the public stream. Refer to SourceCrop{@link #SourceCrop} for more details.
     */
    SourceCrop source_crop;
} PublicStreamLayoutRegion;
/** {zh}
 * @type keytype
 * @brief 公共流布局设置。
 */
/** {en}
 * @type keytype
 * @brief Layout configuration of the public stream
 */
struct PublicStreamLayout {
    /** {zh}
     * @brief 布局模式。必填。<br>
     *        + `0`: 自动模式。默认值。 <br>
     *        + `2`: 自定义模式。
     */
    /** {en}
     * @brief Required. Layout mode of the public stream <br>
     *        + `0`: Auto layout. The default value. <br>
     *        + `2`: Custom mode.
     */
    int layout_mode;
    /** {zh}
     * @brief 插帧模式<br>
     *         + `0`: 补最后一帧<br>
     *         + `1`: 补背景图片，如果没有设置背景图片则补黑帧
     */
    /** {en}
     * @brief Interpolation mode<br>
     *         + `0`: Insert with the last frame<br>
     *         + `1`: Insert with the background image. RTC will insert frames of black if no background image has been set.
     */
    int interpolation_mode;
    /** {zh}
     * @brief 背景图片
     */
    /** {en}
     * @brief Background image
     */
    const char* background_image = nullptr;
    /** {zh}
     * @brief 公共流视频的背景颜色，格式为 RGB 定义下的 Hex 值，如 #FFB6C1 表示浅粉色。默认值 #000000，表示为黑色
     */
    /** {en}
     * @brief Background color of the canvas,in RGB hex value. For example, #FFB6C1 represents light pink. The default value is #000000 (black).
     */
    const char* background_color = nullptr;
    /** {zh}
     * @brief 各路流的布局信息列表。每一个该类型对象为一路单独的视频流的布局信息。详见 PublicStreamLayoutRegion{@link #PublicStreamLayoutRegion}
     */
    /** {en}
     * @brief Layouts of each stream to be mixed into the public stream.  Refer PublicStreamLayoutRegion{@link #PublicStreamLayoutRegion} to more details.
     */
    PublicStreamLayoutRegion* regions = nullptr;
    /** {zh}
     * @brief 参与合流的数量
     */
    /** {en}
     * @brief Number of the streams to be mixed in the public stream
     */
    int regions_num = 0;
};
/** {zh}
 * @hidden currently not available
 * @type keytype
 * @brief 公共流配置信息
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief Configurations of the public stream
 */
struct PublicStreamConfig {
    /** {zh}
     * @brief 公共流 ID
     */
    /** {en}
     * @brief ID of the public stream
     */
    const char* stream_id = nullptr;
    /** {zh}
     * @brief 公共流视频编码参数配置，必填。详见 PublicStreamVideoParam{@link #PublicStreamVideoParam}
     */
    /** {en}
     * @brief Required. Encdoing properties of the public video stream. Refer to PublicStreamVideoParam{@link #PublicStreamVideoParam} for more details.
     */
    PublicStreamVideoParam video_config;
    /** {zh}
     * @hidden currently not available
     * @brief 公共流音频编码参数配置，必填。详见 PublicStreamAudioParam{@link #PublicStreamAudioParam}
     */
    /** {en}
     * @hidden currently not available
     * @brief Required. Encdoing properties of the public audio stream. Refer to PublicStreamAudioParam{@link #PublicStreamAudioParam} for more details.
     */
    PublicStreamAudioParam audio_config;
    /** {zh}
     * @brief 公共流流布局设置，必填。详见 PublicStreamLayout{@link #PublicStreamLayout}
     */
    /** {en}
     * @brief Required. Layout configuration of the public stream. Refer to PublicStreamLayout{@link #PublicStreamLayout} for more details.
     */

    PublicStreamLayout layout;
};
/** {zh}
 * @type keytype
 * @brief 公共流参数
 *        本类型继承了 ITranscoderParamBase{@link #ITranscoderParamBase} 中的所有接口。
 */
/** {en}
 * @type keytype
 * @brief Properties of the public stream
 *        This keytype inherit all interfaces from ITranscoderParamBase{@link #ITranscoderParamBase}.
 */
class IPublicStreamParam : public ITranscoderParamBase {
public:
    /** {zh}
     * @type api
     * @brief 获取公共流的布局模式，多路媒体流将按照指定的布局模式，合成为一路公共流。
     * @return 公共流的布局模式，参看 StreamLayoutMode{@link #StreamLayoutMode}
     */
    /** {en}
     * @type api
     * @brief Get the layout mode of the public stream.
     * @return Layout mode of the public stream. Refer to StreamLayoutMode{@link #StreamLayoutMode} for more details.
     */
    virtual StreamLayoutMode layoutMode() = 0;
    /** {zh}
     * @type api
     * @brief 获取补帧模式
     * @return 补帧模式<br>
     *         + `0`: 补最后一帧<br>
     *         + `1`: 补背景图片，如果没有设置背景图片则补黑帧
     */
    /** {en}
     * @type api
     * @brief Get the interpolation mode of the public stream.
     * @return Enable video frame interpolation.<br>
     *         + `0`: Insert with the last frame<br>
     *         + `1`: Insert with the background image. RTC will insert frames of black if no background image has been set.
     */
    virtual int interpolationMode() = 0;
    /** {zh}
     * @type api
     * @brief 获取背景图片链接
     * @return 背景图片链接
     */
    /** {en}
     * @type api
     * @brief Get the uniform resource identifier(URI) of the background image
     * @return The URI of the background image
     */
    virtual const char* backgroundImageUri() = 0;
    /** {zh}
     * @hidden currently not available
     * @type api
     * @brief 获取公共流音频编码参数
     * @return 公共流音频编码参数内容，参看 PublicStreamAudioParam{@link #PublicStreamAudioParam}
     */
    /** {en}
     * @hidden currently not available
     * @type api
     * @brief Get the properties of the public audio stream
     * @return Properties of the public audio stream. Refer to PublicStreamAudioParam{@link #PublicStreamAudioParam} for more details.
     */
    virtual PublicStreamAudioParam audioParam() = 0;
    /** {zh}
     * @type api
     * @brief 获取公共流视频编码参数
     * @return 公共流视频参数内容，参看 PublicStreamVideoParam{@link #PublicStreamVideoParam}
     */
    /** {en}
     * @type api
     * @brief Get the properties of the public video stream
     * @return Properties of the public video stream. Refer to PublicStreamVideoParam{@link #PublicStreamVideoParam} for more details.
     */
    virtual PublicStreamVideoParam videoParam() = 0;
    /** {zh}
     * @type api
     * @brief 获取公共流视窗布局信息
     * @param [in] index 视窗对应下标
     * @return 公共流视窗布局信息，参看 PublicStreamLayoutRegion{@link #PublicStreamLayoutRegion}
     */
    /** {en}
     * @type api
     * @brief Get the layout configurations of the video stream to be added
     * @param [in] index Stream index
     * @return Layout of the region in the public stream. Refer to PublicStreamLayoutRegion{@link #PublicStreamLayoutRegion} for more details.
     */
    virtual PublicStreamLayoutRegion layoutRegionByIndex(int32_t index) = 0;
    /** {zh}
     * @type api
     * @brief 设置补帧模式
     * @param [in] mode 补帧模式<br>
     *         + `0`: 补最后一帧<br>
     *         + `1`: 补背景图片，如果没有设置背景图片则补黑帧
     */
    /** {en}
     * @type api
     * @brief Set the interpolation mode
     * @param [in] mode  Interpolation mode<br>
     *         + `0`: Insert with the last frame<br>
     *         + `1`: Insert with the background image. RTC will insert frames of black if no background image has been set.
     */
    virtual void setInterpolationMode(int mode) = 0;
    /** {zh}
     * @type api
     * @brief 设置背景图片的地址
     * @param [in] uri 公共流的背景图片的地址
     */
    /** {en}
     * @type api
     * @brief Set the uniform resource identifier(URI) of the background image
     * @param [in] uri URI of the background image 
     */
    virtual void setBackgroundImageUri(const char* uri) = 0;
    /** {zh}
     * @hidden currently not available
     * @type api
     * @brief 设置音频编码参数
     * @param [in] audio_param 音频参数，参看 PublicStreamAudioParam{@link #PublicStreamAudioParam}
     */
    /** {en}
     * @hidden currently not available
     * @type api
     * @brief Set audio encoding properties of the public stream
     * @param [in] audio_param Audio properties of the public stream. Refer to PublicStreamAudioParam{@link #PublicStreamAudioParam} for more details.
     */
    virtual void setAudioParam(const PublicStreamAudioParam& audio_param) = 0;
    /** {zh}
     * @type api
     * @brief 设置视频编码参数
     * @param [in] video_param 视频编码参数，参看 PublicStreamVideoParam{@link #PublicStreamVideoParam}
     */
    /** {en}
     * @type api
     * @brief Set video encoding properties of the public stream
     * @param [in] video_param Video encoding properties of the public stream. Refer to PublicStreamVideoParam{@link #PublicStreamVideoParam} for more details.
     */
    virtual void setVideoParam(const PublicStreamVideoParam& video_param) = 0;
    /** {zh}
     * @type api
     * @brief 设置公共流布局参数
     * @param [in] regions[] 必填。公共流布局参数，参看 PublicStreamLayoutRegion{@link #PublicStreamLayoutRegion}
     * @param [in] regions_size 必填。公共流视窗数量
     * @param [in] bg_color 公共流背景颜色。格式为 RGB 定义下的 Hex 值，如 #FFB6C1 表示浅粉色。默认值 #000000，表示为黑色
     * @param [in] mode 必填。布局参数，参看 StreamLayoutMode{@link #StreamLayoutMode}
     */
    /** {en}
     * @type api
     * @brief Set the layout of the public stream
     * @param [in] regions[] Required. A array including layout configurations of each video stream. Refer to PublicStreamLayoutRegion{@link #PublicStreamLayoutRegion} for more details.
     * @param [in] regions_size Required. Number of the streams included in the public stream
     * @param [in] bg_color Background color of the canvas,in RGB hex value. For example, #FFB6C1 represents light pink. The default value is #000000 (black).
     * @param [in] mode Required. Layout Mode of the public stream. Refer StreamLayoutMode{@link #StreamLayoutMode} to for more details.
     */
    virtual void setLayoutParam(
                PublicStreamLayoutRegion regions[], int32_t regions_size, const char* bg_color,
                StreamLayoutMode mode) = 0;
    /** {zh}
     * @type api
     * @brief 将输入的 json 格式的字符串转成 ITranscoderParam 结构体
     * @param [in] json_str json 格式字符串
     * @return 转换后的 ITranscoderParam 结构体
     */
    /** {en}
     * @type api
     * @brief Transvert the json strings into ITranscoderParam struct
     * @param [in] json_str json string
     * @return ITranscoderParam struct
     */
    virtual IPublicStreamParam* inflatten(const char* json_str) = 0;
    /** {zh}
     * @type api
     * @brief 参数校验
     * @param [in] json_str 传入参数，json 格式字符串
     * @return 检查结果<br>
     *        `true`: 所有参数都合法<br>
     *        `false`: 存在不合法参数
     */
    /** {en}
     * @type api
     * @brief Validate the parameters passed in
     * @param [in] json_str String written in json syntax
     * @return <br>
     *         `true`: All the parameters are valid.<br>
     *         `false`: Invalid parameters.
     */
    virtual bool checkParameter(const char* json_str) = 0;
    /**
     * @hidden constructor/destructor
     */
    virtual ~IPublicStreamParam() = default;
};

/** {zh}
 * @type api
 * @brief 创建公共流参数实例
 */
 /** {en}
 * @hidden currently not available
 * @type api
 * @brief Create a instance of public stream parameters
 */
BYTERTC_API IPublicStreamParam* createPublicStreamParam();
} /* namespace bytertc */
