#include <atomic>
#include <chrono>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <fcntl.h>
#include <iostream>
#include <string>
#include <thread>
#include <unistd.h>
#include <sys/file.h>

#include "app_data_manager.h"
#include "rtc_engine_wrapper.h"
#include "util/util.h"
#include <signal.h>

namespace {
const char *kDefaultBlogConfig = "../../config/config_back.json";
const char *kStreamLockFile = "stream.lock";
std::atomic<bool> g_bExit(false);
int g_streamLockFd = -1;

bool acquireStreamLock() {
	g_streamLockFd = open(kStreamLockFile, O_CREAT | O_RDWR, 0644);
	if (g_streamLockFd < 0) {
		return false;
	}
	struct flock lock {};
	lock.l_type = F_WRLCK;
	lock.l_whence = SEEK_SET;
	if (fcntl(g_streamLockFd, F_SETLK, &lock) != 0) {
		close(g_streamLockFd);
		g_streamLockFd = -1;
		return false;
	}
	const std::string pid_str = std::to_string(getpid());
	(void)write(g_streamLockFd, pid_str.c_str(), pid_str.size());
	return true;
}

void releaseStreamLock() {
	if (g_streamLockFd >= 0) {
		close(g_streamLockFd);
		g_streamLockFd = -1;
		unlink(kStreamLockFile);
	}
}

void printUsage(const char *prog) {
	std::cerr << "用法: " << prog
	          << " <video.mp4> [room_id] [user_id] [config_back.json]\n"
	          << "  默认读取博客配置: " << kDefaultBlogConfig << " 中的 rtc 节点\n";
}

void exitAppSignalCallback(int signal) {
	(void)signal;
	// 仅在主线程中销毁 RTC，避免在信号处理函数里调用 SDK 导致死锁或进程残留
	g_bExit = true;
}

void registerSignals() {
	signal(SIGINT, &exitAppSignalCallback);
	signal(SIGTERM, &exitAppSignalCallback);
}
}

int main(int argc, char *argv[]) {
	registerSignals();
	bytertc::setCurrentDir(bytertc::getExePath());
	// 日志重定向到文件时默认全缓冲，易导致“卡在 do loop begin”的假象
	setvbuf(stdout, nullptr, _IOLBF, 0);

	// SDK 特效库会向 stderr 打印 “super-user” 提示，与推文件无关；日志走 stdout
	int null_fd = open("/dev/null", O_WRONLY);
	if (null_fd >= 0) {
		dup2(null_fd, STDERR_FILENO);
		close(null_fd);
	}

	if (argc < 2) {
		printUsage(argv[0]);
		return 1;
	}

	const std::string video_path = argv[1];
	const std::string room_override = argc > 2 ? argv[2] : "";
	const std::string user_override = argc > 3 ? argv[3] : "";
	const std::string blog_config = argc > 4 ? argv[4] : kDefaultBlogConfig;

	LOG_INFO("MP4: " << video_path << " 配置: " << blog_config);

	auto appDataIns = AppDataManager::instance();
	if (!appDataIns->loadForStream(blog_config, video_path, room_override, user_override)) {
		printUsage(argv[0]);
		return 1;
	}

	if (!acquireStreamLock()) {
		LOG_ERROR("已有 rtccli 推流进程在运行，请先停止后再启动");
		return 1;
	}

	if (RTCVideoEngineWrapper::instance()->init() != 0) {
		releaseStreamLock();
		return 1;
	}

	// joinRoom 可能在调用线程上长期阻塞，但 SDK 会在其它线程完成进房/推流；
	// 主线程不能卡在这里，否则播完后无法检测 isPlaybackFinished() 并退出。
	auto *engine = RTCVideoEngineWrapper::instance();
	std::thread join_worker([engine]() {
		const int ret = engine->joinRoom();
		LOG_INFO("joinRoom 工作线程结束 ret=" << ret);
	});

	LOG_INFO("推流中，影片播完将自动退出（也可 Ctrl+C 提前结束）");
	const auto deadline = std::chrono::steady_clock::now()
		+ std::chrono::milliseconds(engine->maxPlaybackWaitMs());
	while (!g_bExit && !engine->isPlaybackFinished()) {
		if (std::chrono::steady_clock::now() >= deadline) {
			LOG_WARN("播放 watchdog 超时，强制结束推流");
			engine->forceEndPlayback();
			break;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(100));
	}
	if (g_bExit) {
		LOG_INFO("收到停止信号，正在退出推流...");
		engine->forceEndPlayback();
	} else {
		LOG_INFO("影片已播完，正在退出推流...");
	}
	// markPlaybackComplete 已停定时器并 unpublish；不再调用 destory()：
	// SDK 在子进程里 destroy/leaveRoom 常阻塞数秒，且不宜在非主线程调用。
	// _exit 由内核回收本进程全部内存/句柄，不存在“泄漏到其他进程”的问题。
	if (join_worker.joinable()) {
		join_worker.detach();
	}
	releaseStreamLock();
	LOG_INFO("推流进程退出");
	std::cout.flush();
	_exit(0);
}
