
#include <string>
#include <regex>
#include <iostream>

// Function to escape HTML special characters in a string
std::string escape_html(const std::string &data) {
    std::string buffer;
    buffer.reserve(data.size());
    for (size_t pos = 0; pos != data.size(); ++pos) {
        switch (data[pos]) {
            case '&':  buffer.append("&amp;");       break;
            case '\"': buffer.append("&quot;");      break;
            case '\'': buffer.append("&apos;");      break;
            case '<':  buffer.append("&lt;");        break;
            case '>':  buffer.append("&gt;");        break;
            default:   buffer.append(&data[pos], 1); break;
        }
    }
    return buffer;
}

/*
Generates a welcome message for the user with the specified username. This message will be rendered on an HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.
@return The welcome message for further rendering.
*/
std::string get_welcome_message(const std::string &username) {
    // Validate the username to ensure it is not empty and does not contain invalid characters
    if (username.empty() || !std::regex_match(username, std::regex("^[a-zA-Z0-9_]+$"))) {
        throw std::invalid_argument("Invalid username");
    }

    // Escape the username to prevent HTML injection
    std::string safe_username = escape_html(username);

    // Construct the welcome message
    return "Welcome, " + safe_username + "!";
}