
#include <string>
#include <regex>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Regular expression to match URLs strictly within the given domain
    std::regex domain_regex(R"(https:\/\/([a-zA-Z0-9-]+\.)*" + domain + R"(\/|$))");
    
    // Check if the target URL matches the domain regex
    if (std::regex_match(target, domain_regex)) {
        return target;
    } else {
        return "https://" + domain;
    }
}