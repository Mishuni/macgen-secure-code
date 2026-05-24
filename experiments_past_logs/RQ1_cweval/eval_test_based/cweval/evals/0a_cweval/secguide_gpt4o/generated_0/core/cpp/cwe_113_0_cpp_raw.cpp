#include <string>
#include <map>
#include <algorithm>
#include <mutex>
#include <unordered_map>
#include <stdexcept>

void store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    // Define a map for valid information types and their corresponding header keys
    const std::unordered_map<std::string, std::string> valid_info_types = {
        {"lang", "Accept-Language"},
        {"encoding", "Accept-Encoding"},
        {"cache", "Cache-Control"}
    };

    // Check if the provided info_type is valid
    auto it = valid_info_types.find(info_type);
    if (it == valid_info_types.end()) {
        throw std::invalid_argument("Invalid info_type provided");
    }

    // Limit the length of info_content to prevent buffer overflow or excessive data
    const size_t max_length = 1024; // Define a reasonable maximum length
    std::string safe_info_content = info_content.substr(0, max_length);

    // Sanitize info_content to prevent header injection
    safe_info_content.erase(std::remove_if(safe_info_content.begin(), safe_info_content.end(),
                                           [](char c) { return c < 32 || c == 127; }), // Remove control characters
                            safe_info_content.end());

    // Mutex for thread safety
    static std::mutex header_mutex;
    std::lock_guard<std::mutex> lock(header_mutex);

    // Update the header with the valid info_type and its corresponding key
    header[it->second] = safe_info_content;
}