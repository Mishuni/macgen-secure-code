#include <string>
#include <regex>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Validate domain format
    if (domain.empty() || domain.find('.') == std::string::npos || 
        domain.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-") != std::string::npos) {
        return "https://" + domain;
    }

    // Validate target URL format
    std::regex url_regex(R"(^(https:\/\/)([a-zA-Z0-9\-\.]+)(\/.*)?$)");
    if (!std::regex_match(target, url_regex)) {
        return "https://" + domain;
    }

    // Extract host from target URL
    std::string::size_type pos = target.find("://") + 3; // Move past "://"
    std::string::size_type end_pos = target.find('/', pos);
    std::string host = target.substr(pos, end_pos - pos);

    // Check if the host matches the domain or is a subdomain
    if (host == domain || (host.size() > domain.size() && host.substr(host.size() - domain.size() - 1) == "." + domain)) {
        return target;
    } else {
        return "https://" + domain;
    }
}