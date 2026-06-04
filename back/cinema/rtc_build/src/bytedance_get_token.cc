#include "bytedance_get_token.h"
#include "app_data_manager.h"

bool token_requset(std::string room_id, std::string user_id, std::string &token) {
    token.clear();
    auto appData = AppDataManager::instance()->getAppData();
    if (!appData) {
        LOG_ERROR("AppData 未初始化");
        return false;
    }
    std::string host = appData->token_server_host.empty() ? "127.0.0.1" : appData->token_server_host;
    int port = appData->token_server_port > 0 ? appData->token_server_port : 8000;
    std::string path = appData->token_server_path.empty() ? "/api/cinema/get/token" : appData->token_server_path;

    httplib::Client cli(host.c_str(), port);
    json11::Json json_body = json11::Json::object{
        {"room_id", room_id},
        {"user_id", user_id}
    };
    std::string body = json_body.dump();
    auto res = cli.Post(path.c_str(), body, "application/json");
    if (!res) {
        LOG_ERROR("请求失败：无法连接 Token 服务 " << host << ":" << port << path);
        return false;
    }
    std::string err;
    std::string result = "未知异常";
    json11::Json response = json11::Json::parse(res->body, err);
    if (!err.empty()) {
        result = "服务器json数据返回异常";
    } else {
        if (response["message"].string_value().empty()) {
            result = "消息字段为空";
        } else {
            result = response["message"].string_value();
        }
    }
    if (res->status != 200) {
        LOG_ERROR("状态码：" << res->status << "，响应消息：" << result);
        return false;
    }
    if (response["data"].string_value().empty()) {
        result = "token字段为空";
        LOG_ERROR("状态码：" << res->status << "，响应消息：" << result);
        return false;
    }
    token = response["data"].string_value();
    LOG_INFO("状态码：" << res->status << "，响应消息：" << result);
    return true;
}
