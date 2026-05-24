
#include <string>
#include <regex>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    std::regex domain_regex(R"(https:\/\/([a-zA-Z0-9-]+\.)*" + domain + R"(\b)");
    if (std::regex_search(target, domain_regex)) {
        return target;
    } else {
        return "https://" + domain;
    }
}