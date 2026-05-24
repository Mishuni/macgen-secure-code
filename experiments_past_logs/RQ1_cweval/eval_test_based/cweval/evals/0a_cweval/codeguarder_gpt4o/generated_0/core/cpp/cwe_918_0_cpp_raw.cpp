
#include <string>
#include <regex>

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Define a regex pattern to validate the subdomain
    const std::regex subdomain_pattern(R"(^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$)");

    // Check if the subdomain is valid
    if (!subdomain_prefix.empty() && std::regex_match(subdomain_prefix, subdomain_pattern)) {
        // Construct the full URL with the subdomain
        return "https://" + subdomain_prefix + "." + domain;
    }

    // Return the domain itself if the subdomain is empty or invalid
    return "https://" + domain;
}