#include "util.h"
#include <cassert>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <pthread.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>

namespace bytertc {
bool fileExisted( const std::string& path ) {
    struct stat _f_info;
    if ( stat(path.c_str(), &_f_info) != 0 ) return false;
    return !(bool)(_f_info.st_mode & S_IFDIR);
}

std::string& trim(std::string& text) {
    if (!text.empty()) {
        text.erase(0, text.find_first_not_of((" \n\r\t")));
        text.erase(text.find_last_not_of(" \n\r\t") + 1);
    }
    return text;    
}

bool StringStart(const std::string& s, const std::string& p) {
    if ( s.size() >= p.size() ) {
        for ( size_t i = 0; i < p.size(); ++i ) {
            if ( s[i] != p[i] ) return false;
        }
        return true;
    }
    return false;
}
size_t getFileSize(FILE* file) {
    fseek(file, 0, SEEK_END);
    size_t read_len = ftell(file);
    fseek(file, 0, SEEK_SET);
    return read_len;
}

size_t getFileSize(const char* filePath) {
    FILE* file = fopen(filePath, "rb");
    if (file == nullptr) {
        return 0;
    }
    size_t size = getFileSize(file);
    fclose(file);
    return size;
}

std::vector<unsigned char> readFile(const char* file_path,const char *mode) {
    FILE* file = fopen(file_path, mode);
    std::vector<uint8_t> result;
    if (file == nullptr) {
        return result;
    }

    size_t fileSize = getFileSize(file);
    if (fileSize != 0) {
        result.resize(fileSize);
        size_t n = fread(&result[0], 1, fileSize, file);
        assert(n <= fileSize);
        if (n != fileSize) {
            result.resize(n);
        }
    }
    const size_t read_len = 1024;
    char buf[read_len];
    for (;;) {
        size_t n = fread(buf, 1, read_len, file);
        result.insert(result.end(), buf, buf + n);
        if (n < read_len) {
            break;
        }
    }
    fclose(file);
    return result;
}

long long getCurrentMillisecs() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
}

void printLog(const std::string & str) {
	std::cout << str;
	std::cout.flush();
}

unsigned long getCurrentThreadId() {
	return pthread_self();
}

void printHelpAndExit()
{
	LOG_INFO("Please check if the 'config.json' file parameters are correct!");
	exit(0);
}

void setCurrentDir(const std::string & str) {
	chdir(str.c_str());
}

std::string getFileName(const std::string & filePath) {
	auto index = filePath.rfind("/");
	std::string fileName = filePath;
	if (index != std::string::npos) {
		fileName = filePath.substr(index + 1, filePath.size() - index -1);
	}
	return fileName;
}

std::string getExePath()
{
	char chPath[256] = { 0 };
	const int n = readlink("/proc/self/exe", chPath, sizeof(chPath) - 1);
	if (n <= 0) {
		return std::string();
	}
	char *p = strrchr(chPath, '/');
	if (p != nullptr) {
		*p = '\0';
	}
	return std::string(chPath);
}

std::string getCurrentTimeStr() {
	struct timeval tv;
	gettimeofday(&tv, NULL);
	time_t t = time(NULL);
	struct tm time_info;
	localtime_r(&t, &time_info);
	std::stringstream ss;
	ss << std::setw(2) << std::setfill('0') << time_info.tm_hour << ":"
	   << std::setw(2) << std::setfill('0') << time_info.tm_min << ":"
	   << std::setw(2) << std::setfill('0') << time_info.tm_sec << "."
	   << std::setw(3) << std::setfill('0') << (tv.tv_usec / 1000);
	return ss.str();
}

int safeStrToInt(const std::string &str) 
{
	if (str.empty()) return 0;
	if (isdigit(str.front())) {
		return std::stoi(str);
	}
	return 0;
}

}
