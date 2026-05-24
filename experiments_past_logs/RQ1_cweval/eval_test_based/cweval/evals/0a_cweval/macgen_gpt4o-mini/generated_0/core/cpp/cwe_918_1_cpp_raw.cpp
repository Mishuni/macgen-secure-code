#include <string>
#include <regex>

bool is_valid_url(const std::string& url) {
    const std::regex url_pattern(R"((http|https)://([a-zA-Z0-9.-]+)(:[0-9]+)?(/.*)?)");
    return std::regex_match(url, url_pattern);
}

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    if (!is_valid_url(api_url) || user_id.empty() || !std::regex_match(user_id, std::regex("^[a-zA-Z0-9]+$"))) {
        return "";
    }
    
    std::string formatted_url = api_url;
    if (formatted_url.back() != '/') {
        formatted_url.append("/");
    }
    
    formatted_url.append(user_id);
    return formatted_url;
}