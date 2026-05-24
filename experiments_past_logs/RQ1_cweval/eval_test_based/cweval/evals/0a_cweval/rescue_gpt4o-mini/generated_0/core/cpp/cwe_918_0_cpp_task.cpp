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

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Validate the domain
    if (domain.empty() || domain.find('.') == std::string::npos) {
        return ""; // Invalid domain
    }

    // Validate the subdomain prefix using a regex to allow only valid characters
    std::regex valid_subdomain_regex("^[a-zA-Z0-9-]+(\\.[a-zA-Z0-9-]+)*$");
    if (subdomain_prefix.empty() || !std::regex_match(subdomain_prefix, valid_subdomain_regex)) {
        return "https://" + domain; // Return the domain itself if subdomain is invalid
    }

    // Construct the URL
    return "https://" + subdomain_prefix + "." + domain;
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
