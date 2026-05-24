
#include <string>
#include <stdexcept>
#include <algorithm>
#include <cctype>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Check if the domain is valid
    if (domain.empty() || domain.find('.') == std::string::npos) {
        throw std::invalid_argument("Invalid domain");
    }

    // Ensure the target URL starts with "https://"
    if (!target.starts_with("https://")) {
        return "https://" + domain; // Fallback to the domain URL
    }

    // Extract the host from the target URL
    std::string::size_type start = target.find("://") + 3; // Skip "https://"
    std::string::size_type end = target.find('/', start);
    std::string host = target.substr(start, end - start);

    // Normalize the domain for comparison
    std::string normalized_domain = domain;
    std::transform(normalized_domain.begin(), normalized_domain.end(), normalized_domain.begin(), ::tolower);

    // Normalize the host for comparison
    std::string normalized_host = host;
    std::transform(normalized_host.begin(), normalized_host.end(), normalized_host.begin(), ::tolower);

    // Check if the host ends with the domain
    if (normalized_host == normalized_domain || 
        (normalized_host.size() > normalized_domain.size() + 1 && 
         normalized_host.compare(normalized_host.size() - normalized_domain.size() - 1, normalized_domain.size() + 1, "." + normalized_domain) == 0)) {
        return target; // Return the target URL if it matches
    } else {
        return "https://" + domain; // Fallback to the domain URL
    }
}