
#include <string>
#include <map>
#include <algorithm>

void store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    // Define valid types and their corresponding header keys
    const std::map<std::string, std::string> valid_types = {
        {"lang", "Accept-Language"},
        {"encoding", "Accept-Encoding"},
        {"cache", "Cache-Control"}
    };

    // Check if the provided info_type is valid
    auto it = valid_types.find(info_type);
    if (it != valid_types.end()) {
        // Validate the info_content to prevent injection or invalid data
        if (!info_content.empty() && std::all_of(info_content.begin(), info_content.end(), [](unsigned char c) {
            return std::isalnum(c) || c == '-' || c == '_' || c == ' '; // Allow alphanumeric, hyphen, underscore, and space
        })) {
            // Update the header with the new information
            header[it->second] = info_content;
        }
    }
    // If anything goes wrong, return the original header without changes
}