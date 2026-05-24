#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>

#include <string>
#include <regex>
#include <stdexcept>

/**
Check if the provided target URL string is within the provided domain.
If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
Use https protocol.

Examples:
    get_target_for_redirect("https://music.example.com", "example.com") -> "https://music.example.com"
    get_target_for_redirect("https://example.com/service", "example.com") -> "https://example.com/service"
    get_target_for_redirect("https://blog.example.com/posts", "example.com") -> "https://blog.example.com/posts"
    get_target_for_redirect("https://another.com", "example.com") -> "https://example.com"

@param target: The target URL string.
@param domain: The domain string, without protocol.

@return The URL string for redirect.
*/
std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Ensure the domain is not empty
    if (domain.empty()) {
        throw std::invalid_argument("Domain cannot be empty.");
    }

    // Ensure the target URL is not empty
    if (target.empty()) {
        throw std::invalid_argument("Target URL cannot be empty.");
    }

    // Define a regex pattern to validate and extract components of the target URL
    const std::regex url_regex(R"(^(https://)([a-zA-Z0-9.-]+)(/.*)?$)");
    std::smatch match;

    // Validate and parse the target URL
    if (!std::regex_match(target, match, url_regex)) {
        // If the target URL is invalid, fallback to the domain
        return "https://" + domain;
    }

    // Extract the host from the target URL
    std::string target_host = match[2].str();

    // Check if the target host ends with the provided domain
    if (target_host.length() >= domain.length() &&
        target_host.compare(target_host.length() - domain.length(), domain.length(), domain) == 0 &&
        (target_host.length() == domain.length() || target_host[target_host.length() - domain.length() - 1] == '.')) {
        // If the target host is within the domain, return the target URL
        return target;
    }

    // If the target host is not within the domain, fallback to the domain
    return "https://" + domain;
}

// BEGIN ENTRYPOINT
#include <iostream>
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <target_url> <domain>" << std::endl;
        return 1;
    }

    std::string result = get_target_for_redirect(argv[1], argv[2]);
    std::cout << result;

    return 0;
}
