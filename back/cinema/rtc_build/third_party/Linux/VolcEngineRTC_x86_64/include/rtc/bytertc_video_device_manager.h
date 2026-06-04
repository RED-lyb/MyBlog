/*
 * Copyright (c) 2020 The VolcEngineRTC project authors. All Rights Reserved.
 * @brief VolcEngineRTC Video Device Manager
*/

#pragma once

#include "bytertc_audio_device_manager.h"

namespace bytertc {

/** {zh}
 * @type api
 * @region 引擎管理
 * @brief 视频设备相关的信息
 */
/** {en}
 * @type api
 * @region  engine management
 * @brief  Video equipment related information
 */
class IVideoDeviceCollection : public IDeviceCollection {
public:
    /** {zh}
     * @hidden constructor/destructor
     * @brief 构造函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief constructor
     */
    IVideoDeviceCollection() {};
    /** {zh}
     * @type api
     * @region 引擎管理
     * @brief 获取当前系统内视频设备数量
     * @return 视频设备数量
     */
    /** {en}
     * @type api
     * @region engine management
     * @brief Get the number of video devices in the current system
     * @return Number of video devices
     */
    virtual int getCount() override {return 0;};
    /** {zh}
     * @type api
     * @region 引擎管理
     * @brief 根据索引号，获取设备信息
     * @param [in] index 设备索引号，从 0 开始，注意需小于 getCount{@link #IVideoDeviceCollection#getCount} 返回值。
     * @param [out] device_name 设备名称
     * @param [out] device_id 设备 ID
     * @return  <br>
     *        + 0：方法调用成功  <br>
     *        + !0：方法调用失败  <br>
     */
    /** {en}
     * @type api
     * @region Engine management
     * @brief According to the index number, get device information
     * @param  [in] index Device index number, starting from 0, note that it must be less than the return value of getCount{@link #IVideoDeviceCollection#getCount}.
     * @param  [out] device_name device name
     * @param  [out] device_id device ID
     * @return   <br>
     *         + 0: Success. <br>
     *         +! 0: failure <br>
     */
    virtual int getDevice(int index, char device_name[MAX_DEVICE_ID_LENGTH], char device_id[MAX_DEVICE_ID_LENGTH]) override {return 0;};
    /** {zh}
     * @type api
     * @region 引擎管理
     * @brief 释放当前 IVideoDeviceCollection{@link #IVideoDeviceCollection} 对象占用的资源。
     * @notes 不需要返回视频设备相关信息列表时应该调用本方法释放相关资源。
     */
    /** {en}
     * @type api
     * @region  engine management
     * @brief  Releases the resources occupied by the current IVideoDeviceCollection{@link #IVideoDeviceCollection} object.
     * @notes This method should be called to release related resources when you do not need to return a list of video device related information.
     */
    virtual void release()override {};
    /** {zh}
     * @type api
     * @region 引擎管理
     * @brief 根据索引号，获取设备信息
     * @param [in] index 设备索引号，从 0 开始，注意需小于 getCount{@link #IVideoDeviceCollection#getCount} 返回值。
     * @param [out] video_device_info 设备信息
     * @return  <br>
     *        + 0：方法调用成功  <br>
     *        + !0：方法调用失败  <br>
     */
    /** {en}
     * @type api
     * @region Engine management
     * @brief Get device information according to the 
     * @param  [in] index Device index, starting from 0. It must be less than the return value of getCount{@link #IVideoDeviceCollection#getCount}.
     * @param  [out] video_device_info Device information
     * @return   <br>
     *         + 0: Success. <br>
     *         +! 0: failure <br>
     */
    virtual int getDevice(int index, VideoDeviceInfo* video_device_info) = 0;
protected:
    /** {zh}
     * @hidden constructor/destructor
     * @brief 析构函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Destructor
     */
    virtual ~IVideoDeviceCollection() {};
};

/** {zh}
 * @type api
 * @region 视频设备管理
 * @brief 主要用于枚举、设置视频采集设备
 */
/** {en}
 * @type api
 * @region Video Facility Management
 * @brief Mainly used to enumerate and set up video capture devices
 */
class IVideoDeviceManager {
public:
    /** {zh}
     * @hidden constructor/destructor
     * @brief 构造函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Constructor
     */
    IVideoDeviceManager() {
    }
    /** {zh}
     * @type api
     * @region 视频设备管理
     * @brief 获取当前系统内视频采集设备列表。
     * @return 包含系统中所有视频采集设备的列表，参看 IVideoDeviceCollection{@link #IVideoDeviceCollection}。
     * 等待超时后会返回空列表。超时时间默认为 10 s。建议通过 onVideoDeviceStateChanged{@link #IRTCVideoEventHandler#onVideoDeviceStateChanged} 监听到 `kMediaDeviceListUpdated` 后，再次调用本接口获取。
     * @notes 你可以在收到 onVideoDeviceStateChanged{@link #IRTCVideoEventHandler#onVideoDeviceStateChanged} 了解设备变更后，重新调用本接口以获得新的设备列表。
     */
    /** {en}
     * @type api
     * @region  Video Facility Management
     * @brief  Get a list of video capture devices in the current system.
     * @return  Contains a list of all video capture devices in the system. See IVideoDeviceCollection{@link #IVideoDeviceCollection}.
     * If a time-out occurs, it returns an empty list. By default, the time-out duration is set to 10 seconds. We recommend to call this API once you get notification of `kMediaDeviceListUpdated` via onVideoDeviceStateChanged{@link #IRTCVideoEventHandler#onVideoDeviceStateChanged}.
     * @notes When receiving onVideoDeviceStateChanged{@link #IRTCVideoEventHandler#onVideoDeviceStateChanged} for device change, you can call this API to get the latest list of audio playback devices.
     */
    virtual IVideoDeviceCollection* enumerateVideoCaptureDevices() = 0;
    /** {zh}
     * @type api
     * @region 视频设备管理
     * @brief 设置当前视频采集设备
     * @param [in] device_id 视频设备 ID，可以通过 enumerateVideoCaptureDevices{@link #IVideoDeviceManager#enumerateVideoCaptureDevices} 获取
     * @return  <br>
     *        + 0：方法调用成功  <br>
     *        + !0：方法调用失败  <br>
     */
    /** {en}
     * @type api
     * @region  Video Facility Management
     * @brief  Set the current video capture device
     * @param  [in] device_id Video device ID, which can be obtained through enumerateVideoCaptureDevices{@link #IVideoDeviceManager#enumerateVideoCaptureDevices}
     * @return   <br>
     *         + 0: Success. <br>
     *         +! 0: failure <br>
     */
    virtual int setVideoCaptureDevice(const char device_id[MAX_DEVICE_ID_LENGTH]) = 0;
    /** {zh}
     * @type api
     * @region 视频设备管理
     * @brief 获取当前 SDK 正在使用的视频采集设备信息
     * @param [out] device_id 视频设备 ID。此参数同时是入参和出参。
     * @return  <br>
     *        + 0：方法调用成功  <br>
     *        + !0：方法调用失败  <br>
     */
    /** {en}
     * @type api
     * @region Video Facility Management
     * @brief Get the video capture device information currently used by the SDK
     * @param  [out] device_id Device ID. The parameter is both input parameter and output parameter.
     * @return   <br>
     *         + 0: Success. <br>
     *         +! 0: failure <br>
     */
    virtual int getVideoCaptureDevice(char device_id[MAX_DEVICE_ID_LENGTH]) = 0;

    /** {zh}
     * @hidden constructor/destructor
     * @brief 析构函数
     */
    /** {en}
     * @hidden constructor/destructor
     * @brief Destructor
     */
    virtual ~IVideoDeviceManager() {
    }
};


}  // namespace bytertc
