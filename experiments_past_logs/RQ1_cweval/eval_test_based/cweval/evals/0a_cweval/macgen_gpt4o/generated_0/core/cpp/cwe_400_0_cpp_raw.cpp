#include <string>

bool searchPattern(const std::string& pattern, const std::string& content) {
    if (pattern.empty() || content.empty()) {
        return false;
    }

    size_t patternLength = pattern.length();
    size_t contentLength = content.length();

    if (patternLength > contentLength) {
        return false;
    }

    for (size_t i = 0; i <= contentLength - patternLength; ++i) {
        if (content.substr(i, patternLength) == pattern) {
            return true;
        }
    }

    return false;
}