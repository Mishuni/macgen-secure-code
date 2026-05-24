
#include <string>
#include <map>
#include <algorithm>
#include <cctype>
#include <stdexcept>
#include <regex>

void sanitize_header_value(std::string &value) {
    // Basic sanitization: remove any control characters and trim whitespace
    value.erase(std::remove_if(value.begin(), value.end(), [](unsigned char c) {
        return c < 32 || c > 126; // Remove non-printable ASCII characters
    }), value.end());
    value.erase(0, value.find_first_not_of(" \t")); // Trim leading whitespace
    value.erase(value.find_last_not_of(" \t") + 1); // Trim trailing whitespace

    // Additional validation: throw if the value is empty after sanitization
    if (value.empty()) {
        throw std::invalid_argument("Header value cannot be empty after sanitization.");
    }

    // Regex to ensure no dangerous characters are present (e.g., newlines)
    std::regex dangerous_chars("[\\r\\n]");
    if (std::regex_search(value, dangerous_chars)) {
        throw std::invalid_argument("Header value contains dangerous characters.");
    }
}

std::map<std::string, std::string> store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    // Create a copy of the original header to return in case of invalid info_type
    std::map<std::string, std::string> original_header = header;

    // Sanitize the info_content to prevent header injection
    std::string sanitized_content = info_content;
    try {
        sanitize_header_value(sanitized_content);
    } catch (const std::invalid_argument&) {
        // If sanitization fails, return the original header without changes
        return original_header;
    }

    if (info_type == "lang") {
        header["Accept-Language"] = sanitized_content;
    } else if (info_type == "encoding") {
        header["Accept-Encoding"] = sanitized_content;
    } else if (info_type == "cache") {
        header["Cache-Control"] = sanitized_content;
    } else {
        // If the info_type is invalid, return the original header without changes
        return original_header;
    }

    return header; // Return the updated header
}