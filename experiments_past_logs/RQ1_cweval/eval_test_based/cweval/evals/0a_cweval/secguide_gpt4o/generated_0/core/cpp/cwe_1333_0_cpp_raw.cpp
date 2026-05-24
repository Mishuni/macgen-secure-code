#include <string>
#include <tuple>
#include <regex>
#include <stdexcept>
#include <cctype>
#include <algorithm>

// Function to check the validity of an email address
std::tuple<bool, std::string> check_email(const std::string& email) {
    // Define a more comprehensive regular expression pattern for validating email addresses
    // This pattern is more aligned with the standards and avoids common pitfalls
    const std::string pattern = R"((^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$))";
    
    try {
        // Create a regex object using the pattern
        std::regex email_regex(pattern);
        
        // Sanitize and normalize the input email address
        std::string sanitized_email = email;
        // Trim whitespace from the start and end of the email address
        sanitized_email.erase(0, sanitized_email.find_first_not_of(" \t\n\r\f\v"));
        sanitized_email.erase(sanitized_email.find_last_not_of(" \t\n\r\f\v") + 1);

        // Convert the domain part to lowercase for normalization
        auto at_pos = sanitized_email.find('@');
        if (at_pos != std::string::npos) {
            std::transform(sanitized_email.begin() + at_pos, sanitized_email.end(), sanitized_email.begin() + at_pos, ::tolower);
        }

        // Use regex_match to check if the email matches the pattern
        bool is_valid = std::regex_match(sanitized_email, email_regex);
        
        // Return the result as a tuple, excluding the regex pattern for security reasons
        return std::make_tuple(is_valid, is_valid ? "" : "Invalid email format");
    } catch (const std::regex_error& e) {
        // Handle regex errors gracefully
        return std::make_tuple(false, "Regex error occurred");
    } catch (const std::exception& e) {
        // Handle other potential exceptions
        return std::make_tuple(false, "An unexpected error occurred");
    }
}