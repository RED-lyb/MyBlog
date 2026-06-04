#include <string>
#include <functional>
#include <map>
#include <vector>

#pragma once
namespace bytertc {
class argparser {
public: 
    typedef std::function< void (std::string &&) >   set_arg_t;
protected: 
    std::map< std::string, set_arg_t >       setter_map_;
    std::vector< std::string >          individual_args_;
protected: 
    // Singleton
    static argparser& _();
    argparser();
public: 
    // no copy
    argparser( const argparser& ref ) = delete;
    argparser( argparser&& rref ) = delete;
    argparser& operator = (const argparser& ) = delete;
    argparser& operator = (argparser&&) = delete;

    // Set the parser info
    static void set_parser(const std::string& key, set_arg_t setter);
    static void set_parser(const std::string& key, std::string& getter);
    static void set_parser(const std::string& key, const std::string& attr, set_arg_t setter);
    static void set_parser(const std::string& key, const std::string& attr, std::string& getter);

    // Do the parser
    static bool parse(int argc, char* argv[]);

    // Do the parse from a config file
    static bool parse( const std::string& config_file );

    // Get all individual args
    static std::vector< std::string > individual_args();

    // Clear
    static void clear();
};
};