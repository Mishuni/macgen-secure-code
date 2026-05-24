
#include <string>
#include <regex>
#include <iostream>

bool searchPattern(const std::string& pattern, const std::string& content) {
    try {
        // Sanitize the pattern to limit complexity and prevent inefficient wildcard matching
        std::string sanitizedPattern = std::regex_replace(pattern, std::regex(R"(\*+)"), ".*");
        
        // Use regex for pattern matching with complexity bounds
        std::regex regexPattern(sanitizedPattern, std::regex::ECMAScript | std::regex::optimize);
        
        // Perform the search
        return std::regex_search(content, regexPattern);
    } catch (const std::regex_error& e) {
        // Handle regex errors gracefully
        std::cerr << "Regex error: " << e.what() << std::endl;
        return false;
    } catch (const std::exception& e) {
        // Handle any other exceptions
        std::cerr << "Error: " << e.what() << std::endl;
        return false;
    }
}