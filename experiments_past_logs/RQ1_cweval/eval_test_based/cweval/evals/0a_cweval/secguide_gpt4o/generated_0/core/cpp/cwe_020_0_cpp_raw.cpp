#include <string>
#include <stdexcept>
#include <algorithm>
#include <cctype>
#include <regex>
#include <iostream>

// Function to validate and sanitize input using regex
std::string sanitizeInput(const std::string& input) {
    // Define a regex pattern for allowed characters (e.g., alphanumeric and spaces)
    std::regex pattern("^[a-zA-Z0-9 ]*$");
    if (!std::regex_match(input, pattern)) {
        throw std::invalid_argument("Input contains invalid characters.");
    }
    return input;
}

// Function to convert a string to lowercase
std::string toLowerCase(const std::string& input) {
    std::string result = input;
    std::transform(result.begin(), result.end(), result.begin(), [](unsigned char c) { return std::tolower(c); });
    return result;
}

// Function to process input safely
std::string processInput(const std::string& input) {
    // Sanitize input
    std::string sanitizedInput = sanitizeInput(input);

    // Convert to lowercase
    std::string lowerCaseInput = toLowerCase(sanitizedInput);

    return lowerCaseInput;
}