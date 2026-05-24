#include <string>
#include <tuple>
#include <regex>
#include <stdexcept>

struct EmailValidationResult {
    bool is_valid;
    std::string error_message;
};

EmailValidationResult check_email(const std::string& email) {
    // Regular expression pattern for validating an email address
    static const std::regex email_regex(R"(^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$)");

    // Check for empty input
    if (email.empty()) {
        return { false, "Email cannot be empty" };
    }

    // Validate the email against the regex
    bool is_valid = std::regex_match(email, email_regex);
    
    // Return the validation result without exposing the regex pattern
    return { is_valid, is_valid ? "" : "Invalid email format" };
}