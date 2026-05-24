#include <string>
#include <regex>
#include <stdexcept>
#include <unordered_set>

// A set of valid TLDs for validation purposes
const std::unordered_set<std::string> valid_tlds = {
    "com", "org", "net", "edu", "gov", "io", "co", "us", "uk", "de", "jp", "fr", "au", "ru", "ch", "it", "nl", "se", "no", "es", "mil", "int", "biz", "info", "mobi", "name", "aero", "jobs", "museum"
    // Add more TLDs as needed
};

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Define a regex pattern to validate the subdomain
    const std::regex subdomain_pattern("^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$");
    // Define a regex pattern to validate the domain
    const std::regex domain_pattern("^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\\.[A-Za-z0-9-]{1,63})*$");

    // Validate the domain
    if (!std::regex_match(domain, domain_pattern)) {
        throw std::invalid_argument("Invalid domain format.");
    }

    // Split the domain to validate the TLD
    size_t last_dot = domain.find_last_of('.');
    if (last_dot == std::string::npos || last_dot == domain.length() - 1) {
        throw std::invalid_argument("Domain must contain a valid TLD.");
    }
    std::string tld = domain.substr(last_dot + 1);
    if (valid_tlds.find(tld) == valid_tlds.end()) {
        throw std::invalid_argument("Invalid or unknown TLD.");
    }

    // Validate the subdomain
    if (!subdomain_prefix.empty() && !std::regex_match(subdomain_prefix, subdomain_pattern)) {
        throw std::invalid_argument("Invalid subdomain format.");
    }

    // Construct the URL
    std::string url = "https://";
    if (!subdomain_prefix.empty()) {
        url += subdomain_prefix + ".";
    }
    url += domain;

    // Check the total length of the URL
    if (url.length() > 253) {
        throw std::invalid_argument("The constructed URL exceeds the maximum allowed length.");
    }

    return url;
}