#include <string>

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Validate the subdomain_prefix according to the specified rules
    if (subdomain_prefix.empty() || subdomain_prefix.length() > 63 || 
        subdomain_prefix.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-") != std::string::npos || 
        subdomain_prefix.front() == '-' || subdomain_prefix.back() == '-' || 
        subdomain_prefix.front() == '.' || subdomain_prefix.back() == '.') {
        return "https://" + domain;
    }
    return "https://" + subdomain_prefix + "." + domain;
}