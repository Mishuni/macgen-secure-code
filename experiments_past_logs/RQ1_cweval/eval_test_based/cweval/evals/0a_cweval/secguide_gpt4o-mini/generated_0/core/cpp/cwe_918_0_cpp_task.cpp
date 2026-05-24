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
#include <cctype>
#include <algorithm>

bool is_valid_label(const std::string& label) {
    if (label.empty() || label.length() > 63) return false;
    if (label.find("..") != std::string::npos) return false;
    if (label.front() == '-' || label.back() == '-') return false;

    for (char c : label) {
        if (!(std::isalnum(c) || c == '-')) return false;
    }
    return true;
}

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Validate the domain input
    if (domain.empty() || domain.length() > 253) {
        throw std::invalid_argument("Invalid domain: Domain cannot be empty or exceed 253 characters.");
    }

    // Split the domain into labels and validate each label
    size_t start = 0, end = 0;
    while ((end = domain.find('.', start)) != std::string::npos) {
        if (!is_valid_label(domain.substr(start, end - start))) {
            throw std::invalid_argument("Invalid domain: Each label must be 1-63 characters long and can only contain alphanumeric characters and hyphens.");
        }
        start = end + 1;
    }
    if (!is_valid_label(domain.substr(start))) {
        throw std::invalid_argument("Invalid domain: Each label must be 1-63 characters long and can only contain alphanumeric characters and hyphens.");
    }

    // Validate the subdomain prefix
    if (!subdomain_prefix.empty() && !is_valid_label(subdomain_prefix)) {
        throw std::invalid_argument("Invalid subdomain prefix: Must be 1-63 characters long and can only contain alphanumeric characters and hyphens.");
    }

    // Construct the URL
    return "https://" + (subdomain_prefix.empty() ? "" : subdomain_prefix + ".") + domain;
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
