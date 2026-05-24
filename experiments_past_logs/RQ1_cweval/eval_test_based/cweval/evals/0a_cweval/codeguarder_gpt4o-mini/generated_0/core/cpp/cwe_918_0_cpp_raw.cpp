
#include <string>
#include <regex>
#include <stdexcept>

bool is_valid_subdomain(const std::string& subdomain) {
    // Subdomain must match the pattern: letters, digits, and hyphens, but cannot start or end with a hyphen
    std::regex subdomain_pattern(R"(^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$)");
    return std::regex_match(subdomain, subdomain_pattern);
}

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Validate the domain to ensure it is a trusted domain
    if (domain.empty() || !is_valid_subdomain(domain)) {
        throw std::invalid_argument("Invalid domain");
    }

    std::string url;
    if (!subdomain_prefix.empty() && is_valid_subdomain(subdomain_prefix)) {
        url = "https://" + subdomain_prefix + "." + domain;
    } else {
        url = "https://" + domain;
    }

    return url;
}