#include <map>
#include <string>
#include <algorithm>
#include <cctype>

void store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    const std::map<std::string, std::string> info_map = {
        {"lang", "Accept-Language"},
        {"encoding", "Accept-Encoding"},
        {"cache", "Cache-Control"}
    };

    if (info_map.find(info_type) == info_map.end()) {
        return; // Skip update if invalid
    }

    std::string sanitized_content = info_content;
    sanitized_content.erase(std::remove_if(sanitized_content.begin(), sanitized_content.end(), [](char c) {
        return !std::isprint(c);
    }), sanitized_content.end());

    const size_t MAX_LENGTH = 1024; // Define maximum length
    if (sanitized_content.length() > MAX_LENGTH) {
        return; // Reject overly long inputs
    }

    header[info_map.at(info_type)] = sanitized_content;
}