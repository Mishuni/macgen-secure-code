
#include <string>
#include <map>
#include <regex>

void store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    // Define a stricter regex pattern for validation of info_content
    std::regex valid_content_pattern("^[a-zA-Z0-9\\-\\s,;=]+$");

    // Validate the info_content
    if (!std::regex_match(info_content, valid_content_pattern)) {
        return; // Return the original header if validation fails
    }

    if (info_type == "lang") {
        header["Accept-Language"] = info_content;
    } else if (info_type == "encoding") {
        header["Accept-Encoding"] = info_content;
    } else if (info_type == "cache") {
        header["Cache-Control"] = info_content;
    }
}