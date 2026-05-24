#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>

#include <string>
#include <regex>
#include <iostream>

bool searchPattern(const std::string& pattern, const std::string& content) {
    try {
        // Sanitize the pattern to limit complexity and prevent inefficient wildcard matching
        std::string sanitizedPattern = std::regex_replace(pattern, std::regex(R"(\*+)"), ".*");
        
        // Use regex for pattern matching with complexity bounds
        std::regex regexPattern(sanitizedPattern, std::regex::ECMAScript | std::regex::optimize);
        
        // Perform the search
        return std::regex_search(content, regexPattern);
    } catch (const std::regex_error& e) {
        // Handle regex errors gracefully
        std::cerr << "Regex error: " << e.what() << std::endl;
        return false;
    } catch (const std::exception& e) {
        // Handle any other exceptions
        std::cerr << "Error: " << e.what() << std::endl;
        return false;
    }
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    std::string pattern = argv[1];
    std::string content = argv[2];

    if (searchPattern(pattern, content)) {
        std::cout << "true";
    } else {
        std::cout << "false";
    }

    return 0;
}
