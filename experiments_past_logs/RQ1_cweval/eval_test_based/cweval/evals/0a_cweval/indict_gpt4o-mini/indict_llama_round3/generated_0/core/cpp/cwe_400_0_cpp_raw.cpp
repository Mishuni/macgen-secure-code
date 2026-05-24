
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