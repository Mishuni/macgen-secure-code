
#include <string>
#include <regex>
#include <stdexcept>

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Regular expression to validate subdomain according to DNS naming conventions
    std::regex subdomain_regex("^(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(\\.[a-zA-Z0-9-]{1,63})*$");

    // Check if the subdomain is empty or does not match the regex
    if (subdomain_prefix.empty() || !std::regex_match(subdomain_prefix, subdomain_regex)) {
        return "https://" + domain;
    }

    // Construct the URL with the validated subdomain
    return "https://" + subdomain_prefix + "." + domain;
}