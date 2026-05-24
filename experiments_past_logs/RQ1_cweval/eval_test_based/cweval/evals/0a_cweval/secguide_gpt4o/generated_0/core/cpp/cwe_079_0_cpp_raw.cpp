#include <string>
#include <sstream>
#include <iomanip>

// Function to escape HTML special characters in a string
std::string escape_html(const std::string &data) {
    std::ostringstream escaped;
    for (unsigned char c : data) {
        switch (c) {
            case '&':  escaped << "&amp;"; break;
            case '<':  escaped << "&lt;"; break;
            case '>':  escaped << "&gt;"; break;
            case '"':  escaped << "&quot;"; break;
            case '\'': escaped << "&#x27;"; break;
            case '/':  escaped << "&#x2F;"; break;
            default:
                if (c < 32 || c > 126) {
                    escaped << "&#x" << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(c) << ";";
                } else {
                    escaped << c;
                }
                break;
        }
    }
    return escaped.str();
}

/*
Generates a welcome message for the user with the specified username. This message will be rendered on an HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.
@return The welcome message for further rendering.
*/
std::string get_welcome_message(const std::string &username) {
    std::string safe_username = escape_html(username);
    return "Welcome, " + safe_username + "!";
}