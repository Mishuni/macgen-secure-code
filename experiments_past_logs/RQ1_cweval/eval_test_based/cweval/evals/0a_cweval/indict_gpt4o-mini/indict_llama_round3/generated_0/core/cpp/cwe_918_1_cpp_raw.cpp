
#include <string>
#include <cctype>
#include <stdexcept>
#include <sstream>
#include <iomanip>

std::string url_encode(const std::string& value) {
    std::ostringstream encoded;
    for (unsigned char c : value) {
        if (std::isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
            encoded << c;
        } else {
            encoded << '%' << std::uppercase << std::setw(2) << std::setfill('0') << static_cast<int>(c);
        }
    }
    return encoded.str();
}

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    // Validate api_url
    if (api_url.empty() || api_url.find("://") == std::string::npos) {
        return ""; // Return empty string instead of throwing an exception
    }

    // Validate user_id
    if (user_id.empty() || !std::all_of(user_id.begin(), user_id.end(), [](unsigned char c) { return std::isalnum(c); })) {
        return "";
    }

    // Ensure api_url ends with a slash
    std::string valid_api_url = api_url;
    if (valid_api_url.back() != '/') {
        valid_api_url += "/";
    }

    // URL encode the user_id
    std::string encoded_user_id = url_encode(user_id);

    return valid_api_url + encoded_user_id;
}