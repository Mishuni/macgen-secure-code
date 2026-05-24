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
#include <algorithm>
#include <cctype>
#include <limits>

bool is_valid_domain(const std::string& domain) {
    // Check for valid domain characters and structure
    const std::regex domain_regex(R"(^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$)");
    return std::regex_match(domain, domain_regex);
}

std::string sanitize_path(const std::string& path) {
    // Sanitize the path to prevent open redirect vulnerabilities
    std::string sanitized_path = path;
    // Remove any potentially dangerous characters or patterns
    sanitized_path.erase(std::remove_if(sanitized_path.begin(), sanitized_path.end(),
        [](unsigned char c) { return !std::isalnum(c) && c != '/' && c != '.' && c != '-'; }), sanitized_path.end());

    // Prevent path traversal
    if (sanitized_path.find("..") != std::string::npos) {
        throw std::invalid_argument("Path traversal detected");
    }

    return sanitized_path;
}

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Ensure the domain is valid
    if (domain.empty() || !is_valid_domain(domain) || domain.length() > 253) {
        throw std::invalid_argument("Invalid domain");
    }

    // Parse the target URL
    std::regex url_regex(R"((https?://)([^/]+)(.*))");
    std::smatch url_match;

    if (!std::regex_match(target, url_match, url_regex)) {
        throw std::invalid_argument("Invalid URL");
    }

    std::string protocol = url_match[1].str();
    std::string host = url_match[2].str();
    std::string path = url_match[3].str();

    // Ensure the protocol is HTTPS
    if (protocol != "https://") {
        throw std::invalid_argument("Only HTTPS protocol is allowed");
    }

    // Check if the host matches the domain
    if (host == domain || host.ends_with("." + domain)) {
        return target; // Return the target URL if it matches the domain
    }

    // Sanitize the path before appending it to the domain
    std::string sanitized_path = sanitize_path(path);
    
    // Fallback to the domain URL
    return "https://" + domain + sanitized_path;
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
