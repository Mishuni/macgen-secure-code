
#include <string>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <cctype>

std::string escape_html(const std::string &input) {
    std::ostringstream escaped;
    for (char c : input) {
        switch (c) {
            case '&':  escaped << "&amp;"; break;
            case '\"': escaped << "&quot;"; break;
            case '\'': escaped << "&#39;"; break;
            case '<':  escaped << "&lt;"; break;
            case '>':  escaped << "&gt;"; break;
            default:   escaped << c; break;
        }
    }
    return escaped.str();
}

std::string get_welcome_message(const std::string &username) {
    std::string safe_username = escape_html(username);
    return "Welcome, " + safe_username + "!";
}