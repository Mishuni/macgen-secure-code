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
#include <map>
#include <string>
#include <regex>
#include <stdexcept>
#include <mutex>
#include <algorithm>
#include <cctype>

std::mutex header_mutex;

bool is_valid_language_code(const std::string &lang) {
    return std::regex_match(lang, std::regex("^[a-z]{2}(-[A-Z]{2})?$"));
}

bool is_valid_encoding(const std::string &encoding) {
    static const std::set<std::string> valid_encodings = {"gzip", "deflate", "br", "identity"};
    return valid_encodings.find(encoding) != valid_encodings.end();
}

bool is_valid_cache_control(const std::string &cache) {
    static const std::set<std::string> valid_cache_controls = {"no-cache", "no-store", "max-age", "public", "private"};
    return valid_cache_controls.find(cache) != valid_cache_controls.end();
}

std::string sanitize_input(const std::string &input) {
    std::string sanitized;
    std::copy_if(input.begin(), input.end(), std::back_inserter(sanitized), [](char c) {
        return std::isalnum(c) || c == '-' || c == '_'; // Allow alphanumeric, hyphen, and underscore
    });
    return sanitized;
}

void store_info_in_header(const std::string &info_type, const std::string &info_content, std::map<std::string, std::string> &header) {
    std::lock_guard<std::mutex> lock(header_mutex);
    std::string key;

    std::string sanitized_content = sanitize_input(info_content);

    if (info_type == "lang") {
        if (!is_valid_language_code(sanitized_content)) {
            throw std::invalid_argument("Invalid language code");
        }
        key = "Accept-Language";
    } else if (info_type == "encoding") {
        if (!is_valid_encoding(sanitized_content)) {
            throw std::invalid_argument("Invalid encoding type");
        }
        key = "Accept-Encoding";
    } else if (info_type == "cache") {
        if (!is_valid_cache_control(sanitized_content)) {
            throw std::invalid_argument("Invalid cache control directive");
        }
        key = "Cache-Control";
    } else {
        throw std::invalid_argument("Invalid info_type");
    }

    header[key] = sanitized_content;
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
