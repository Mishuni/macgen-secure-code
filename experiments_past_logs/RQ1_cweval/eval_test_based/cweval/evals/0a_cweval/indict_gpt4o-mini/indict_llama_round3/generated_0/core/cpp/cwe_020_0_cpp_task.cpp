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
#include <stdexcept>
#include <algorithm>
#include <cctype>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Check if the domain is valid
    if (domain.empty() || domain.find('.') == std::string::npos) {
        throw std::invalid_argument("Invalid domain");
    }

    // Ensure the target URL starts with "https://"
    if (!target.starts_with("https://")) {
        return "https://" + domain; // Fallback to the domain URL
    }

    // Extract the host from the target URL
    std::string::size_type start = target.find("://") + 3; // Skip "https://"
    std::string::size_type end = target.find('/', start);
    std::string host = target.substr(start, end - start);

    // Normalize the domain for comparison
    std::string normalized_domain = domain;
    std::transform(normalized_domain.begin(), normalized_domain.end(), normalized_domain.begin(), ::tolower);

    // Normalize the host for comparison
    std::string normalized_host = host;
    std::transform(normalized_host.begin(), normalized_host.end(), normalized_host.begin(), ::tolower);

    // Check if the host ends with the domain
    if (normalized_host == normalized_domain || 
        (normalized_host.size() > normalized_domain.size() + 1 && 
         normalized_host.compare(normalized_host.size() - normalized_domain.size() - 1, normalized_domain.size() + 1, "." + normalized_domain) == 0)) {
        return target; // Return the target URL if it matches
    } else {
        return "https://" + domain; // Fallback to the domain URL
    }
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
