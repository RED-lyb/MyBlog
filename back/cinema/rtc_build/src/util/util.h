
#pragma once

#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string>
#include <vector>
#include <iostream>
#include <sstream>
#include <functional>
#include <time.h>
#include <chrono>
#include <unistd.h>
namespace bytertc {


bool fileExisted( const std::string& path );

std::string& trim(std::string& text);
// Check if string is start with sub string
bool StringStart(const std::string& s, const std::string& p);

// Get the carry size
template < typename carry_t > inline size_t carrySize( const carry_t& c ) { return sizeof(c); }
template < > inline size_t carrySize<std::string>(const std::string& c) { return c.size(); }

template < typename carry_iterator_t >
inline std::vector< std::string > splitString(const std::string& value, carry_iterator_t b, carry_iterator_t e) {
    std::vector< std::string > components_;
    if ( value.size() == 0 ) return components_;
    std::string::size_type _pos = 0;
    do {
        std::string::size_type _lastPos = std::string::npos;
        size_t _carry_size = 0;
        for ( carry_iterator_t i = b; i != e; ++i ) {
            std::string::size_type _nextCarry = value.find(*i, _pos);
            if ( _nextCarry != std::string::npos && _nextCarry < _lastPos ) {
                _lastPos = _nextCarry;
                _carry_size = carrySize(*i);
            }
        }
        if ( _lastPos == std::string::npos ) _lastPos = value.size();
        if ( _lastPos > _pos ) {
            std::string _com = value.substr( _pos, _lastPos - _pos );
            components_.emplace_back(_com);
        }
        _pos = _lastPos + _carry_size;
    } while( _pos < value.size() );
    return components_;
}
template < typename carry_t >
inline std::vector< std::string > splitString(const std::string& value, const carry_t& carry) {
    return splitString(value, std::begin(carry), std::end(carry));
}


// Override to_string to support char * and string
inline std::string toString(const char* __val) { return std::string(__val); }
inline const std::string& toString(const std::string& __val) { return __val; }

template < typename T >
inline void ignoreResult( T unused_result ) { (void) unused_result; }

// Join Items as String
template< typename ComIterator, typename Connector_t >
inline std::string join(ComIterator begin, ComIterator end, Connector_t c) {
    std::string _final_string;
    if ( begin == end ) return _final_string;
    std::string _cstr = toString(c);
    auto i = begin, j = (++begin);
    for ( ; j != end; ++i, ++j ) {
        _final_string += toString(*i);
        _final_string += _cstr;
    }
    _final_string += toString(*i);
    return _final_string;
}

template < typename Component_t, typename Connector_t >
inline std::string join(const Component_t& parts, Connector_t c) {
    return join(begin(parts), end(parts), c);
}

size_t getFileSize(FILE* file);
size_t getFileSize(const char* filePath);
std::vector<unsigned char> readFile(const char* filePath,const char* mode = "rb");

long long getCurrentMillisecs();
void printLog(const std::string & str);
unsigned long getCurrentThreadId();
void printHelpAndExit();
void setCurrentDir(const std::string & str);
std::string getFileName(const std::string & filePath);
std::string getExePath();
std::string getCurrentTimeStr();
int safeStrToInt(const std::string &str);

}

#define LOG_BASE_INFO   "|line:" << __LINE__ << "|" << __FUNCTION__ << "; "
#define LOG__(level, type, d) { \
    std::stringstream ss; ss << bytertc::getCurrentTimeStr() << " RTCCLI|" << level << "[" << bytertc::getCurrentThreadId() << "] " << LOG_BASE_INFO << d << std::endl; bytertc::printLog(ss.str()); }

#define LOG_DEBUG(d)     LOG__("D",0, d)
#define LOG_INFO(d)        LOG__("I", 1, d)
#define LOG_WARN(d)        LOG__("W", 2, d)
#define LOG_ERROR(d)    LOG__("E",3, d)
#define LOG_FATAL(d)    LOG__("F",4, d)
#define CHECK_HELPER(PTR0, PTR1, ...) if ((!PTR0) || (!PTR1)) return __VA_ARGS__;