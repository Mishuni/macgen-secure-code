
#include <string>
#include <cctype>
#include <sstream>
#include <iomanip>

std::string url_encode(const std::string& value) {
    std::ostringstream escaped;
    escaped.fill('0');
    escaped << std::hex;

    for (char c : value) {
        if (isalnum(static_cast<unsigned char>(c)) || c == '-' || c == '_' || c == '.' || c == '~') {
            escaped << c;
        } else {
            escaped << '%' << std::setw(2) << static_cast<int>(static_cast<unsigned char>(c));
        }
    }

    return escaped.str();
}

bool is_valid_user_id(const std::string& user_id) {
    for (char c : user_id) {
        if (!isalnum(static_cast<unsigned char>(c)) && c != '-' && c != '_') {
            return false;
        }
    }
    return true;
}

bool is_valid_api_url(const std::string& api_url) {
    // Basic validation to check if the URL starts with http:// or https://
    return api_url.find("http://") == 0 || api_url.find("https://") == 0;
}

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    if (user_id.empty() || !is_valid_user_id(user_id) || !is_valid_api_url(api_url)) {
        return "";
    }
    return api_url + "/" + url_encode(user_id);
}