#pragma once

#include <cstdint>
#include <vector>

/** 从 MP4 解码音频为 RTC 所需格式：48kHz 立体声 PCM S16，按 10ms 分块 */
class Mp4AudioSrc {
public:
	static const int kSampleRate = 48000;
	static const int kChannels = 2;
	static const int kBytesPer10Ms = kSampleRate * kChannels * 2 / 100; // 1920

	explicit Mp4AudioSrc(const char *filePath);
	bool valid() const { return valid_; }
	int totalChunks() const { return total_chunks_; }
	const uint8_t *chunkData(int chunkIndex) const;
	const std::vector<uint8_t> &pcm() const { return pcm_; }
	int chunkSize() const { return kBytesPer10Ms; }

private:
	bool valid_ = false;
	std::vector<uint8_t> pcm_;
	int total_chunks_ = 0;
};
