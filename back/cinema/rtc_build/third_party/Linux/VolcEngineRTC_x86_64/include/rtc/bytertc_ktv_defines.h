#pragma once

#include <string>

namespace bytertc {

/** {zh}
 * @type keytype
 * @brief 歌曲过滤方式。
 */
/** {en}
 * @hidden currently not available currently not available
 * @type keytype
 * @brief The filter type of the music list.
 */
enum MusicFilterType {
    /** {zh}
     * @brief 不过滤。
     */
    /** {en}
     * @brief No filter.
     */
    kMusicFilterTypeNone = 0,
    /** {zh}
     * @brief 过滤没有歌词的歌曲。
     */
    /** {en}
     * @brief Remove music that does not have lyrics.
     */
    kMusicFilterTypeWithoutLyric     = 1 << 0,
    /** {zh}
     * @brief 过滤不支持打分的歌曲。
     */
    /** {en}
     * @brief Remove music that does not support scoring.
     */
    kMusicFilterTypeUnsupportedScore     = 1 << 1,
    /** {zh}
     * @brief 过滤不支持伴唱切换的歌曲。
     */
    /** {en}
     * @brief Remove music that does not support accompany mode.
     */
    kMusicFilterTypeUnsupportedAccopmay  = 1 << 2,
    /** {zh}
     * @brief 过滤没有高潮片段的歌曲。
     */
    /** {en}
     * @brief Remove music that does not have a climax part.
     */
    kMusicFilterTypeUnsupportedClimx     = 1 << 3,
};

/** {zh}
 * @type keytype
 * @brief 榜单类别。
 */
/** {en}
 * @hidden currently not available currently not available
 * @type keytype
 * @brief Hot music type.
 */
enum MusicHotType {
    /** {zh}
     * @brief 火山内容中心热歌榜。
     */
    /** {en}
     * @brief Hot music in the content center.
     */
    kMusicHotTypeContentCenter       = 1 << 0,
    /** {zh}
     * @brief 项目热歌榜。
     */
    /** {en}
     * @brief Hot music of the project.
     */
    kMusicHotTypeProject          = 1 << 1,
};

/** {zh}
 * @type keytype
 * @brief 原唱伴唱类型。
 */
/** {en}
 * @hidden currently not available currently not available
 * @type keytype
 * @brief Audio track type of the KTV player.
 */
enum class AudioTrackType {
    /** {zh}
     * @brief 播放原唱。
     */
    /** {en}
     * @brief Play the original music with vocals.
     */
    kOriginal = 1,
    /** {zh}
     * @brief 播放伴唱。
     */
    /** {en}
     * @brief Play the instrumental music without vocals.
     */
    kAccompy = 2
};

/** {zh}
 * @type keytype
 * @brief 音乐播放类型。
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief Audio play type.
 */
enum class AudioPlayType {
    /** {zh}
     * @brief 仅本地播放。
     */
    /** {en}
     * @brief Only play on the local side.
     */
    kLocal,
    /** {zh}
     * @brief 仅远端播放。
     */
    /** {en}
     * @brief Only play on the remote side.
     */
    kRemote,
    /** {zh}
     * @brief 本地、远端同时播放。
     */
    /** {en}
     * @brief Play on the local and remote side.
     */
    kLocalAndRemote
};

/** {zh}
 * @type keytype
 * @brief 音乐播放状态。
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief Music playing status.
 */
enum class PlayState {
    /** {zh}
     * @brief 播放中。
     */
    /** {en}
     * @brief Playing.
     */
    kPlaying = 1,
    /** {zh}
     * @brief 暂停中。
     */
    /** {en}
     * @brief Paused.
     */
    kPaused = 2,
    /** {zh}
     * @brief 已停止。
     */
    /** {en}
     * @brief Stopped.
     */
    kStoped = 3,
    /** {zh}
     * @brief 播放失败。
     */
    /** {en}
     * @brief Failed to play.
     */
    kFailed = 4,
    /** {zh}
     * @brief 播放结束。
     */
    /** {en}
     * @brief Finished.
     */
    kFinished = 5,
};

/** {zh}
 * @type keytype
 * @brief 歌词格式类型。
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief The lyrics type.
 */
enum class LyricStatus {
    /** {zh}
     * @brief 无歌词。
     */
    /** {en}
     * @brief No lyrics.
     */
    kNone = 0,
    /** {zh}
     * @brief KRC 歌词。
     */
    /** {en}
     * @brief KRC lyrics.
     */
    kKRC = 1,
    /** {zh}
     * @brief LRC 歌词。
     */
    /** {en}
     * @brief LRC lyrics.
     */
    kLRC = 2,
    /** {zh}
     * @brief KRC 歌词和 LRC 歌词均有。
     */
    /** {en}
     * @brief KRC and LRC lyrics.
     */
    kKRCAndLRC = 3
};

/** {zh}
 * @type keytype
 * @brief 歌词文件类型。
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief The lyrics file's format.
 */
enum class DownloadLyricType {
    /** {zh}
     * @brief KRC 歌词文件。
     */
    /** {en}
     * @brief KRC lyrics file.
     */
    kKRC,
    /** {zh}
     * @brief LRC 歌词文件。
     */
    /** {en}
     * @brief LRC lyrics file.
     */
    kLRC
};



/** {zh}
 * @type keytype
 * @brief 歌曲数据。
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief Music information.
 */
struct MusicInfo
{
    /** {zh}
     * @brief 音乐 ID。
     */
    /** {en}
     * @brief Music ID.
     */
    const char*  music_id;
    /** {zh}
     * @brief 音乐名称。
     */
    /** {en}
     * @brief Music name.
     */
    const char*  music_name;
    /** {zh}
     * @brief 歌手。
     */
    /** {en}
     * @brief Singer.
     */
    const char*  singer;
    /** {zh}
     * @brief 版权商 ID。
     */
    /** {en}
     * @brief Vendor ID.
     */
    const char*  vendor_id;
    /** {zh}
     * @brief 版权商名称。
     */
    /** {en}
     * @brief Vendor name.
     */
    const char* vendor_name;
    /** {zh}
     * @brief 最新更新时间戳，单位为毫秒。
     */
    /** {en}
     * @brief Latest update timestamp in milliseconds.
     */
    int64_t update_timestamp;
    /** {zh}
     * @brief 封面地址。
     */
    /** {en}
     * @brief The URL of the music cover.
     */
    const char*  poster_url;
    /** {zh}
     * @brief 歌词格式类型，参看 LyricStatus{@link #LyricStatus}。
     */
    /** {en}
     * @brief The lyrics type. See LyricStatus{@link #LyricStatus}.
     */
    LyricStatus lyric_status;
    /** {zh}
     * @brief 歌曲长度，单位为毫秒。
     */
    /** {en}
     * @brief The length of the song in milliseconds.
     */
    int duration;
    /** {zh}
     * @brief 歌曲是否支持打分。
     */
    /** {en}
     * @brief Whether the song supports scoring.
     */
    bool enable_score;
    /** {zh}
     * @brief 歌曲高潮片段开始时间，单位为毫秒。
     */
    /** {en}
     * @brief The starting time of the climax part in milliseconds.
     */
    int climax_start_time;
    /** {zh}
     * @brief 歌曲高潮片段停止时间，单位为毫秒。
     */
    /** {en}
     * @brief The ending time of the climax part in milliseconds.
     */
     int climax_stop_time;

};

/** {zh}
 * @type keytype
 * @brief 热榜歌曲数据。
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief Hot music information.
 */
struct HotMusicInfo {
    /** {zh}
     * @brief 榜单类别，参看 MusicHotType{@link #MusicHotType}。
     */
    /** {en}
     * @brief Hot music type. See MusicHotType{@link #MusicHotType}.
     */
    MusicHotType hot_type;
    /** {zh}
     * @brief 热榜名称。
     */
    /** {en}
     * @brief Hot list name.
     */
    const char* hot_name;
    /** {zh}
     * @brief 歌曲数据，参看 MusicInfo{@link #MusicInfo}。
     */
    /** {en}
     * @brief Music information. See MusicInfo{@link #MusicInfo}.
     */
    MusicInfo* musics;
    /** {zh}
     * @brief 歌曲列表的数量。
     */
    /** {en}
     * @brief The number of music in the list.
     */
    int music_count;
};

/** {zh}
 * @type keytype
 * @brief 下载文件类型。
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief Download file type.
 */
enum DownloadFileType {
    /** {zh}
     * @brief 音频文件。
     */
    /** {en}
     * @brief Audio file.
     */
    kDownloadFileTypeMusic = 1,
    /** {zh}
     * @brief KRC 歌词文件。
     */
    /** {en}
     * @brief KRC lyrics file.
     */
    kDownloadFileTypeKRC = 2,
    /** {zh}
     * @brief LRC 歌词文件。
     */
    /** {en}
     * @brief LRC lyrics file.
     */
    kDownloadFileTypeLRC = 3,
    /** {zh}
     * @brief MIDI 文件。
     */
    /** {en}
     * @brief MIDI file.
     */
    kDownloadFileTypeMIDI = 4

} ;

/** {zh}
 * @type keytype
 * @brief 歌曲下载信息。
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief Download music information.
 */
struct DownloadResult {
    /** {zh}
     * @brief 文件存放路径。
     */
    /** {en}
     * @brief Download file path.
     */
    const char* local_file_path;
    /** {zh}
     * @brief 音乐 ID。
     */
    /** {en}
     * @brief Music ID.
     */
    const char* music_id;
    /** {zh}
     * @brief 下载文件类型，参看 DownloadFileType{@link #DownloadFileType}。
     */
    /** {en}
     * @brief Download file type. See DownloadFileType{@link #DownloadFileType}.
     */
    DownloadFileType type;
};


/** {zh}
 * @type errorcode
 * @brief KTV 错误码。
 */
/** {en}
 * @hidden currently not available
 * @type errorcode
 * @brief KTV error code.
 */
enum KTVErrorCode {
    /** {zh}
     * @brief 成功。
     */
    /** {en}
     * @brief Success.
     */
    kKTVErrorCodeOK = 0,
    /** {zh}
     * @brief AppID 异常。
     */
    /** {en}
     * @brief Invalid AppID.
     */
    kKTVErrorCodeAppidInValid = -3000,
    /** {zh}
     * @brief 非法参数，传入的参数不正确。
     */
    /** {en}
     * @brief Invalid parameter.
     */
    kKTVErrorCodeParasInValid = -3001,
    /** {zh}
     * @brief 获取歌曲资源失败。
     */
    /** {en}
     * @brief Failed to get music resources.
     */
    kKTVErrorCodeGetMusicFailed = -3002,
    /** {zh}
     * @brief 获取歌词失败。
     */
    /** {en}
     * @brief Failed to get lyrics.
     */
    kKTVErrorCodeGetLyricFailed = -3003,
    /** {zh}
     * @brief 歌曲下架。
     */
    /** {en}
     * @brief The music is removed.
     */
    kKTVErrorCodeMusicTakedown = -3004,
    /** {zh}
     * @brief 歌曲文件下载失败。
     */
    /** {en}
     * @brief Failed to download the music file.
     */
    kKTVErrorCodeMusicDownload = -3005,
    /** {zh}
     * @brief MIDI 文件下载失败。
     */
    /** {en}
     * @brief Failed to download the MIDI file.
     */
    kKTVErrorCodeMidiDownloadFailed = -3006,
    /** {zh}
     * @brief 系统繁忙。
     */
    /** {en}
     * @brief The system is busy.
     */
    kKTVErrorCodeSystemBusy = -3007,
    /** {zh}
     * @brief 网络异常。
     */
    /** {en}
     * @brief Network anomaly.
     */
    kKTVErrorCodeNetwork = -3008,
    /** {zh}
     * @brief KTV 功能未加入房间。
     */
    /** {en}
     * @brief The KTV feature is not added to the room.
     */
    kKTVErrorCodeNotJoinRoom = -3009,
    /** {zh}
     * @brief 解析数据失败。
     */
    /** {en}
     * @brief Failed to parse data.
     */
    kKTVErrorCodeParseData = -3010,
    /** {zh}
     * @hidden
     * @deprecated 从353开始。
     * @brief 下载失败。
     */
    /** {en}
     * @hidden
     * @deprecated since 353.
     * @brief Failed to download.
     */
    kKTVErrorCodeDownload = -3011,
    /** {zh}
     * @brief 已在下载中。
     */
    /** {en}
     * @brief Already downloading.
     */
    kKTVErrorCodeDownloading = -3012,
    /** {zh}
     * @brief 内部错误，联系技术支持人员。
     */
    /** {en}
     * @brief Internal error. Contact the technical support representatives for help.
     */
    kKTVErrorCodeInternalDomain = -3013,
    /** {zh}
     * @brief 下载失败，磁盘空间不足。清除缓存后重试。
     */
    /** {en}
     * @brief Failed to download because of insufficient disk space. Please retry after clearing cache.
     */
    kKTVErrorCodeInsufficientDiskSpace = -3014,
    /** {zh}
     * @brief 下载失败，音乐文件解密失败，联系技术支持人员。
     */
    /** {en}
     * @brief Failed to download because of music decryption failed. Contact the technical support representatives for help.
     */
    kKTVErrorCodeMusicDecryptionFailed = -3015,
    /** {zh}
     * @brief 下载失败，音乐文件重命名失败，请重试。
     */
    /** {en}
     * @brief Failed to download because of music rename failed. Please retry.
     */
    kKTVErrorCodeFileRenameFailed = -3016,
    /** {zh}
     * @brief 下载失败，下载超时，请重试。
     */
    /** {en}
     * @brief Failed to download because of network failure. Please retry.
     */
    kKTVErrorCodeDownloadTimeOut = -3017,
    /** {zh}
     * @brief 清除缓存失败，可能原因是文件被占用或者系统异常，请重试。
     */
    /** {en}
     * @brief Failed to clear cache because the file is occupied or the system is abnormal. Please retry.
     */
    kKTVErrorCodeClearCacheFailed = -3018,
    /** {zh}
     * @brief 取消下载。
     */
    /** {en}
     * @brief Cancel download task.
     */
    kKTVErrorCodeDownloadCanceled = -3019
};

/** {zh}
 * @type keytype
 * @brief KTV 播放器错误码。
 */
/** {en}
 * @hidden currently not available
 * @type keytype
 * @brief KTV player error code.
 */
enum KTVPlayerErrorCode {
    /** {zh}
     * @brief 成功。
     */
    /** {en}
     * @brief Success.
     */
    kKTVPlayerErrorCodeOK = 0,
    /** {zh}
     * @brief 播放错误，请下载后播放。
     */
    /** {en}
     * @brief Failed to play the music. Download first.
     */
    kKTVPlayerErrorCodeFileNotExist = -3020,
    /** {zh}
     * @brief 播放错误，请确认文件播放格式。
     */
    /** {en}
     * @brief Failed to play the music. Check the file's format.
     */
    kKTVPlayerErrorCodeFileError = -3021,
    /** {zh}
     * @brief 播放错误，未进入房间。
     */
    /** {en}
     * @brief Failed to play the music. Join a room first.
     */
    kKTVPlayerErrorCodeNotJoinRoom = -3022,
    /** {zh}
     * @brief 参数错误。
     */
    /** {en}
     * @brief Invalid parameter.
     */
    kKTVPlayerErrorCodeParam = -3023,
    /** {zh}
     * @brief 播放失败，找不到文件或文件打开失败。
     */
    /** {en}
     * @brief Failed to play the music. Invalid path or failed to open the file.
     */
    kKTVPlayerErrorCodeStartError = -3024,
    /** {zh}
     * @brief 混音 ID 异常。
     */
    /** {en}
     * @brief Invalid mixing ID.
     */
    kKTVPlayerErrorCodeMixIdError = -3025,
    /** {zh}
     * @brief 设置播放位置出错。
     */
    /** {en}
     * @brief Invalid position.
     */
    kKTVPlayerErrorCodePositionError = -3026,
    /** {zh}
     * @brief 音量参数不合法，可设置的取值范围为 [0,400]。
     */
    /** {en}
     * @brief Invalid volume.
     */
    kKTVPlayerErrorCodeAudioVolumeError = -3027,
    /** {zh}
     * @brief 不支持此混音类型。
     */
    /** {en}
     * @brief Do not support the mix type.
     */
    kKTVPlayerErrorCodeTypeError = -3028,
    /** {zh}
     * @brief 音调文件不合法。
     */
    /** {en}
     * @brief Invalid pitch.
     */
    kKTVPlayerErrorCodePitchError = -3029,
    /** {zh}
     * @brief 音轨不合法。
     */
    /** {en}
     * @brief Invalid audio track.
     */
    kKTVPlayerErrorCodeAudioTrackError = -3030,
    /** {zh}
     * @brief 混音启动中。
     */
    /** {en}
     * @brief Mixing in process.
     */
    kKTVPlayerErrorCodeStartingError = -3031
};


} // namespace bytertc
