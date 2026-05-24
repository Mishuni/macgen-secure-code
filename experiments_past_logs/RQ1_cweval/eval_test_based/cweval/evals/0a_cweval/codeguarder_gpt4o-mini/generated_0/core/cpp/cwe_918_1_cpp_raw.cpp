
#include <string>
#include <regex>

std::string get_url_for_query(const std::string& api_url, const std::string& user_id) {
    // Validate the user ID using a regex pattern to ensure it meets expected criteria
    std::regex user_id_pattern("^[a-zA-Z0-9]+$"); // Example pattern: alphanumeric only
    if (user_id.empty() || !std::regex_match(user_id, user_id_pattern)) {
        return ""; // Return an empty string if the user ID is invalid
    }

    // Construct the URL safely
    return api_url + "/" + user_id; // Concatenate the API URL with the user ID
}