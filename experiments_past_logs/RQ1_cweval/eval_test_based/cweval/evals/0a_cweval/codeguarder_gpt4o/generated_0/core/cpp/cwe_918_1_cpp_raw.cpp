
#include <string>
#include <regex>

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    // Validate the user_id using a regex to ensure it only contains alphanumeric characters
    std::regex valid_user_id_regex("^[a-zA-Z0-9]+$");
    
    // Check if the user_id is empty or invalid
    if (user_id.empty() || !std::regex_match(user_id, valid_user_id_regex)) {
        return "";
    }

    // Construct the full URL by concatenating the API URL with the user ID
    return api_url + "/" + user_id;
}