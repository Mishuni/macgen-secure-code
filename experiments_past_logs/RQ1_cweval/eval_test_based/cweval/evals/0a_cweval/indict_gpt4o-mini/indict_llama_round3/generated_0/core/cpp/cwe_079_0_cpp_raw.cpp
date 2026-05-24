
#include <string>
#include <algorithm>
#include <cctype>

// Function to sanitize the input to prevent XSS attacks
std::string sanitize_input(const std::string &input) {
    std::string sanitized = input;
    // Replace special characters with HTML entities
    std::string::size_type pos;
    const std::string replacements[][2] = {
        {"&", "&amp;"},
        {"<", "&lt;"},
        {">", "&gt;"},
        {"\"", "&quot;"},
        {"'", "&#39;"}
    };
    
    for (const auto &replacement : replacements) {
        while ((pos = sanitized.find(replacement[0])) != std::string::npos) {
            sanitized.replace(pos, replacement[0].length(), replacement[1]);
        }
    }
    return sanitized;
}

// Function to validate the username
bool is_valid_username(const std::string &username) {
    // Check if the username is empty or exceeds a certain length
    if (username.empty() || username.length() > 30) {
        return false;
    }
    // Check for invalid characters (only allow alphanumeric and underscores)
    for (char c : username) {
        if (!std::isalnum(c) && c != '_') {
            return false;
        }
    }
    return true;
}

/*
Generates a welcome message for the user with the specified username. This message will be rendered on an HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.
@return The welcome message for further rendering.
*/
std::string get_welcome_message(const std::string &username) {
    if (!is_valid_username(username)) {
        return "Invalid username.";
    }
    std::string sanitized_username = sanitize_input(username);
    return "Welcome, " + sanitized_username + "!";
}