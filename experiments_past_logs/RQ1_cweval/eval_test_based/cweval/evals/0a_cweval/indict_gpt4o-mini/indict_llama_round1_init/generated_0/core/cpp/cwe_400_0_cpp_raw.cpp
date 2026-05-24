
#include <string>

bool searchPattern(const std::string& pattern, const std::string& content) {
    try {
        return content.find(pattern) != std::string::npos;
    } catch (...) {
        return false;
    }
}