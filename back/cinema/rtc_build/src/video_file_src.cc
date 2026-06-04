#include "video_file_src.h"
#include <iostream>
#include <fstream>
#include "util/util.h"

#ifdef WITH_FFMPEG

extern "C" {
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavcodec/bsf.h>
}

VideoFileSrc::VideoFileSrc(const char* filePath)
{
    AVFormatContext* formatContext = nullptr;
    AVBSFContext* bsfContext = nullptr;
    AVPacket* packet = av_packet_alloc();
    AVPacket* filteredPacket = av_packet_alloc();

    auto cleanup = [&]() {
        if (packet) {
            av_packet_free(&packet);
        }
        if (filteredPacket) {
            av_packet_free(&filteredPacket);
        }
        if (bsfContext) {
            av_bsf_free(&bsfContext);
        }
        if (formatContext) {
            avformat_close_input(&formatContext);
        }
    };

    if (!packet || !filteredPacket) {
        LOG_ERROR("Failed to allocate AVPacket.");
        cleanup();
        return;
    }

    if (avformat_open_input(&formatContext, filePath, nullptr, nullptr) != 0) {
        LOG_ERROR("Error opening the input file: " << filePath);
        cleanup();
        return;
    }

    if (avformat_find_stream_info(formatContext, nullptr) < 0) {
        LOG_ERROR("Error finding stream information.");
        cleanup();
        return;
    }

    int videoStreamIndex = -1;
    AVCodecParameters* codecParams = nullptr;
    for (unsigned int i = 0; i < formatContext->nb_streams; ++i) {
        if (formatContext->streams[i]->codecpar->codec_type == AVMEDIA_TYPE_VIDEO) {
            videoStreamIndex = static_cast<int>(i);
            codecParams = formatContext->streams[i]->codecpar;
            width_ = codecParams->width;
            height_ = codecParams->height;
            AVRational frameRate = formatContext->streams[videoStreamIndex]->avg_frame_rate;
            fps_ = av_q2d(frameRate);
            if (fps_ <= 0.0) {
                frameRate = formatContext->streams[videoStreamIndex]->r_frame_rate;
                fps_ = av_q2d(frameRate);
            }
            if (fps_ <= 0.0) {
                fps_ = 30.0;
            }
            break;
        }
    }

    if (videoStreamIndex == -1 || !codecParams) {
        LOG_ERROR("No video stream found in the input file.");
        cleanup();
        return;
    }

    const AVBitStreamFilter* bsf = av_bsf_get_by_name("h264_mp4toannexb");
    if (!bsf || av_bsf_alloc(bsf, &bsfContext) < 0) {
        LOG_ERROR("Failed to create h264_mp4toannexb bitstream filter.");
        cleanup();
        return;
    }

    if (avcodec_parameters_copy(bsfContext->par_in, codecParams) < 0 ||
        av_bsf_init(bsfContext) < 0) {
        LOG_ERROR("Failed to initialize h264_mp4toannexb bitstream filter.");
        cleanup();
        return;
    }

    while (av_read_frame(formatContext, packet) == 0) {
        if (packet->stream_index != videoStreamIndex) {
            av_packet_unref(packet);
            continue;
        }

        if (av_bsf_send_packet(bsfContext, packet) < 0) {
            av_packet_unref(packet);
            continue;
        }

        while (av_bsf_receive_packet(bsfContext, filteredPacket) == 0) {
            const uint64_t offset = framesBuffer_.size();
            framesBuffer_.insert(
                framesBuffer_.end(),
                filteredPacket->data,
                filteredPacket->data + filteredPacket->size);
            framesOffset_.push_back(offset);
            framesSize_.push_back(filteredPacket->size);
            framesIsKey_.push_back((filteredPacket->flags & AV_PKT_FLAG_KEY) != 0);
            av_packet_unref(filteredPacket);
        }
        av_packet_unref(packet);
    }

    av_bsf_send_packet(bsfContext, nullptr);
    while (av_bsf_receive_packet(bsfContext, filteredPacket) == 0) {
        const uint64_t offset = framesBuffer_.size();
        framesBuffer_.insert(
            framesBuffer_.end(),
            filteredPacket->data,
            filteredPacket->data + filteredPacket->size);
        framesOffset_.push_back(offset);
        framesSize_.push_back(filteredPacket->size);
        framesIsKey_.push_back((filteredPacket->flags & AV_PKT_FLAG_KEY) != 0);
        av_packet_unref(filteredPacket);
    }

    cleanup();

    if (framesOffset_.empty()) {
        LOG_ERROR("No video frames found in the input file.");
        return;
    }

    LOG_INFO("file_name:" << filePath << " total_size:" << framesBuffer_.size()
        << " number_frames:" << framesOffset_.size());
}

#else
VideoFileSrc::VideoFileSrc(const char* infoFilePath, const char* videoFilePath, int width, int height, double fps)
{
    std::ifstream infoFile(infoFilePath, std::ios::in);
    if (!infoFile) {
        LOG_ERROR("Failed to open " << infoFilePath);
        return;
    }

    std::string line;
    while(std::getline(infoFile, line)) {
        std::istringstream iss(line);
        uint64_t offset;
        int size;
        bool isKey;
        iss >> offset >> size >> isKey;
        framesOffset_.push_back(offset);
        framesSize_.push_back(size);
        framesIsKey_.push_back(isKey);
    }

    std::ifstream file(videoFilePath, std::ios::binary);
    if (!file) {
        LOG_ERROR("Failed to open " << videoFilePath);
        return;
    }

    file.seekg(0, std::ios::end);
    std::streampos fileSize = file.tellg();
    file.seekg(0, std::ios::beg);

    framesBuffer_.resize(fileSize);
    if (!file.read(reinterpret_cast<char*>(framesBuffer_.data()), fileSize)) {
        LOG_ERROR("Failed to read the file.");
        return;
    }

    file.close();

    width_ = width;
    height_ = height;
    fps_ = fps;

    LOG_INFO("file_name:" << videoFilePath << " total_size:" << fileSize << " number_frames:" << framesOffset_.size());
}
#endif

VideoFileSrc::~VideoFileSrc()
{
}

void VideoFileSrc::getNextFrame(uint8_t* &data, int &size, bool &isKey)
{
    data = framesBuffer_.data() + framesOffset_[frameIndex_];
    size = framesSize_[frameIndex_];
    isKey = framesIsKey_[frameIndex_];
    
    frameIndex_++;

    if (frameIndex_ >= framesOffset_.size()) {
        frameIndex_ = 0;
    }
}

