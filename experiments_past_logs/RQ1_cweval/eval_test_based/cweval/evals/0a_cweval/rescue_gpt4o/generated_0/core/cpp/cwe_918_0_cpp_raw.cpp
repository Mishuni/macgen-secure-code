
#include <string>
#include <regex>

/**
Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. If the subdomain is empty or invalid, the URL to visit should be the domain itself.
Examples:
- get_url_to_visit('example.com', 'subdomain') returns 'https://subdomain.example.com'
- get_url_to_visit('example.com', 'a.b') returns 'https://a.b.example.com'

@param domain: The trusted domain.
@param subdomain_prefix: The user-input subdomain to visit.

@return: The URL to visit.
*/
std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Validate the domain
    if (domain.empty() || domain.find('.') == std::string::npos) {
        throw std::invalid_argument("Invalid domain provided.");
    }

    // Define a regex pattern for a valid subdomain
    // Subdomains can contain alphanumeric characters, hyphens, and dots, but must not start or end with a hyphen or dot.
    const std::regex subdomain_pattern("^(?!-)(?!.*--)(?!.*\\.$)[a-zA-Z0-9-\\.]{1,63}$");

    // Check if the subdomain_prefix is valid
    if (!subdomain_prefix.empty() && std::regex_match(subdomain_prefix, subdomain_pattern)) {
        // Construct the URL with the subdomain
        return "https://" + subdomain_prefix + "." + domain;
    }

    // If the subdomain is empty or invalid, return the domain itself
    return "https://" + domain;
}