
#include <string>

bool searchPattern(const std::string& pattern, const std::string& content) {
    // Validate input to prevent potential security issues
    if (pattern.empty() || content.empty()) {
        return false;
    }

    // Check for excessively large input to prevent resource exhaustion
    const size_t maxAllowedSize = 1000000; // Example threshold, adjust as needed
    if (pattern.size() > maxAllowedSize || content.size() > maxAllowedSize) {
        return false;
    }

    // Perform the search
    return content.find(pattern) != std::string::npos;
}