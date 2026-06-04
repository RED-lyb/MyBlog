

#include "argparser.h"
#include "util.h"

#include <vector>
#include <iostream>
#include <fstream>

namespace bytertc {
    // Singleton
argparser& argparser::_() { static argparser _; return _; }
argparser::argparser() { }

// Set the parser info
void argparser::set_parser(const std::string& key, set_arg_t setter) {
    argparser::set_parser(key, "", setter);
}
void argparser::set_parser(const std::string& key, std::string& getter) {
    argparser::set_parser(key, "", getter);
}
void argparser::set_parser(const std::string& key, const std::string& attr, set_arg_t setter) {
    _().setter_map_[key] = setter;
    if ( attr.size() > 0 ) _().setter_map_[attr] = setter;
}
void argparser::set_parser(const std::string& key, const std::string& attr, std::string& getter) {
    std::string* _pgetter = &getter;
    argparser::set_parser(key, attr, [_pgetter](std::string && arg) {
        *_pgetter = move(arg);
    });
}

// Get all individual args
std::vector< std::string > argparser::individual_args() {
    return _().individual_args_;
}

// Do the parser
bool argparser::parse(int argc, char* argv[]) {
    static std::vector< std::string > _remarks = {"="};
    for ( int i = 1; i < argc; ++i ) {
        std::string _arg = argv[i];
        std::string _key_with_equal;
        if ( StringStart(_arg, "--") ) {
            _key_with_equal = _arg.substr(2);
        } else if ( StringStart(_arg, "-") ) {
            _key_with_equal = _arg.substr(1);
        } else {
            _().individual_args_.push_back(_arg);
            continue;
        }
        int first_of_equal = _key_with_equal.find_first_of('=');
        std::string _fmt_parts;
        if (first_of_equal != std::string::npos) {
            _fmt_parts = std::string(_key_with_equal.begin(), _key_with_equal.begin() + first_of_equal);
        }
        if (_fmt_parts.empty()) {
            std::cerr << "Unknow command: " << _arg << std::endl;
            return false;
        }
        auto s = _().setter_map_.find(_fmt_parts);
        if ( s == _().setter_map_.end() ) {
            std::cerr << "Unknow command: " << _arg << std::endl;
            return false;
        }
        std::string _value = std::string(_key_with_equal.begin() + first_of_equal + 1, _key_with_equal.end());      
        s->second(move(_value));
    }
    return true;
}

// Do the parse from a config file
bool argparser::parse( const std::string& config_file ) {
    static std::vector< std::string > _remarks = {"=", " ", ":", "\t"};
    std::ifstream _cfg(config_file);
    if ( !_cfg ) return false;

    std::string _line;
    while ( std::getline(_cfg, _line) ) {
        trim(_line);
        if ( _line.size() == 0 ) continue;
        if ( _line[0] == '#' ) continue;    // Comment Line

        // Sub comment in the line
        size_t _comment_pos = _line.find("#");
        if ( _comment_pos != std::string::npos ) {
            // Do have comment
            _line = _line.substr(0, _comment_pos);
            // Remove the end whitespace
            trim(_line);
        }

        auto _fmt_parts = splitString(_line, _remarks);
        auto s = _().setter_map_.find(_fmt_parts[0]);
        if ( s == _().setter_map_.end() ) {
            std::cerr << "Unknow config key: " << _fmt_parts[0] << std::endl;
            continue;
        }
        size_t _skip_size = _fmt_parts[0].size();
        while ( _skip_size < _line.size() ) {
            if ( 
                _line[_skip_size] == '=' || 
                _line[_skip_size] == ' ' ||
                _line[_skip_size] == ':' ||
                _line[_skip_size] == '\t'
                ) ++_skip_size;
            else break;
        }
        std::string _value = (_skip_size == _line.size() ? 
            "" : _line.substr(_skip_size));
        trim(_value);
        s->second(move(_value));
    }
    return true;
}

// Clear
void argparser::clear() {
    _().setter_map_.clear();
    _().individual_args_.clear();
}
}