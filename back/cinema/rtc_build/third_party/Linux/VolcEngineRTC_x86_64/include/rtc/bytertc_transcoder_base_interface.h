//
//  bytertc_transcoder_base_interface.h
//  ByteRTC
//
#pragma once

namespace bytertc {
/** {zh}
 * @hidden for internal use only
 * @type keytype
 * @brief 合流房间状态
 */
/** {en}
 * @hidden for internal use only
 * @type keytype
 * @brief Confluence room status
 */
enum TranscoderRoomStatus {
    /**
     * @brief join room status
     */
    kRoomStatusJoinRoom,
    /**
     * @brief leave room status
     */
    kRoomStatusLeaveRoom,
    /**
     * @brief room status was offline
     */
    kRoomStatusOffline,
    /**
     * @brief room status was online
     */
    kRoomStatusOnline,
};

/** {zh}
 * @deprecated since 3.52, use MixedStreamMediaType{@link #MixedStreamMediaType} instead.
 * @type keytype
 * @brief 合流输出内容类型
 */
/** {en}
 * @deprecated since 3.52, use MixedStreamMediaType{@link #MixedStreamMediaType} instead.
 * @type keytype
 * @brief Types of streams to be mixed
 */
enum class TranscoderContentControlType {
    /** {zh}
     * @brief 输出的混流包含音频和视频
     */
    /** {en}
     * @brief Audio and video
     */
    kHasAudioAndVideo = 0,
    /** {zh}
     * @brief 输出的混流只包含音频
     */
    /** {en}
     * @brief Audio only
     */
    kHasAudioOnly = 1,
    /** {zh}
     * @brief 输出的混流只包含视频
     */
    /** {en}
     * @brief Video only
     */
    kHasVideoOnly = 2,
};
/** {zh}
 * @type keytype
 * @brief 合流转码参数
 */
/** {en}
 * @type keytype
 * @brief Properties of the mixing stream
 */
class ITranscoderParamBase {
public:
    /** {zh}
     * @type api
     * @region 转码
     * @brief 获取合流房间 ID
     * @return 合流房间 ID
     */
    /** {en}
     * @type api
     * @region Forward to live broadcast
     * @brief Get the confluence room ID
     * @return Confluence room ID
     */
    virtual const char* roomID() = 0;
    /** {zh}
     * @type api
     * @region 转推直播
     * @brief 获取 other 数据
     * @return Other数据
     */
    /** {en}
     * @type api
     * @region  retweet live
     * @brief  Get other data
     * @return other data
     */
    virtual const char* other() = 0;
    /** {zh}
     * @type api
     * @region 转推直播
     * @brief 获取通过 flatten{@link #ITranscoderParamBase#flatten} 方法转换得到的 json 格式内容
     * @return json 格式数据
     */
    /** {en}
     * @type api
     * @region Forward to live broadcast
     * @brief Get the json format content json
     * @return Format data converted by the flatten{@link #ITranscoderParamBase#flatten} method
     */
    virtual const char* jsonContent() = 0;
    /** {zh}
     * @type api
     * @region 转推直播
     * @brief 获取合流参数中视窗的数量
     * @return 合流参数中视窗的数量
     */
    /** {en}
     * @type api
     * @region Forward to live broadcast
     * @brief Get the number of windows in the confluence parameter
     * @return The number of windows in the confluence parameter
     */
    virtual int32_t layoutRegionsSize() = 0;
    /** {zh}
     * @type api
     * @region 转推直播
     * @brief 获取背景颜色
     * @return 背景颜色
     */
    /** {en}
     * @type api
     * @region  turn to push live
     * @brief  Get background color
     * @return  Background color
     */
    virtual const char* backgroundColor() = 0;
    /** {zh}
     * @type api
     * @region 转推直播
     * @brief 设置合流房间 ID
     * @param [in] room_id 发起合流的用户所在的房间 ID
     */
    /** {en}
     * @type api
     * @region Forward to live broadcast
     * @brief Set the confluence room ID
     * @param  [in] room_id The room ID of the user who initiated the confluence
     */
    virtual void setRoomID(const char* room_id) = 0;
    /** {zh}
     * @type api
     * @region 转推直播
     * @brief 设置 jsonContent  <br>
     *        传入通过 flatten{@link #ITranscoderParamBase#flatten} 方法转换得到的 json 格式内容
     * @param [in] json_content json 格式内容
     */
    /** {en}
     * @type api
     * @region Forward to live broadcast
     * @brief Settings jsonContent <br>
     *        Passing in json format content obtained by converting the flatten{@link #ITranscoderParamBase#flatten} method
     * @param  [in] json_content Json format content
     */
    virtual void setJsonContent(const char* json_content) = 0;
    /** {zh}
     * @type api
     * @region 转推直播
     * @brief 设置 other 数据
     * @param [in] other other 数据
     */
    /** {en}
     * @type api
     * @region Forward to live broadcast
     * @brief Settings other data
     * @param [in] other other data
     */
    virtual void setOther(const char* other) = 0;
    /** {zh}
     * @type api
     * @region 转推直播
     * @brief 将合流参数转成 json 字符串
     * @param [in] content_type 内容属性，表明是合流信令
     * @param [in] action 合流状态，可选取值如下：  <br>
     *               + started: 开启合流  <br>
     *               + layoutChanged: 更新合流布局  <br>
     *               + stopped: 停止合流
     * @return 转换后的 json 字符串
     */
    /** {en}
     * @type api
     * @region Forward push live broadcast
     * @brief Turn the confluence parameter into json string
     * @param  [in] content_type Content attribute to indicate the confluence signaling
     * @param  [in] action Confluence status. The optional values are as follows: <br>
     *                + Started: open the confluence <br>
     *                + LayoutChanged: update the confluence layout <br>
     *                + Stopped: Stop Confluence
     * @return Converted json string
     */
    virtual const char* flatten(const char* content_type, const char* action) = 0;
    /**
     * @hidden constructor/destructor
     */
    virtual ~ITranscoderParamBase() = default;
};
}/*namespace bytertc*/
