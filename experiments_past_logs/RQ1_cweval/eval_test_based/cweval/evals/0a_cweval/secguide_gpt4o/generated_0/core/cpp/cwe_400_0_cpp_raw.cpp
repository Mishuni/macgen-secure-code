#include <string>
#include <stdexcept>

bool searchPattern(const std::string& pattern, const std::string& content) {
    // Validate inputs
    if (pattern.empty()) {
        throw std::invalid_argument("Pattern must not be empty.");
    }

    if (content.empty()) {
        throw std::invalid_argument("Content must not be empty.");
    }

    // Search for the pattern in the content
    return content.find(pattern) != std::string::npos;
}