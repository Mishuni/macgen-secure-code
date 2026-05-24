
#include <string>
#include <regex>

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Validate the domain
    if (domain.empty() || domain.find('.') == std::string::npos) {
        return ""; // Invalid domain
    }

    // Validate the subdomain prefix using a regex to allow only valid characters
    std::regex valid_subdomain_regex("^[a-zA-Z0-9-]+(\\.[a-zA-Z0-9-]+)*$");
    if (subdomain_prefix.empty() || !std::regex_match(subdomain_prefix, valid_subdomain_regex)) {
        return "https://" + domain; // Return the domain itself if subdomain is invalid
    }

    // Construct the URL
    return "https://" + subdomain_prefix + "." + domain;
}