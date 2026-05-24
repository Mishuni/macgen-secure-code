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
#include <stdexcept>
#include <algorithm>
#include <cctype>
#include <regex>

bool isInputValid(const std::string& pattern, const std::string& content) {
    // Check for null or excessively long strings
    if (pattern.empty() || content.empty() || pattern.length() > 1000 || content.length() > 10000) {
        return false;
    }

    // Check for invalid characters (e.g., control characters)
    if (!std::all_of(pattern.begin(), pattern.end(), [](unsigned char c) { return std::isprint(c); }) ||
        !std::all_of(content.begin(), content.end(), [](unsigned char c) { return std::isprint(c); })) {
        return false;
    }

    // Additional sanitization checks can be added here
    return true;
}

bool searchPattern(const std::string& pattern, const std::string& content) {
    if (!isInputValid(pattern, content)) {
        return false;
    }

    try {
        // Escape special regex characters in the pattern to treat them literally
        std::string escapedPattern = std::regex_replace(pattern, std::regex(R"([\[\]\(\)\{\}\.\+\?\^\$\\])"), R"(\\$0)");
        
        // Handle whitespace in the pattern by trimming it
        escapedPattern = std::regex_replace(escapedPattern, std::regex(R"(^\s+|\s+$)"), "");

        // Use regex to search for the escaped pattern in the content
        std::regex safePattern(escapedPattern);
        return std::regex_search(content, safePattern);
    } catch (const std::regex_error& e) {
        // Log the regex error message if needed
        return false;
    } catch (const std::exception& e) {
        // Log the exception message if needed
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
