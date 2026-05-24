
#include <string>
#include <regex>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Define a regex pattern to match URLs within the specified domain
    std::regex domain_regex(R"(https:\/\/([a-zA-Z0-9-]+\.)?" + domain + R"((\/.*)?)");

    // Check if the target URL matches the domain pattern
    if (std::regex_match(target, domain_regex)) {
        return target;
    }

    // Fallback to the domain URL with https protocol
    return "https://" + domain;
}