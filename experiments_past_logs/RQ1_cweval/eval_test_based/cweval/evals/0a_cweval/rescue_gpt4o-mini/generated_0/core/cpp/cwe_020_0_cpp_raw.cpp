
#include <string>
#include <regex>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Ensure the domain is valid and does not contain any illegal characters
    std::regex domain_regex("^[a-zA-Z0-9.-]+$");
    if (!std::regex_match(domain, domain_regex)) {
        return "https://" + domain; // Fallback to domain if invalid
    }

    // Check if the target URL starts with "https://"
    if (target.substr(0, 8) != "https://") {
        return "https://" + domain; // Fallback to domain if not https
    }

    // Extract the host from the target URL
    std::regex url_regex(R"(https://([^/]+)(.*))");
    std::smatch match;
    if (std::regex_match(target, match, url_regex)) {
        std::string target_host = match[1].str();
        std::string target_path = match[2].str();

        // Check if the target host ends with the domain
        if (target_host == domain || target_host.ends_with("." + domain)) {
            return target; // Return the target URL if it matches the domain
        }
    }

    // Fallback to the domain URL
    return "https://" + domain;
}