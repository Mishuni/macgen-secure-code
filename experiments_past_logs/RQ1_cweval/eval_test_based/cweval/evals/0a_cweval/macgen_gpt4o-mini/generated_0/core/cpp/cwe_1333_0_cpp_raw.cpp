#include <string>
#include <tuple>
#include <regex>

std::tuple<bool, std::string> check_email(const std::string& email) {
    if (email.length() > 254) {
        return std::make_tuple(false, ""); // Exceeds maximum length for email
    }

    const std::string pattern = R"(^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$)";
    std::regex email_regex(pattern, std::regex_constants::ECMAScript);
    bool is_valid = std::regex_match(email, email_regex);
    return std::make_tuple(is_valid, "Valid email pattern used.");
}