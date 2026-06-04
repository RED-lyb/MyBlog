/*
 * Copyright (c) 2023 The VolcEngineRTC project authors. All Rights Reserved.
 * @brief VolcEngineRTC Audio Effect Player
*/
#pragma once

#include "bytertc_audio_frame.h"

namespace bytertc {
/** {zh}
 * @type callback
 * @brief 本地音频文件混音的音频帧观察者。
 */
/** {en}
 * @type callback
 * @brief observer for the audio frames during local audio file mixing.
 */
class IMediaPlayerAudioFrameObserver {
public:
    /** {zh}
     * @type callback
     * @brief 当本地音频文件混音时，回调播放的音频帧。
     * @param player_id
     * @param frame 参看 IAudioFrame{@link #IAudioFrame}。
     */
    /** {en}
     * @type callback
     * @brief The callback for the audio frames during local audio file mixing.
     * @param player_id
     * @param frame See IAudioFrame{@link #IAudioFrame}.
     */
    virtual void onFrame(int player_id, const IAudioFrame& frame) = 0;
    /**
     * @hidden constructor
     */
    virtual ~IMediaPlayerAudioFrameObserver() {
    }
};
/** {zh} 
 * @type keytype
 * @brief 自定义音频源模式
 */
/** {en} 
 * @type keytype
 * @brief Custom audio source mode
 */
enum MediaPlayerCustomSourceMode{
    /** {zh} 
     * @brief 当播放来自本地的 PCM 数据时，使用此选项。
     */
    /** {en} 
     * @brief When you use the local PCM data, use this mode.
     */
    kMediaPlayerCustomSourceModePush = 0,
    /** {zh} 
     * @brief 当播放来自内存的音频数据时，使用此选项。
     */
    /** {en} 
     * @brief When you use the audio data from local memory, use this mode.
     */
    kMediaPlayerCustomSourceModePull,
};

/** {zh}
 * @type keytype
 * @brief 音频数据的起始读取位置。
 */
 /** {en}
 * @type keytype
 * @brief The starting position where audio data seeking begins. 
 */
enum MediaPlayerCustomSourceSeekWhence{
    /** {zh}
     * @brief 从音频数据的头开始读取，读取的实际偏移量为参数 offset 的值。
     */
    /** {en}
     * @brief Seeks from the head of the audio data, and the actual data offset after seeking is offset.
     */
    kMediaPlayerCustomSourceSeekWhenceSet = 0,
    /** {zh}
     * @brief 从音频数据的某一位置开始读取，读取的实际偏移量为音频数据当前的读取位置位置加上参数 offset 的值。 
     */
    /** {en}
     * @brief Seeks from a specific position of the audio data stream, and the actual data offset after seeking is the current position plus offset.
     */
    kMediaPlayerCustomSourceSeekWhenceCur = 1,
    /** {zh}
     * @brief 从音频数据的尾开始读取，读取的实际数据偏移量为用户传入的音频数据大小加上参数 offset 的值。 
     */
    /** {en}
     * @brief Seeks from the end of the audio data, and the actual data offset after seeking is the whole data length plus offset.
     */
    kMediaPlayerCustomSourceSeekWhenceEnd = 2,
    /** {zh}
     * @brief 返回音频数据的大小。
     */
    /** {en}
     * @brief Returns the size of audio data.
     */
    kMediaPlayerCustomSourceSeekWhenceSize = 3,
};
/** {zh} 
 * @type keytype
 * @brief 自定义音频流类型
 */
/** {en} 
 * @type keytype
 * @brief Custom audio source stream type
 */
enum MediaPlayerCustomSourceStreamType{
    /** {zh} 
     * @brief 当播放来自本地的 PCM 数据时，使用此选项。
     */
    /** {en} 
     * @brief When you use the local PCM data, use this type.
     */
    kMediaPlayerCustomSourceStreamTypeRaw = 0,
    /** {zh} 
     * @brief 当播放来自内存的音频数据时，使用此选项。
     */
    /** {en} 
     * @brief When you use the audio data from local memory, use this type.
     */
    kMediaPlayerCustomSourceStreamTypeEncoded,
};
/** {zh}
 * @type callback
 * @brief 内存播放数据源回调
 */
/** {en}
 * @type callback
 * @brief  In-memory audio data playing callback interface
 */
class IMediaPlayerCustomSourceProvider {
public:
    /** {zh}
     * @valid since 3.53
     * @type callback
     * @region 音乐播放器
     * @brief 调用 openWithCustomSource{@link #IMediaPlayer#openWithCustomSource} 接口播放用户传入的内存音频数据时，会触发此回调，用户需要写入音频数据。
     * @param [in] *buffer 内存地址。在该地址中写入音频数据，写入音频数据的大小不超过 bufferSize 中填入的数值。支持的音频数据格式有: mp3，aac，m4a，3gp，wav。
     * @param [in] buffer_size 音频数据大小，单位为字节。如果你想停止播放内存音频数据，可在 bufferSize 中填入小于或等于 0 的数，此时 SDK 会停止调用此接口。 
     * @return 返回实际读取的音频数据大小。
     * @notes 若 openWithCustomSource{@link #IMediaPlayer#openWithCustomSource} 接口调用失败，请在 buffer 和 bufferSize 两个参数中填入 0。 此时 SDK 会停止调用此接口。
     */
    /** {en}
     * @valid since 3.53
     * @type callback
     * @region Music player
     * @brief Callback of getting the path and size of the audio data you input. <br>
     *        When you call openWithCustomSource{@link #IMediaPlayer#openWithCustomSource} API to play the in-memory audio data you input, this callback will be triggered and you need to enter the path and size of the audio data. 
     * @param [in] *buffer The path of the audio data you input. The size of audio data should be equal to or less than the value of bufferSize. The supported formats are: mp3, aac, m4a, 3gp, wav.
     * @param [in] buffer_size The size of the audio data, in bytes. If you want to stop audio playing, you can enter a figure less than or equal to zero into bufferSize and then SDK will stop calling this callback. 
     * @return Returns the size of the audio data that are actually read. 
     * @notes If calling openWithCustomSource{@link #IMediaPlayer#openWithCustomSource} API failed, please enter 0 into buffer and bufferSize. In this situation, SDK will stop calling this callback.  
     */
    virtual int onReadData(uint8_t *buffer, int buffer_size) = 0;
    /** {zh}
     * @valid since 3.53
     * @type callback
     * @region 音乐播放器
     * @brief 根据设置好的内存音频数据的读取位置和读取偏移量对音频数据进行偏移，以便 SDK 读取和分析音频数据。 <br>
     *        在调用 openWithCustomSource{@link #IMediaPlayer#openWithCustomSource} 接口传入内存音频数据，或者调用 setPosition{@link #IMediaPlayer#setPosition} 设置了音频数据的起始播放位置后，SDK 会对音频数据进行读取和分析，此时会触发该回调，你需要根据参数中设置的起始读取位置和偏移量进行操作。
     * @param [in] offset 音频数据读取偏移量，单位为字节，取值可正可负。  <br>
     * @param [in] whence 音频数据的起始读取位置。参看 MediaPlayerCustomSourceSeekWhence{@link #MediaPlayerCustomSourceSeekWhence}
     * @return <br>
     *         定位成功，返回偏移后的位置信息，或返回音频数据的大小。<br>
     *         定位失败，返回 -1。         
     */
    /** {en}
     * @valid since 3.53
     * @type callback
     * @region Music player
     * @brief Seeking the audio data based on the set starting position and offset to help SDK read and analyze data. <br>
     *        When you call openWithCustomSource{@link #IMediaPlayer#openWithCustomSource}  API to play the in-memory audio data you input, or when you call setPosition{@link #IMediaPlayer#setPosition} to set the starting position of audio playing, this callback will be trigerred and you need to seek the audio data accorring to the value of offset and whence.  
     * @param [in] offset The offset of the target position relative to the starting position, in bytes. The value can be positive or negative.  <br>
     * @param [in] whence The starting position of the seeking.  Refer to MediaPlayerCustomSourceSeekWhence{@link #MediaPlayerCustomSourceSeekWhence} for more details. 
     * @return <br>
     *         If the seeking succeeded, the information on the final adjusted play position after seeking or the size of the audio data will be returned.<br>
     *         If the seeking failed, -1 will be returned.  
     */
    virtual int64_t onSeek(int64_t offset, MediaPlayerCustomSourceSeekWhence whence) = 0;
    
    virtual ~IMediaPlayerCustomSourceProvider() {}
};
/** {zh}
 * @type keytype
 * @brief 音频源
 */
/** {en}
 * @type keytype
 * @brief The audio source for media player.
 */
struct MediaPlayerCustomSource {
    /** {zh} 
     * @hidden reserved for later use
     */
    IMediaPlayerCustomSourceProvider* provider = nullptr;
    /** {zh} 
     * @type keytype
     * @brief 数据源模式，详见 MediaPlayerCustomSourceMode{@link #MediaPlayerCustomSourceMode}。
     */
    /** {en} 
     * @type keytype
     * @brief See MediaPlayerCustomSourceMode{@link #MediaPlayerCustomSourceMode}.
     */
    MediaPlayerCustomSourceMode mode = kMediaPlayerCustomSourceModePush;
    /** {zh} 
     * @type keytype
     * @brief 数据源类型，详见 MediaPlayerCustomSourceStreamType{@link #MediaPlayerCustomSourceStreamType}
     */
    /** {en} 
     * @type keytype
     * @brief See MediaPlayerCustomSourceStreamType{@link #MediaPlayerCustomSourceStreamType}.
     */
    MediaPlayerCustomSourceStreamType type = kMediaPlayerCustomSourceStreamTypeRaw;
};
/** {zh}
 * @type callback
 * @brief IMediaPlayer{@link #IMediaPlayer} 对应的回调句柄。你必须调用 setEventHandler{@link #IMediaPlayer#setEventHandler} 完成设置后，才能收到对应回调。
 */
/** {en}
 * @type callback
 * @brief Event handler for IMediaPlayer{@link #IMediaPlayer}. You must call setEventHandler{@link #IMediaPlayer#setEventHandler} to set the corresponding event handler to get the events.
 */
class IMediaPlayerEventHandler {
public:
    virtual ~IMediaPlayerEventHandler() {}
    /** {zh}
    * @type callback
    * @brief 播放状态改变时回调。
    * @param player_id IMediaPlayer{@link #IMediaPlayer} 的 ID。通过 getMediaPlayer{@link #IRTCVideo#getMediaPlayer} 设置。
    * @param state 混音状态。参考 PlayerState{@link #PlayerState}。
    * @param error 错误码。参考 PlayerError{@link #PlayerError}。
    */
    /** {en}
    * @type callback
    * @brief Callback for audio mixing status change.
    * @param player_id The ID of IMediaPlayer{@link #IMediaPlayer}. Set by getMediaPlayer{@link #IRTCVideo#getMediaPlayer}.
    * @param state See PlayerState{@link #PlayerState}.
    * @param error See PlayerError{@link #PlayerError}.
    */
    virtual void onMediaPlayerStateChanged(int player_id, PlayerState state, PlayerError error) = 0;
   /** {zh}
    * @type callback
    * @brief 播放进度周期性回调。回调周期通过 setProgressInterval{@link #IMediaPlayer#setProgressInterval} 设置。
    * @param player_id IMediaPlayer{@link #IMediaPlayer} 的 ID。通过 getMediaPlayer{@link #IRTCVideo#getMediaPlayer} 设置。
    * @param progress 进度。单位 ms。
    */
    /** {en}
    * @type callback
    * @brief Periodic callback for audio mixing progress. The period is set by setProgressInterval{@link #IMediaPlayer#setProgressInterval}.
    * @param player_id The ID of IMediaPlayer{@link #IMediaPlayer}. Set by getMediaPlayer{@link #IRTCVideo#getMediaPlayer}.
    * @param progress Mixing progress in ms.
    */
    virtual void onMediaPlayerPlayingProgress(int player_id, int64_t progress) = 0;
};
/** {zh}
 * @valid since 3.53
 * @type api
 * @brief 音乐播放器<br>
 *        调用 setEventHandler{@link #IMediaPlayer#setEventHandler} 设置回调句柄以获取相关回调。
 */
/** {en}
 * @valid since 3.53
 * @type api
 * @brief Media player<br>
 *        Call setEventHandler{@link #IMediaPlayer#setEventHandler} to set the callback handler to receive related callbacks.
 */
class IMediaPlayer {
public:
    IMediaPlayer(){}
    virtual ~IMediaPlayer() {}
    /** {zh}
     * @type api
     * @brief 打开音乐文件。
     *        一个播放器实例仅能够同时打开一个音乐文件。如果需要同时打开多个音乐文件，请创建多个音乐播放器实例。
     *        要播放 PCM 格式的音频数据，参看 openWithCustomSource{@link #IMediaPlayer#openWithCustomSource}。`openWithCustomSource` 和此 API 互斥。
     * @param file_path 音乐文件路径。
     *        支持在线文件的 URL、本地文件的 URI、或本地文件的绝对路径。对于在线文件的 URL，仅支持 https 协议。
     *        推荐的采样率：8KHz、16KHz、22.05KHz、44.1KHz、48KHz。
     *        不同平台支持的本地文件格式:
     *        <table>
     *           <tr><th></th><th>mp3</th><th>mp4</th><th>aac</th><th>m4a</th><th>3gp</th><th>wav</th><th>ogg</th><th>ts</th><th>wma</th></tr>
     *           <tr><td>Android</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td></td><td></td></tr>
     *           <tr><td>iOS/macOS</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td></td><td></td><td></td></tr>
     *           <tr><td>Windows</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td></td><td>Y</td><td>Y</td></tr>
     *        </table>
     *        不同平台支持的在线文件格式:
     *        <table>
     *           <tr><th></th><th>mp3</th><th>mp4</th><th>aac</th><th>m4a</th><th>3gp</th><th>wav</th><th>ogg</th><th>ts</th><th>wma</th></tr>
     *           <tr><td>Android</td><td>Y</td><td></td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td></td><td></td><td></td></tr>
     *           <tr><td>iOS/macOS</td><td>Y</td><td></td><td>Y</td><td>Y</td><td></td><td>Y</td><td></td><td></td><td></td></tr>
     *           <tr><td>Windows</td><td>Y</td><td></td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td></td><td>Y</td><td>Y</td></tr>
     *        </table>
     * @param config 详见 MediaPlayerConfig{@link #MediaPlayerConfig}。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     */
    /** {en}
     * @type api
     * @brief Open the audio file. <br>
     *        You can only open one audio file with one player instance at the same time. For multiple audio files at the same time, create multiple player instances.
     *        For audio file in PCM format, see openWithCustomSource{@link #IMediaPlayer#openWithCustomSource}. `openWithCustomSource` and this API are mutually exclusive.
     * @param file_path Audio file paths.
     *        URL of online file, URI of local file, or full path to local file. For URL of online file, only the https protocol is supported.
     *        Recommended sample rate for audio effect files: 8KHz、16KHz、22.05KHz、44.1KHz、48KHz.
     *        Local audio effect file formats supported by different platforms:
     *        <table>
     *           <tr><th></th><th>mp3</th><th>mp4</th><th>aac</th><th>m4a</th><th>3gp</th><th>wav</th><th>ogg</th><th>ts</th><th>wma</th></tr>
     *           <tr><td>Android</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td></td><td></td></tr>
     *           <tr><td>iOS/macOS</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td></td><td></td><td></td></tr>
     *           <tr><td>Windows</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td></td><td>Y</td><td>Y</td></tr>
     *        </table>
     *        Online audio effect file formats supported by different platforms.
     *        <table>
     *           <tr><th></th><th>mp3</th><th>mp4</th><th>aac</th><th>m4a</th><th>3gp</th><th>wav</th><th>ogg</th><th>ts</th><th>wma</th></tr>
     *           <tr><td>Android</td><td>Y</td><td></td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td></td><td></td><td></td></tr>
     *           <tr><td>iOS/macOS</td><td>Y</td><td></td><td>Y</td><td>Y</td><td></td><td>Y</td><td></td><td></td><td></td></tr>
     *           <tr><td>Windows</td><td>Y</td><td></td><td>Y</td><td>Y</td><td>Y</td><td>Y</td><td></td><td>Y</td><td>Y</td></tr>
     *        </table>
     * @param config See MediaPlayerConfig{@link #MediaPlayerConfig}.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     */
    virtual int open(const char* file_path, const MediaPlayerConfig& config) = 0;
    /** {zh}
     * @type api
     * @brief 播放音乐。你仅需要在调用 open{@link #IMediaPlayer#open}，且未开启自动播放时，调用此方法。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes  <br>
     * + 要播放 PCM 格式的音频数据，参看 openWithCustomSource{@link #IMediaPlayer#openWithCustomSource}。`openWithCustomSource` 和此 API 互斥。
     * + 调用本方法播放音频文件后，可调用 stop{@link #IMediaPlayer#stop} 方法暂停播放。
     */
    /** {en}
     * @type api
     * @brief Start playing the audio. Call this API when you call open{@link #IMediaPlayer#open} and set `AutoPlay=False`.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes  <br>
     * + For audio file in PCM format, see openWithCustomSource{@link #IMediaPlayer#openWithCustomSource}. `openWithCustomSource` and this API are mutually exclusive.
     * + After calling this API, call stop{@link #IMediaPlayer#stop} to stop playing the audio file.
     */
    virtual int start() = 0;
    /** {zh}
     * @type api
     * @brief 启动音频裸数据混音。
     *        要播放音乐文件，参看 open{@link #IMediaPlayer#open}。`open` 与此 API 互斥。
     * @param source 数据源，详见 MediaPlayerCustomSource{@link #MediaPlayerCustomSource}
     * @param config 详见 MediaPlayerConfig{@link #MediaPlayerConfig}
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes  <br>
     *       + 调用本方法启动后，再调用 pushExternalAudioFrame{@link #IMediaPlayer#pushExternalAudioFrame} 推送音频数据，才会开始混音。
     *       + 如要结束 PCM 音频数据混音，调用 stop{@link #IMediaPlayer#stop}。
     */
    /** {en}
     * @type api
     * @brief Enable audio mixing with audio raw data.
     *        To open the audio file, see open{@link #IMediaPlayer#open}. `open` and this API are mutually exclusive.
     * @param source See MediaPlayerCustomSource{@link #MediaPlayerCustomSource}.
     * @param config See MediaPlayerConfig{@link #MediaPlayerConfig}.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes  <br>
     *       + After calling this API, you must call pushExternalAudioFrame{@link #IMediaPlayer#pushExternalAudioFrame} to push audio data and start the audio mixing.
     *       + To stop the raw data audio mixing, call stop{@link #IMediaPlayer#stop}.
     */
    virtual int openWithCustomSource(const MediaPlayerCustomSource& source, const MediaPlayerConfig& config) = 0;
    /** {zh}
     * @type api
     * @brief 调用 open{@link #IMediaPlayer#open}, start{@link #IMediaPlayer#start}, 或 openWithCustomSource{@link #IMediaPlayer#openWithCustomSource} 开始播放后，可以调用本方法停止。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     */
    /** {en}
     * @type api
     * @brief After calling open{@link #IMediaPlayer#open}, start{@link #IMediaPlayer#start}, or openWithCustomSource{@link #IMediaPlayer#openWithCustomSource} to start audio mixing, call this method to stop audio mixing.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     */
    virtual int stop() = 0;
    /** {zh}
     * @type api
     * @brief 调用 open{@link #IMediaPlayer#open}，或 start{@link #IMediaPlayer#start} 开始播放音频文件后，调用本方法暂停播放。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes <br>
     *        + 调用本方法暂停播放后，可调用 resume{@link #IMediaPlayer#resume} 恢复播放。<br>
     *        + 此接口仅支持音频文件，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief After calling open{@link #IMediaPlayer#open}, or start{@link #IMediaPlayer#start} to start audio mixing, call this API to pause audio mixing.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes <br>
     *        + After calling this API to pause audio mixing, call resume{@link #IMediaPlayer#resume} to resume audio mixing.<br>
     *        + The API is valid for audio file, not PCM data.
     */
    virtual int pause() = 0;
    /** {zh}
     * @type api
     * @brief 调用 pause{@link #IMediaPlayer#pause} 暂停音频播放后，调用本方法恢复播放。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes <br>
     *        此接口仅支持音频文件，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief After calling pause{@link #IMediaPlayer#pause} to pause audio mixing, call this API to resume audio mixing.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes <br>
     *        The API is valid for audio file, not PCM data.
     */
    virtual int resume() = 0;
    /** {zh}
     * @type api
     * @brief 调节指定混音的音量大小，包括音乐文件混音和 PCM 混音。
     * @param volume 播放音量相对原音量的比值。单位为 %。范围为 `[0, 400]`，建议范围是 `[0, 100]`。带溢出保护。
     * @param type 详见 AudioMixingType{@link #AudioMixingType}。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes 仅在音频播放进行状态时，调用此方法。
     */
     /** {en}
     * @type api
     * @brief Adjusts the volume of the specified audio mixing, including media file mixing and PCM mixing.
     * @param volume The ratio of the volume to the original volume in % with overflow protection. The range is `[0, 400]` and the recommended range is `[0, 100]`.
     * @param type See AudioMixingType{@link #AudioMixingType}.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes Call this API only when audio is mixing.
     */
    virtual int setVolume(int volume, AudioMixingType type) = 0;
    /** {zh}
     * @type api
     * @brief 获取当前音量
     * @param type 详见 AudioMixingType{@link #AudioMixingType}。
     * @return  <br>
     *        + >0: 成功, 当前音量值。  <br>
     *        + < 0: 失败
     * @notes 仅在音频播放进行状态时，调用此方法。包括音乐文件混音和 PCM 混音。
     */
    /** {en}
     * @type api
     * @brief Gets the current volume.
     * @param type See AudioMixingType{@link #AudioMixingType}.
     * @return  <br>
     *        + >0: Success, the current volume. <br>
     *        + < 0: Failed.
     * @notes Call this API only when audio is mixing, including media file mixing and PCM mixing.
     */
    virtual int getVolume(AudioMixingType type) = 0;
    /** {zh}
     * @type api
     * @brief 获取音乐文件时长。
     * @return  <br>
     *        + >0: 成功, 音乐文件时长，单位为毫秒。  <br>
     *        + < 0: 失败
     * @notes <br>
     *        + 仅在音频播放进行状态时，调用此方法。
     *        + 此接口仅支持音频文件，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief Gets the duration of the media file.
     * @return  <br>
     *        + >0: Success, the duration of the media file in milliseconds.  <br>
     *        + < 0: Failed.
     * @notes <br>
     *        + Call this API only when audio is mixing.
     *        + The API is valid for audio file, not PCM data.
     */
    virtual int getTotalDuration() = 0;
    /** {zh}
     * @type api
     * @brief 获取混音音乐文件的实际播放时长，单位为毫秒。
     * @return  <br>
     *        + >0: 实际播放时长。
     *        + < 0: 失败。
     * @notes <br>
     *        + 实际播放时长指的是歌曲不受停止、跳转、倍速、卡顿影响的播放时长。例如，若歌曲正常播放到 1:30 时停止播放 30s 或跳转进度到 2:00, 随后继续正常播放 2分钟，则实际播放时长为 3分30秒。
     *        + 仅在音频播放进行状态，且 setProgressInterval{@link #IMediaPlayer#setProgressInterval} 设置间隔大于 `0` 时，调用此方法。
     *        + 此接口仅支持音频文件，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief Gets the actual playback duration of the mixed media file, in milliseconds.
     * @return  <br>
     *        + >0: Success, the actual playback time.
     *        + < 0: Failed.
     * @notes <br>
     *        + The actual playback time refers to the playback time of the song without being affected by stop, jump, double speed, and freeze. For example, if the song stops playing for 30 seconds at 1:30 or skips to 2:00, and then continues to play normally for 2 minutes, the actual playing time is 3 minutes and 30 seconds.
     *        + Call this API only when audio is mixing and the interval set by setProgressInterval{@link #IMediaPlayer#setProgressInterval} is above `0`.
     *        + The API is valid for audio file, not PCM data.
     */
    virtual int getPlaybackDuration() = 0;
    /** {zh}
     * @type api
     * @brief 获取音乐文件播放进度。
     * @return  <br>
     *        + >0: 成功, 音乐文件播放进度，单位为毫秒。
     *        + < 0: 失败
     * @notes <br>
     *        + 仅在音频播放进行状态时，调用此方法。
     *        + 此接口仅支持音频文件，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief Gets the playback progress of the media file.
     * @return  <br>
     *        + >0: Success, the playback progress of media file in ms.
     *        + < 0: Failed.
     * @notes <br>
     *        + Call this API only when audio is mixing.
     *        + The API is valid for audio file, not PCM data.
     */
    virtual int getPosition() = 0;
    /** {zh}
     * @type api
     * @brief 开启变调功能，多用于 K 歌场景。
     * @param pitch 与音乐文件原始音调相比的升高/降低值，取值范围为 `[-12，12]`，默认值为 0。每相邻两个值的音高距离相差半音，正值表示升调，负值表示降调。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes <br>
     *        + 仅在音频播放进行状态时，调用此方法。
     *        + 仅支持音乐文件混音，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief Set the pitch of the local audio file mixing. Usually used in karaoke scenes.
     * @param pitch The increase or decrease value compared with the original pitch of the music file. The range is `[-12, 12]`. The default value is 0. The pitch distance between two adjacent values is half a step. A positive value indicates a rising pitch, and a negative value indicates a falling pitch.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes <br>
     *        + Call this API only when audio is mixing.
     *        + Support audio file only and not PCM data.
     */
    virtual int setAudioPitch(int pitch) = 0;
    /** {zh}
     * @type api
     * @brief 设置音乐文件的起始播放位置。
     * @param position 音乐文件起始播放位置，单位为毫秒。  <br>
     *        你可以通过 getTotalDuration{@link #IMediaPlayer#getTotalDuration} 获取音乐文件总时长，position 的值应小于音乐文件总时长。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes <br>
     *        + 此接口仅支持音频文件，不支持 PCM 数据。
     *        + 在播放在线文件时，调用此接口可能造成播放延迟的现象。
     */
    /** {en}
     * @type api
     * @brief Sets the starting playback position of the media file.
     * @param position The starting position of the media file in milliseconds.
     *        You can get the total duration of the media file through getTotalDuration{@link #IMediaPlayer#getTotalDuration}. The value of position should be less than the total duration of the media file.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes  <br>
     *        + The API is valid for audio file, not PCM data.
     *        + When playing online files, calling this API may cause playback delay.
     */
    virtual int setPosition(int position) = 0;
    /** {zh}
     * @type api
     * @brief 设置当前音乐文件的声道模式
     * @param mode 声道模式。默认的声道模式和源文件一致，详见 AudioMixingDualMonoMode{@link #AudioMixingDualMonoMode}。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes <br>
     *        + 仅在音频播放进行状态时，调用此方法。
     *        + 仅支持音频文件，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief Sets the channel mode of the mixing of the media file.
     * @param mode The mode of channel. The default channel mode is the same as the source file. See AudioMixingDualMonoMode{@link #AudioMixingDualMonoMode}.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes <br>
     *       + Call this API only when audio is mixing.
     *       + Audio file is supported, but not PCM data.
     */
    virtual int setAudioDualMonoMode(AudioMixingDualMonoMode mode) = 0;
    /** {zh}
     * @type api
     * @brief 获取当前音乐文件的音轨数
     * @return + >= 0：成功，返回当前音乐文件的音轨数
     *         + < 0：方法调用失败
     * @notes <br>
     *        + 仅在音频播放进行状态时，调用此方法。
     *        + 此方法仅支持音乐文件，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief Gets the track count of the current media file.
     * @return + >= 0：Success. Return the track count of the current media file.
     *         + < 0：Failed.
     * @notes <br>
     *       + Call this API only when audio is mixing.
     *       + This API is valid for audio file, not PCM data.
     */
    virtual int getAudioTrackCount() = 0;
    /** {zh}
     * @type api
     * @brief 指定当前音乐文件的播放音轨
     * @param index 指定的播放音轨，从 0 开始，取值范围为 `[0, getAudioTrackCount()-1]`。
     *        设置的参数值需要小于 getAudioTrackCount{@link #IMediaPlayer#getAudioTrackCount} 的返回值
     * @notes <br>
     *        + 仅在音频播放进行状态时，调用此方法。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     *        + 此方法仅支持音乐文件，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief Specifies the playback track of the current media file.
     * @param index The specified playback audio track, starting from 0, and the range is `[0, getAudioTrackCount()-1]`. The value must be less than the return value of getAudioTrackCount{@link #IMediaPlayer#getAudioTrackCount}.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes <br>
     *       + Call this API only when audio is mixing.
     *       + This API is valid for audio file, not PCM data.
     */
    virtual int selectAudioTrack(int index) = 0;
    /** {zh}
     * @type api
     * @brief 设置播放速度
     * @param speed 播放速度与原始文件速度的比例，单位：%，取值范围为 `[50,200]`，默认值为 100。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes <br>
     *        + 仅在音频播放进行状态时，调用此方法。
     *        + 此方法对音频文件可用，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief Set the playback speed of the audio file.
     * @param speed The ratio of the actual playback speed than that of the original speed of the audio file in %. The range is `[50,200]`. The default value is 100.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes <br>
     *       + Call this API only when audio is mixing.
     *       + The API is valid for audio file and not PCM data.
     */
    virtual int setPlaybackSpeed(int speed) = 0;
    /** {zh}
     * @type api
     * @brief 设置音频文件混音时，收到 onMediaPlayerPlayingProgress{@link #IMediaPlayerEventHandler#onMediaPlayerPlayingProgress} 的间隔。
     * @param interval 时间间隔，单位毫秒。
     *       + interval > 0 时，触发回调。实际间隔为 10 的倍数。如果输入数值不能被 10 整除，将自动向上取整。例如传入 `52`，实际间隔为 60 ms。
     *       + interval <= 0 时，不会触发回调。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes <br>
     *        + 仅在音频播放进行状态时，调用此方法。
     *        + 此方法仅支持音频文件，不支持 PCM 数据。
     */
     /** {en}
     * @type api
     * @brief Set the interval of the periodic callback onMediaPlayerPlayingProgress{@link #IMediaPlayerEventHandler#onMediaPlayerPlayingProgress} during audio mixing.
     * @param interval interval in ms.
     *       + interval > 0: The callback is enabled. The actual interval is `10*(mod(10)+1)`.
     *       + interval <= 0: The callback is disabled.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes <br>
     *       + Call this API only when audio is mixing.
     *       + This API is valid for audio file, not PCM data.
     */
    virtual int setProgressInterval(int64_t interval) = 0;
    /** {zh}
     * @type api
     * @brief 如果你需要使用 enableVocalInstrumentBalance{@link #IRTCVideo#enableVocalInstrumentBalance} 对音频文件/PCM 音频数据设置音量均衡，你必须通过此接口传入其原始响度。
     * @param loudness 原始响度，单位：lufs，取值范围为 `[-70.0, 0.0]`。
     *        当设置的值小于 -70.0lufs 时，则默认调整为 -70.0lufs，大于 0.0lufs 时，则不对该响度做音量均衡处理。默认值为 1.0lufs，即不做处理。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @notes <br>
     *        + 仅在音频播放进行状态时，调用此方法。
     *        + 此方法对音频文件和音频裸数据播放都可用。
     */
    /** {en}
     * @type api
     * @brief To call enableVocalInstrumentBalance{@link #IRTCVideo#enableVocalInstrumentBalance} to adjust the volume of the mixed media file or the PCM audio data, you must pass in its original loudness through this API.
     * @param loudness Original loudness in lufs. The range is `[-70.0, 0.0]`.
     *       When the value is less than -70.0lufs, it will be adjusted to -70.0lufs by default, and if it is more than 0.0lufs, the loudness will not be equalized. The default value is 1.0lufs, which means no processing.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes <br>
     *       + Call this API only when audio is mixing.
     *       + The API is valid for audio file and PCM data.
     */
    virtual int setLoudness(float loudness) = 0;
    /** {zh}
     * @type api
     * @brief 注册回调句柄以在本地音乐文件混音时，收到相关回调。
     * @return  <br>
     *        + 0: 调用成功。
     *        + < 0 : 调用失败。查看 ReturnStatus{@link #ReturnStatus} 获得更多错误说明
     * @param observer 参看 IMediaPlayerAudioFrameObserver{@link #IMediaPlayerAudioFrameObserver}。
     * @notes <br>
     *        此接口仅支持音频文件，不支持 PCM 数据。
     */
    /** {en}
     * @type api
     * @brief Register an observer to receive related callbacks when the local media file is mixing.
     * @param observer See IMediaPlayerAudioFrameObserver{@link #IMediaPlayerAudioFrameObserver}.
     * @return  <br>
     *        + 0: Success.
     *        + < 0 : Fail. See ReturnStatus{@link #ReturnStatus} for more details.
     * @notes <br>
     *        The API is valid for audio file, not PCM data.
     */
    virtual int registerAudioFrameObserver(IMediaPlayerAudioFrameObserver* observer) = 0;
    /** {zh}
     * @type api
     * @brief 推送用于混音的 PCM 音频帧数据
     * @param audio_frame 音频帧，详见 IAudioFrame{@link #IAudioFrame}。
     *        + 音频采样格式必须为 S16。音频缓冲区内的数据格式必须为 PCM，其容量大小应该为 audioFrame.samples × audioFrame.channel × 2。
     *        + 必须指定具体的采样率和声道数，不支持设置为自动。
     * @return  <br>
     *       + 0: 成功  <br>
     *       + < 0: 失败
     * @notes
     *      + 调用该方法前，须通过 openWithCustomSource{@link #IMediaPlayer#openWithCustomSource} 启动外部音频流混音。
     *      + 使用参考建议：首次推送数据，请在应用侧先缓存一定数据（如 200 毫秒），然后一次性推送过去；此后的推送操作定时 10 毫秒一次，并且每次的音频数据量为 10 毫秒数据量。
     *      + 如果要暂停播放，暂停推送即可。
     */
    /** {en}
     * @type api
     * @brief Push PCM audio frame data for mixing.
     * @param audio_frame See IAudioFrame{@link #IAudioFrame}.
     * @return  <br>
     *       + 0: Success.  <br>
     *       + < 0: Failed.
     * @notes
     *      + Before calling this method, the raw audio data mixing must be enabled through openWithCustomSource{@link #IMediaPlayer#openWithCustomSource}.
     *      + Suggestions: Before pushing data for the first time, please cache a certain amount of data (like 200 ms) on the application side, and then push it at once. Schedule subsequent push operation every 10 ms with audio data of 10 ms.
     *      + To pause the playback, just pause the push.
     */
    virtual int pushExternalAudioFrame(IAudioFrame* audio_frame) = 0;
    /** {zh}
     * @type api
     * @brief 设置回调句柄。
     * @param handler 参看 IMediaPlayerEventHandler{@link #IMediaPlayerEventHandler}。
     * @return  <br>
     *        + 0: 成功。  <br>
     *        + < 0: 失败。
     */
    /** {en}
     * @type api
     * @brief Set the event handler.
     * @param handler See IMediaPlayerEventHandler{@link #IMediaPlayerEventHandler}.
     * @return  <br>
     *        + 0: Success.  <br>
     *        + < 0: Failed.
     */
    virtual int setEventHandler(IMediaPlayerEventHandler* handler) = 0;
 };


}
