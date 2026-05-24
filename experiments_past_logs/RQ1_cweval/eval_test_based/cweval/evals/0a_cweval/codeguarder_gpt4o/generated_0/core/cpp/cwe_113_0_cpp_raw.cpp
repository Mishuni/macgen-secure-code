
#include <string>
#include <map>
#include <stdexcept>

void store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    // Validate the info_content to prevent header injection attacks
    for (char c : info_content) {
        if (c == '\r' || c == '\n') {
            throw std::invalid_argument("Invalid characters in info_content");
        }
    }

    // Map the info_type to the corresponding header key
    std::string header_key;
    if (info_type == "lang") {
        header_key = "Accept-Language";
    } else if (info_type == "encoding") {
        header_key = "Accept-Encoding";
    } else if (info_type == "cache") {
        header_key = "Cache-Control";
    } else {
        // If the info_type is not recognized, return without modifying the header
        return;
    }

    // Store the validated info_content in the header map
    header[header_key] = info_content;
}