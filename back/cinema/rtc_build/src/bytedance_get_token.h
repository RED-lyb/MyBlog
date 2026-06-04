#pragma once
#include <string>
#include "util/util.h" //日志
#include "util/httplib.h"
#include "json11.hpp"
bool token_requset(std::string room_id ,std::string user_id,std::string &token);