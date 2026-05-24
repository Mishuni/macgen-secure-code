
#include <string>

bool searchPattern(const std::string& pattern, const std::string& content) {
    if (pattern.empty() || content.empty()) {
        return false;
    }
    return content.find(pattern) != std::string::npos;
}