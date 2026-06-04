#include "mp4_audio_src.h"
#include "util/util.h"

#ifdef WITH_FFMPEG

extern "C" {
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavutil/version.h>
#include <libswresample/swresample.h>
#if LIBAVCODEC_VERSION_MAJOR >= 59
#include <libavutil/channel_layout.h>
#endif
}

Mp4AudioSrc::Mp4AudioSrc(const char *filePath) {
	AVFormatContext *formatContext = nullptr;
	AVCodecContext *codecContext = nullptr;
	SwrContext *swrContext = nullptr;
	AVPacket *packet = av_packet_alloc();
	AVFrame *frame = av_frame_alloc();

	auto cleanup = [&]() {
		if (frame) {
			av_frame_free(&frame);
		}
		if (packet) {
			av_packet_free(&packet);
		}
		if (codecContext) {
			avcodec_free_context(&codecContext);
		}
		if (swrContext) {
			swr_free(&swrContext);
		}
		if (formatContext) {
			avformat_close_input(&formatContext);
		}
	};

	if (!packet || !frame) {
		LOG_ERROR("Mp4AudioSrc: 分配 FFmpeg 结构失败");
		cleanup();
		return;
	}

	if (avformat_open_input(&formatContext, filePath, nullptr, nullptr) != 0) {
		LOG_WARN("Mp4AudioSrc: 无法打开文件 " << filePath);
		cleanup();
		return;
	}
	if (avformat_find_stream_info(formatContext, nullptr) < 0) {
		LOG_WARN("Mp4AudioSrc: 无法读取流信息");
		cleanup();
		return;
	}

	int audioStreamIndex = -1;
	for (unsigned int i = 0; i < formatContext->nb_streams; ++i) {
		if (formatContext->streams[i]->codecpar->codec_type == AVMEDIA_TYPE_AUDIO) {
			audioStreamIndex = static_cast<int>(i);
			break;
		}
	}
	if (audioStreamIndex < 0) {
		LOG_WARN("Mp4AudioSrc: 文件中无音频轨 " << filePath);
		cleanup();
		return;
	}

	AVCodecParameters *codecpar = formatContext->streams[audioStreamIndex]->codecpar;
	const AVCodec *codec = avcodec_find_decoder(codecpar->codec_id);
	if (!codec) {
		LOG_WARN("Mp4AudioSrc: 不支持的音频编码");
		cleanup();
		return;
	}

	codecContext = avcodec_alloc_context3(codec);
	if (!codecContext || avcodec_parameters_to_context(codecContext, codecpar) < 0) {
		LOG_WARN("Mp4AudioSrc: 音频解码器初始化失败");
		cleanup();
		return;
	}
	if (avcodec_open2(codecContext, codec, nullptr) < 0) {
		LOG_WARN("Mp4AudioSrc: 无法打开音频解码器");
		cleanup();
		return;
	}

#if LIBAVCODEC_VERSION_MAJOR >= 59
	AVChannelLayout outLayout = AV_CHANNEL_LAYOUT_STEREO;
	AVChannelLayout inLayout = {};
	if (codecContext->ch_layout.nb_channels > 0) {
		if (av_channel_layout_copy(&inLayout, &codecContext->ch_layout) < 0) {
			LOG_WARN("Mp4AudioSrc: 无法复制输入声道布局");
			cleanup();
			return;
		}
	} else if (codecpar->ch_layout.nb_channels > 0) {
		if (av_channel_layout_copy(&inLayout, &codecpar->ch_layout) < 0) {
			LOG_WARN("Mp4AudioSrc: 无法复制流声道布局");
			cleanup();
			return;
		}
	} else {
		// FFmpeg 7+ 中 av_channel_layout_default 返回 void
		av_channel_layout_default(&inLayout, 2);
	}
	if (swr_alloc_set_opts2(
			&swrContext,
			&outLayout, AV_SAMPLE_FMT_S16, kSampleRate,
			&inLayout, codecContext->sample_fmt, codecContext->sample_rate,
			0, nullptr) < 0) {
		av_channel_layout_uninit(&inLayout);
		LOG_WARN("Mp4AudioSrc: 重采样器分配失败");
		cleanup();
		return;
	}
	av_channel_layout_uninit(&inLayout);
#else
	int64_t inLayout = codecContext->channel_layout;
	if (!inLayout) {
		inLayout = av_get_default_channel_layout(codecContext->channels);
	}
	swrContext = swr_alloc_set_opts(
		nullptr,
		AV_CH_LAYOUT_STEREO,
		AV_SAMPLE_FMT_S16,
		kSampleRate,
		inLayout,
		codecContext->sample_fmt,
		codecContext->sample_rate,
		0,
		nullptr);
#endif
	if (!swrContext || swr_init(swrContext) < 0) {
		LOG_WARN("Mp4AudioSrc: 重采样初始化失败");
		cleanup();
		return;
	}

	auto appendFrame = [&](AVFrame *decoded) {
		const int outSamples = swr_get_out_samples(swrContext, decoded->nb_samples);
		if (outSamples <= 0) {
			return;
		}
		const int bufSize = av_samples_get_buffer_size(
			nullptr, kChannels, outSamples, AV_SAMPLE_FMT_S16, 1);
		if (bufSize <= 0) {
			return;
		}
		std::vector<uint8_t> buf(static_cast<size_t>(bufSize));
		uint8_t *outData[1] = { buf.data() };
		const int converted = swr_convert(
			swrContext, outData, outSamples,
			const_cast<const uint8_t **>(decoded->data), decoded->nb_samples);
		if (converted > 0) {
			const int bytes = converted * kChannels * static_cast<int>(sizeof(int16_t));
			pcm_.insert(pcm_.end(), buf.begin(), buf.begin() + bytes);
		}
	};

	while (av_read_frame(formatContext, packet) == 0) {
		if (packet->stream_index != audioStreamIndex) {
			av_packet_unref(packet);
			continue;
		}
		if (avcodec_send_packet(codecContext, packet) < 0) {
			av_packet_unref(packet);
			continue;
		}
		while (avcodec_receive_frame(codecContext, frame) == 0) {
			appendFrame(frame);
		}
		av_packet_unref(packet);
	}

	avcodec_send_packet(codecContext, nullptr);
	while (avcodec_receive_frame(codecContext, frame) == 0) {
		appendFrame(frame);
	}

	if (swrContext) {
		while (true) {
			const int outCap = swr_get_out_samples(swrContext, 0);
			if (outCap <= 0) {
				break;
			}
			const int bufSize = av_samples_get_buffer_size(
				nullptr, kChannels, outCap, AV_SAMPLE_FMT_S16, 1);
			if (bufSize <= 0) {
				break;
			}
			std::vector<uint8_t> buf(static_cast<size_t>(bufSize));
			uint8_t *outData[1] = { buf.data() };
			const int converted = swr_convert(
				swrContext, outData, outCap, nullptr, 0);
			if (converted <= 0) {
				break;
			}
			const int bytes = converted * kChannels * static_cast<int>(sizeof(int16_t));
			pcm_.insert(pcm_.end(), buf.begin(), buf.begin() + bytes);
		}
	}

	cleanup();

	if (pcm_.empty()) {
		LOG_WARN("Mp4AudioSrc: 未解码到音频数据");
		return;
	}

	const size_t remainder = pcm_.size() % static_cast<size_t>(kBytesPer10Ms);
	if (remainder != 0) {
		pcm_.resize(pcm_.size() + (static_cast<size_t>(kBytesPer10Ms) - remainder), 0);
	}
	total_chunks_ = static_cast<int>(pcm_.size() / static_cast<size_t>(kBytesPer10Ms));
	valid_ = total_chunks_ > 0;
	LOG_INFO("Mp4AudioSrc: 已加载 " << total_chunks_ << " 个 10ms 音频块 ("
		<< (pcm_.size() / 1024) << " KB PCM)");
}

const uint8_t *Mp4AudioSrc::chunkData(int chunkIndex) const {
	if (!valid_ || total_chunks_ <= 0) {
		return nullptr;
	}
	const int idx = chunkIndex % total_chunks_;
	const size_t offset = static_cast<size_t>(idx) * static_cast<size_t>(kBytesPer10Ms);
	if (offset + static_cast<size_t>(kBytesPer10Ms) > pcm_.size()) {
		return nullptr;
	}
	return pcm_.data() + offset;
}

#else

Mp4AudioSrc::Mp4AudioSrc(const char *) {}
const uint8_t *Mp4AudioSrc::chunkData(int) const { return nullptr; }

#endif
