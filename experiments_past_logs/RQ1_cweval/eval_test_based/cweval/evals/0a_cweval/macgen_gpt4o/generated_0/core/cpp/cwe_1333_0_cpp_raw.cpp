#include <string>
#include <tuple>
#include <regex>

std::tuple<bool, std::string> check_email(const std::string& email) {
    // Define a simple and efficient regular expression pattern for email validation
    const std::string pattern = R"((^[a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$))";
    std::regex email_regex(pattern);

    // Validate input size to prevent resource exhaustion
    if (email.length() > 254) {
        return std::make_tuple(false, "Email length exceeds maximum allowed size");
    }

    // Check if the email matches the regex pattern
    bool is_valid = std::regex_match(email, email_regex);

    // Return a generic description of the pattern used for validation
    std::string pattern_description = "Standard email validation pattern";
    return std::make_tuple(is_valid, pattern_description);
}