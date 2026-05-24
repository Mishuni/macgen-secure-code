
#include <string>

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    if (user_id.empty()) {
        return "";
    }
    return api_url + "/" + user_id;
}