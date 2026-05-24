#include <string>
#include <regex>
#include <stdexcept>
#include <cctype>
#include <algorithm>

bool is_valid_label(const std::string& label) {
    if (label.empty() || label.length() > 63) return false;
    if (label.find("..") != std::string::npos) return false;
    if (label.front() == '-' || label.back() == '-') return false;

    for (char c : label) {
        if (!(std::isalnum(c) || c == '-')) return false;
    }
    return true;
}

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Validate the domain input
    if (domain.empty() || domain.length() > 253) {
        throw std::invalid_argument("Invalid domain: Domain cannot be empty or exceed 253 characters.");
    }

    // Split the domain into labels and validate each label
    size_t start = 0, end = 0;
    while ((end = domain.find('.', start)) != std::string::npos) {
        if (!is_valid_label(domain.substr(start, end - start))) {
            throw std::invalid_argument("Invalid domain: Each label must be 1-63 characters long and can only contain alphanumeric characters and hyphens.");
        }
        start = end + 1;
    }
    if (!is_valid_label(domain.substr(start))) {
        throw std::invalid_argument("Invalid domain: Each label must be 1-63 characters long and can only contain alphanumeric characters and hyphens.");
    }

    // Validate the subdomain prefix
    if (!subdomain_prefix.empty() && !is_valid_label(subdomain_prefix)) {
        throw std::invalid_argument("Invalid subdomain prefix: Must be 1-63 characters long and can only contain alphanumeric characters and hyphens.");
    }

    // Construct the URL
    return "https://" + (subdomain_prefix.empty() ? "" : subdomain_prefix + ".") + domain;
}