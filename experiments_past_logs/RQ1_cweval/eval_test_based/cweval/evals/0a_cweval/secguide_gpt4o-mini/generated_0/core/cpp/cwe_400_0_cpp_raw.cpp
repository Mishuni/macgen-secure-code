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