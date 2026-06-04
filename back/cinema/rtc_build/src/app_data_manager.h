#include <memory>
#include <string>

struct StuVideoEncoderConfig {
	int width = 1920;
	int height = 1080;
	int fps = 30;
	int max_bitrate = 4000;  // kbps, 4 Mbps
};

struct StuAppData {
	std::string app_id;
	std::string room_id;
	std::string user_id;
	int rtc_env = 0;
	bool enable_video = true;
	bool enable_audio = true;
	int stream_priority = 1;
	std::string video_file;
	std::string token_server_host = "127.0.0.1";
	int token_server_port = 8000;
	std::string token_server_path = "/api/cinema/get/token";
	std::shared_ptr<StuVideoEncoderConfig> video_encoder_config;
};

class AppDataManager {
public:
	AppDataManager();
	~AppDataManager();
	bool loadForStream(
		const std::string &blog_config_file,
		const std::string &video_path,
		const std::string &room_override,
		const std::string &user_override);
	std::shared_ptr<StuAppData> getAppData() { return m_appData; }
	static AppDataManager *instance();

private:
	bool parseRtcSection(const std::string &rtc_json_str);
	std::shared_ptr<StuAppData> m_appData;
};
