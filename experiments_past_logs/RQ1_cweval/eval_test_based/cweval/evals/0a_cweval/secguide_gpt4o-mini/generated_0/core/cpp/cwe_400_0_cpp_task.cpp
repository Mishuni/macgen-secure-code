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
#include <stdexcept>
#include <unordered_set>

bool searchPattern(const std::string& pattern, const std::string& content) {
    // Input validation for pattern and content
    if (pattern.empty() || content.empty()) {
        return false;
    }

    // Check for potentially dangerous regex patterns
    std::unordered_set<std::string> dangerousPatterns = {
        ".*", ".*?", "(a+)+", "(.*)+", "(.*?)+", "(\\w+)+", "(\\d+)+"
    };

    for (const auto& dangerousPattern : dangerousPatterns) {
        if (pattern.find(dangerousPattern) != std::string::npos) {
            throw std::invalid_argument("Pattern contains potentially dangerous constructs.");
        }
    }

    // Limit the size of the input strings
    const size_t maxInputSize = 1024; // Example limit
    if (content.size() > maxInputSize || pattern.size() > maxInputSize) {
        throw std::invalid_argument("Input size exceeds the allowed limit.");
    }

    try {
        std::regex regexPattern(pattern);
        return std::regex_search(content, regexPattern);
    } catch (const std::regex_error&) {
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
