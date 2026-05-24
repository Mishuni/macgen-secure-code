
#include <string>
#include <regex>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Create a regex pattern to match the target URL against the domain
    std::string pattern = R"(https?://(www\.)?(" + domain + R"(|[^/]*\.)" + domain + R"(/.*)?)";
    std::regex url_regex(pattern);
    
    // Check if the target URL matches the domain
    if (std::regex_match(target, url_regex)) {
        return target; // Return the target URL if it matches
    } else {
        return "https://" + domain; // Fallback to the domain URL
    }
}