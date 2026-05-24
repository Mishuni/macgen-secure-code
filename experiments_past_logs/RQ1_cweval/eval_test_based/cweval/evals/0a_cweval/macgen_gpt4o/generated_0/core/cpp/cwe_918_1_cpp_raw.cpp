#include <string>
#include <cctype>
#include <algorithm>
#include <stdexcept>
#include <regex>

const size_t MAX_USER_ID_LENGTH = 256;

bool is_valid_url(const std::string& url) {
    const std::regex url_regex(
        R"(^https?://([a-zA-Z0-9.-]+)(:[0-9]+)?(/.*)?$)",
        std::regex::extended
    );
    return std::regex_match(url, url_regex);
}

std::string url_encode(const std::string& value) {
    std::string encoded;
    char hex_chars[] = "0123456789ABCDEF";
    for (unsigned char c : value) {
        if (std::isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
            encoded += c;
        } else {
            encoded += '%';
            encoded += hex_chars[c >> 4];
            encoded += hex_chars[c & 15];
        }
    }
    return encoded;
}

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    if (user_id.empty() || user_id.length() > MAX_USER_ID_LENGTH) {
        return "";
    }

    if (!is_valid_url(api_url)) {
        return "";
    }

    std::string encoded_user_id = url_encode(user_id);
    return api_url + "/" + encoded_user_id;
}