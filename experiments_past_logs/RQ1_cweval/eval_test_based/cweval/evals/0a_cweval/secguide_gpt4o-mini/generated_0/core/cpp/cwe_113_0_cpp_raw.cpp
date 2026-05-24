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