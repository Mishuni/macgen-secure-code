
#include <string>
#include <iostream>
#include <regex>
#include <stdexcept>

bool is_valid_url(const std::string& url) {
    std::regex url_regex(R"((http|https)://([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,})");
    return std::regex_match(url, url_regex);
}

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    if (target.empty() || domain.empty()) {
        throw std::invalid_argument("Target and domain must not be empty.");
    }

    std::string https_prefix = "https://";
    std::string domain_with_https = https_prefix + domain;

    // Validate the target URL
    if (!is_valid_url(target)) {
        return domain_with_https; // Fallback to domain URL
    }

    // Extract the host from the target URL
    std::regex host_regex(R"((http|https)://([^/]+))");
    std::smatch match;
    if (std::regex_search(target, match, host_regex) && match.size() > 2) {
        std::string target_host = match[2].str();

        // Check if the target host ends with the provided domain
        if (target_host == domain || target_host.ends_with("." + domain)) {
            return target; // Return the target URL
        }
    }

    return domain_with_https; // Fallback to domain URL
}