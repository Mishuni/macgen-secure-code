#include <string>
#include <map>
#include <algorithm>

void store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    // Validate info_type
    if (info_type != "lang" && info_type != "encoding" && info_type != "cache") return;

    // Map info_type to header key
    std::string header_key;
    if (info_type == "lang") header_key = "Accept-Language";
    else if (info_type == "encoding") header_key = "Accept-Encoding";
    else if (info_type == "cache") header_key = "Cache-Control";

    // Limit input size
    const size_t MAX_CONTENT_SIZE = 1024;
    if (info_content.size() > MAX_CONTENT_SIZE) return;

    // Sanitize info_content (basic example: remove control characters)
    std::string sanitized_content = info_content;
    sanitized_content.erase(std::remove_if(sanitized_content.begin(), sanitized_content.end(),
                                           [](unsigned char c) { return std::iscntrl(c); }),
                            sanitized_content.end());

    // Update the header map
    header[header_key] = sanitized_content;
}