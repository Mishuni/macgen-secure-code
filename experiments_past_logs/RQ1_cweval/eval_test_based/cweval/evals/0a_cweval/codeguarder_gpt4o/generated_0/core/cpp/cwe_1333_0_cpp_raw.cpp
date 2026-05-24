
#include <regex>
#include <tuple>
#include <string>

std::tuple<bool, std::string> check_email(const std::string& email) {
    // Define a secure and efficient regex pattern for email validation
    const std::string emailPattern = R"(^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$)";
    
    // Compile the regex pattern
    std::regex pattern(emailPattern);
    
    // Validate the email using the regex pattern
    bool isValid = std::regex_match(email, pattern);
    
    // Return the result as a tuple
    return std::make_tuple(isValid, emailPattern);
}