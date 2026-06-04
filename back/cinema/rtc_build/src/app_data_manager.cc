#include "app_data_manager.h"
#include "json11.hpp"
#include "util/util.h"
#include <regex>

namespace {
const std::string kNameRegex = "^[a-zA-Z0-9@._-]{1,128}$";

bool validName(const std::string &data) {
	if (data.empty()) {
		return false;
	}
	std::regex exp(kNameRegex);
	return std::regex_match(data, exp);
}
}

AppDataManager::AppDataManager() = default;
AppDataManager::~AppDataManager() = default;

bool AppDataManager::parseRtcSection(const std::string &rtc_json_str) {
	std::string err;
	auto rtcJson = json11::Json::parse(rtc_json_str, err);
	if (rtcJson.is_null()) {
		LOG_WARN("parser rtc json failed: " << err);
		return false;
	}

	m_appData = std::make_shared<StuAppData>();
	m_appData->app_id = rtcJson["app_id"].string_value();
	m_appData->room_id = rtcJson["default_room_id"].string_value();
	m_appData->user_id = rtcJson["default_user_id"].string_value();
	m_appData->rtc_env = rtcJson["rtc_env"].int_value();
	m_appData->enable_video = rtcJson["enable_video"].bool_value();
	if (!rtcJson["enable_video"].is_bool()) {
		m_appData->enable_video = true;
	}
	m_appData->enable_audio = rtcJson["enable_audio"].bool_value();
	if (!rtcJson["enable_audio"].is_bool()) {
		m_appData->enable_audio = true;
	}
	m_appData->stream_priority = 1;

	m_appData->token_server_host = rtcJson["token_server_host"].string_value();
	if (m_appData->token_server_host.empty()) {
		m_appData->token_server_host = "127.0.0.1";
	}
	m_appData->token_server_port = rtcJson["token_server_port"].int_value();
	if (m_appData->token_server_port <= 0) {
		m_appData->token_server_port = 8000;
	}
	m_appData->token_server_path = rtcJson["token_server_path"].string_value();
	if (m_appData->token_server_path.empty()) {
		m_appData->token_server_path = "/api/cinema/get/token";
	}

	auto enc = rtcJson["video_encoder_config"];
	if (!enc.is_null()) {
		auto cfg = std::make_shared<StuVideoEncoderConfig>();
		cfg->width = enc["width"].int_value() > 0 ? enc["width"].int_value() : 1920;
		cfg->height = enc["height"].int_value() > 0 ? enc["height"].int_value() : 1080;
		cfg->fps = enc["fps"].int_value() > 0 ? enc["fps"].int_value() : 30;
		cfg->max_bitrate = enc["max_bitrate"].int_value() > 0 ? enc["max_bitrate"].int_value() : 4000;
		m_appData->video_encoder_config = cfg;
	} else {
		m_appData->video_encoder_config = std::make_shared<StuVideoEncoderConfig>();
	}

	if (m_appData->app_id.empty()) {
		LOG_WARN("rtc.app_id is empty");
		return false;
	}
	if (!validName(m_appData->room_id)) {
		LOG_WARN("rtc.default_room_id is invalid");
		return false;
	}
	if (!validName(m_appData->user_id)) {
		LOG_WARN("rtc.default_user_id is invalid");
		return false;
	}
	return true;
}

bool AppDataManager::loadForStream(
	const std::string &blog_config_file,
	const std::string &video_path,
	const std::string &room_override,
	const std::string &user_override) {
	auto data = bytertc::readFile(blog_config_file.c_str(), "rt");
	if (data.empty()) {
		LOG_ERROR("无法读取配置: " << blog_config_file);
		return false;
	}
	std::string content(reinterpret_cast<const char *>(data.data()), data.size());
	int left = static_cast<int>(content.find_first_of('{'));
	int right = static_cast<int>(content.find_last_of('}'));
	if (left == -1 || right == -1 || right < left) {
		LOG_ERROR("配置文件不是合法 JSON: " << blog_config_file);
		return false;
	}
	content = content.substr(static_cast<size_t>(left), static_cast<size_t>(right - left + 1));

	std::string err;
	auto root = json11::Json::parse(content, err);
	if (!err.empty() || root.is_null()) {
		LOG_ERROR("解析配置文件失败: " << err);
		return false;
	}
	auto rtc = root["rtc"];
	if (rtc.is_null()) {
		LOG_ERROR("配置中缺少 rtc 节点: " << blog_config_file);
		return false;
	}

	std::string rtc_dump = rtc.dump();
	if (!parseRtcSection(rtc_dump)) {
		return false;
	}

	if (video_path.empty()) {
		LOG_ERROR("未指定 MP4 文件路径");
		return false;
	}
	m_appData->video_file = video_path;

	if (!room_override.empty()) {
		if (!validName(room_override)) {
			LOG_WARN("room_id override invalid");
			return false;
		}
		m_appData->room_id = room_override;
	}
	if (!user_override.empty()) {
		if (!validName(user_override)) {
			LOG_WARN("user_id override invalid");
			return false;
		}
		m_appData->user_id = user_override;
	}

	if (!m_appData->enable_video) {
		LOG_ERROR("rtc.enable_video 必须为 true");
		return false;
	}
	return true;
}

AppDataManager *AppDataManager::instance() {
	static AppDataManager appDataMgr;
	return &appDataMgr;
}
