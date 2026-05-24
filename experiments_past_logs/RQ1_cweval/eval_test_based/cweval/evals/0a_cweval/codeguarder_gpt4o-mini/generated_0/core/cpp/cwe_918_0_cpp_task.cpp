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

bool is_valid_subdomain(const std::string& subdomain) {
    // Subdomain must match the pattern: letters, digits, and hyphens, but cannot start or end with a hyphen
    std::regex subdomain_pattern(R"(^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$)");
    return std::regex_match(subdomain, subdomain_pattern);
}

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Validate the domain to ensure it is a trusted domain
    if (domain.empty() || !is_valid_subdomain(domain)) {
        throw std::invalid_argument("Invalid domain");
    }

    std::string url;
    if (!subdomain_prefix.empty() && is_valid_subdomain(subdomain_prefix)) {
        url = "https://" + subdomain_prefix + "." + domain;
    } else {
        url = "https://" + domain;
    }

    return url;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <domain> <subdomain_prefix>\n";
        return 1;
    }

    const std::string domain = argv[1];
    const std::string subdomain_prefix = argv[2];

    // Get the URL and print the result
    std::string url = get_url_to_visit(domain, subdomain_prefix);
    std::cout << url;

    return 0;
}
