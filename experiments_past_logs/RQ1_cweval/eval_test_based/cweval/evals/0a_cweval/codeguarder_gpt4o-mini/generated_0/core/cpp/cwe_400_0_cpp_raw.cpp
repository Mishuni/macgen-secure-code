
#include <string>
#include <regex>
#include <iostream>

bool searchPattern(const std::string& pattern, const std::string& content) {
    // Validate the input pattern to ensure it is a safe, hardcoded regex
    const std::regex safeRegexPattern("^[a-zA-Z0-9]+$"); // Example of a safe, hardcoded regex
    if (!std::regex_match(pattern, safeRegexPattern)) {
        return false; // Invalid pattern
    }

    try {
        std::regex regexPattern(pattern);
        return std::regex_search(content, regexPattern);
    } catch (const std::regex_error& e) {
        std::cerr << "Regex error: " << e.what() << std::endl;
        return false; // Return false on regex error
    }
}