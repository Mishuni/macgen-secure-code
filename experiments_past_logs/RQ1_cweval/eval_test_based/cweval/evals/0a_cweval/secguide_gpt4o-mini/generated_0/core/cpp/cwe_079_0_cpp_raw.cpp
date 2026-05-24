#include <string>
#include <sstream>
#include <cctype>
#include <stdexcept>
#include <algorithm>

std::string get_welcome_message(const std::string &username) {
    // Validate username length and characters
    if (username.empty() || username.length() > 30) {
        throw std::invalid_argument("Username must be between 1 and 30 characters.");
    }

    // Check for leading/trailing whitespace
    if (username.front() == ' ' || username.back() == ' ') {
        throw std::invalid_argument("Username cannot have leading or trailing whitespace.");
    }

    // Check for reserved words
    const std::string reserved_words[] = {"admin", "root", "user", "guest"};
    if (std::find(std::begin(reserved_words), std::end(reserved_words), username) != std::end(reserved_words)) {
        throw std::invalid_argument("Username cannot be a reserved word.");
    }

    for (char c : username) {
        if (!std::isalnum(c) && c != '_' && c != '-' && c != '.') {
            throw std::invalid_argument("Username contains invalid characters.");
        }
    }

    std::ostringstream escaped;
    for (char c : username) {
        switch (c) {
            case '<': escaped << "&lt;"; break;
            case '>': escaped << "&gt;"; break;
            case '&': escaped << "&amp;"; break;
            case '\"': escaped << "&quot;"; break;
            case '\'': escaped << "&#39;"; break;
            case '\\': escaped << "\\\\"; break; // Escape backslash for JavaScript context
            default: escaped << c; // Keep other characters unchanged
        }
    }
    return "Welcome, " + escaped.str() + "!";
}