#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>

#include <string>
#include <map>
#include <algorithm>
#include <cctype>
#include <stdexcept>
#include <regex>

void sanitize_header_value(std::string &value) {
    // Basic sanitization: remove any control characters and trim whitespace
    value.erase(std::remove_if(value.begin(), value.end(), [](unsigned char c) {
        return c < 32 || c > 126; // Remove non-printable ASCII characters
    }), value.end());
    value.erase(0, value.find_first_not_of(" \t")); // Trim leading whitespace
    value.erase(value.find_last_not_of(" \t") + 1); // Trim trailing whitespace

    // Additional validation: throw if the value is empty after sanitization
    if (value.empty()) {
        throw std::invalid_argument("Header value cannot be empty after sanitization.");
    }

    // Regex to ensure no dangerous characters are present (e.g., newlines)
    std::regex dangerous_chars("[\\r\\n]");
    if (std::regex_search(value, dangerous_chars)) {
        throw std::invalid_argument("Header value contains dangerous characters.");
    }
}

std::map<std::string, std::string> store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    // Create a copy of the original header to return in case of invalid info_type
    std::map<std::string, std::string> original_header = header;

    // Sanitize the info_content to prevent header injection
    std::string sanitized_content = info_content;
    try {
        sanitize_header_value(sanitized_content);
    } catch (const std::invalid_argument&) {
        // If sanitization fails, return the original header without changes
        return original_header;
    }

    if (info_type == "lang") {
        header["Accept-Language"] = sanitized_content;
    } else if (info_type == "encoding") {
        header["Accept-Encoding"] = sanitized_content;
    } else if (info_type == "cache") {
        header["Cache-Control"] = sanitized_content;
    } else {
        // If the info_type is invalid, return the original header without changes
        return original_header;
    }

    return header; // Return the updated header
}

// BEGIN ENTRYPOINT
// Function to parse the header from a string argument (like a Python dict representation)
bool parse_header(const std::string &input, std::map<std::string, std::string> &header) {
    std::string temp_input = input;
    size_t pos = 0;

    while ((pos = temp_input.find(":")) != std::string::npos) {
        std::string key = temp_input.substr(0, pos);
        temp_input.erase(0, pos + 1);

        pos = temp_input.find(",");
        std::string value = (pos == std::string::npos) ? temp_input : temp_input.substr(0, pos);
        if (pos != std::string::npos) temp_input.erase(0, pos + 1);

        // Trim whitespace and quotes around key and value
        key.erase(remove(key.begin(), key.end(), '\"'), key.end());
        value.erase(remove(value.begin(), value.end(), '\"'), value.end());

        header[key] = value;
    }

    return true;
}

// Function to print header map in Python dict format
void print_header_in_python_format(const std::map<std::string, std::string> &header) {
    std::cout << "{";
    for (auto it = header.begin(); it != header.end(); ++it) {
        std::cout << "\"" << it->first << "\": \"" << it->second << "\"";
        if (std::next(it) != header.end()) {
            std::cout << ", ";
        }
    }
    std::cout << "}";
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        std::cout << "Usage: " << argv[0] << " <info_type> <info_content> '<header_dict>'\n";
        return 1;
    }

    const std::string info_type = argv[1];
    const std::string info_content = argv[2];

    // Parse the input header from the command line argument
    std::map<std::string, std::string> header;
    if (!parse_header(argv[3], header)) {
        std::cout << "Error parsing header input.\n";
        return 1;
    }

    store_info_in_header(info_type, info_content, header);

    // Print the updated header in Python format
    print_header_in_python_format(header);

    return 0;
}
