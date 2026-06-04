#pragma once
#include <cstdint>
#include <vector>

typedef struct FrameInfo_ {
    uint64_t offset;
    int size;
    bool isKey;
} FrameInfo;

class VideoFileSrc {
public:
    VideoFileSrc() = delete;
#ifdef WITH_FFMPEG
    VideoFileSrc(const char* fname);
#else
    VideoFileSrc(const char* infoFilePath, const char* videoFilePath, int width, int height, double fps);
#endif
    ~VideoFileSrc();
    void getNextFrame(uint8_t* &data, int &size, bool &isKey);
    std::vector<uint8_t> getEntireBuffer() const { return framesBuffer_; };
    std::vector<uint64_t> getFramesOffset() const { return framesOffset_; }
    std::vector<int> getFramesSize() const { return framesSize_; }
    std::vector<bool> getFramesIsKey() const { return framesIsKey_; }
    void seekToBegin() { frameIndex_ = 0; }
    int width() const { return width_; }
    int height() const { return height_; }
    double fps() const { return fps_; }
    int index() const { return frameIndex_; }
    int totalFrames() const { return framesOffset_.size(); }
    int sizeInByte() const { return framesBuffer_.size(); }

private:

    std::vector<uint8_t> framesBuffer_;
    std::vector<uint64_t> framesOffset_;
    std::vector<int> framesSize_;
    std::vector<bool> framesIsKey_;
    
    int frameIndex_ = 0;
    int width_ = 0;
    int height_ = 0;
    double fps_ = 0.0;
};