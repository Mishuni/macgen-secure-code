#include <string>
#include <stdexcept>
#include <algorithm>

std::string html_escape(const std::string &input) {
    std::string output;
    for (char c : input) {
        switch (c) {
            case '&': output += "&amp;"; break;
            case '<': output += "&lt;"; break;
            case '>': output += "&gt;"; break;
            case '"': output += "&quot;"; break;
            case '\'': output += "&#39;"; break;
            default: output += c; break;
        }
    }
    return output;
}

std::string get_welcome_message(const std::string &username) {
    if (username.empty() || username.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_") != std::string::npos) {
        throw std::invalid_argument("Invalid username");
    }
    
    const std::string welcome_prefix = "Welcome, ";
    std::string safe_username = html_escape(username);
    return welcome_prefix + safe_username + "!";
}