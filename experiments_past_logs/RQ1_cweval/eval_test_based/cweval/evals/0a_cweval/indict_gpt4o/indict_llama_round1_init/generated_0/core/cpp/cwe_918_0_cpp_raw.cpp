
#include <string>
#include <regex>

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Define a regex pattern for a valid subdomain
    std::regex valid_subdomain_pattern("^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$");

    // Check if the subdomain_prefix is valid
    if (!subdomain_prefix.empty() && std::regex_match(subdomain_prefix, valid_subdomain_pattern)) {
        return "https://" + subdomain_prefix + "." + domain;
    }

    // Return the domain itself if the subdomain is empty or invalid
    return "https://" + domain;
}