
#include <string>
#include <tuple>
#include <regex>

std::tuple<bool, std::string> check_email(const std::string& email) {
    // Define a regex pattern for validating email addresses
    const std::string email_pattern = R"(^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$";
    
    // Check if the email contains exactly one '@' symbol
    if (std::count(email.begin(), email.end(), '@') != 1) {
        return std::make_tuple(false, "Invalid email format: must contain exactly one '@' symbol.");
    }

    // Use regex to validate the email format
    std::regex pattern(email_pattern);
    bool is_valid = std::regex_match(email, pattern);
    
    return std::make_tuple(is_valid, is_valid ? "Valid email format." : "Invalid email format.");
}