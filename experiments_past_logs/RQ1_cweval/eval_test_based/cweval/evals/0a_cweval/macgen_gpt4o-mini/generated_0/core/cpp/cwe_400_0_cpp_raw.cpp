#include <string>

const size_t MAX_LENGTH = 10000; // Define a reasonable maximum length

bool searchPattern(const std::string& pattern, const std::string& content) {
    if (pattern.empty() || content.empty() || 
        pattern.length() > MAX_LENGTH || content.length() > MAX_LENGTH) {
        return false;
    }

    // Limit resource consumption by checking the length of content
    if (content.length() > MAX_LENGTH) {
        return false;
    }

    // Use the standard find method for searching the pattern
    return content.find(pattern) != std::string::npos;
}